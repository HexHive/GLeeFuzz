# ******************************************************
# * Copyright (C) 2022 the GLeeFuzz authors.
# * This file is part of GLeeFuzz.
# *
# * GLeeFuzz is free software: you can redistribute it
# * and/or modify it under the terms of the GNU General 
# * Public License as published by the Free Software 
# * Foundation, either version 3 of the License, or 
# * (at your option) any later version.
# *
# * GLeeFuzz is distributed in the hope that it will 
# * be useful, but WITHOUT ANY WARRANTY; without even
# * the implied warranty of MERCHANTABILITY or FITNESS
# * FOR A PARTICULAR PURPOSE. See the GNU General 
# * Public License for more details.
# *
# * You should have received a copy of the GNU 
# * General Public License along with GLeeFuzz. If not,
# * see <https://www.gnu.org/licenses/>.
# ******************************************************

import logging
import copy
import json
from enum import Enum

logger = logging.getLogger(__name__)

from .api_spec import WebGLSpecs, WebGLAPI
from . import config
from .shader import shader_groups
from utils.utils import choose_random_one_from_list
from utils.utils import choose_random_int_in_range

from executor.exec_log import ChromeExecutionLog

# this is the json encoder class for
# serializing the program object to json
# and send it to browser side for execution
class WebGLProgramJSONEncoder(json.JSONEncoder):
    '''
    JSON is used for communication with
    browser,

    internally, the fuzzer uses pickle for
    serialization/deserialization
    '''

    def default(self, obj):
        if isinstance(obj, WebGLProgram):
            return {"apis":obj.apis, "ctx":obj.ctx,
               "spec":obj.spec.version, "test_flag": obj.test_flag}

        # here we do not save the args etc, only the values
        if isinstance(obj, WebGLAPI):
            return {"name":obj.name,
                    "id": obj.id,
                    "arg_values": obj.arg_values}

        return json.JSONEncoder.default(self, obj)

class ArgGenConstraint(Enum):
    KEEP = 1
    GEN = 2
    TRANSIT = 3

class WebGLProgram:

    def __init__(self, version:int, **kwargs):
        self.apis = []
        self.log_msgs = []
        self.ctx = {}
        assert version in [1, 2]
        self.spec = WebGLSpecs[version]
        self.version = version

        self.shader_group = None
        self.load_a_shader_group(version)

        self.analyzer_states = {}

        self.test_flag = 0

    def load_a_shader_group(self, version:int):
        n = len(shader_groups[version])
        r = choose_random_int_in_range(0, n - 1)
        self.shader_group = shader_groups[version][r]


    def get_copy(self):
        '''
        Get a fresh copy of the program

        with data generated removed except shader_group
        '''

        c = WebGLProgram(self.version)
        c.shader_group = self.shader_group

        return c

    @staticmethod
    def generate(version:int):
        '''
        return a randomly generated webgl program
        '''

        ret = WebGLProgram(version)

        api_list = ret.spec.apis
        n_apis = len(api_list)
        i = 0
        while i < config.NR_APIS:
            # choose a random one API
            r = choose_random_int_in_range(0, n_apis-1)
            o_api = api_list[r]

            # check whether the API is enabled or not
            if not ret.spec.is_enabled(o_api.id):
                continue

            api = o_api.get_copy()
            ret.gen_args_for_api_and_add_to_program(api)
            i = i + 1

        return ret


    def add_api(self, api:WebGLAPI, skip_analyzers=False):
        '''
        simply appending the `api` to the list of `apis`
        '''

        self.apis.append(api)
        self.__post_analyze(api,
                            len(self.apis) - 1,
                            skip_analyzers=skip_analyzers)


    def __post_analyze(self, api:WebGLAPI, pos:int,
                       skip_analyzers:bool=False):

        if api.ret_type.startswith("WebGL"):
            if api.ret_type in self.ctx:
                self.ctx[api.ret_type].append(pos)
            else:
                self.ctx[api.ret_type] = [pos]

        if not skip_analyzers:
            api.post_analyze(self, pos=pos)

    def gen_args_for_api_and_add_to_program(self, api:WebGLAPI, mutation=False, **kwargs):
        '''
        kwargs:

        values: passed in values, used for cases we want to use some specific arg values
        constraints: the constraints on how to generate the arguments
        mutation: bool, whether to perform mutation following runtime log message
        '''

        if not mutation:
            api.gen_args(self, **kwargs)
        else:
            api.mutate(self, **kwargs)

        # after generating the values, we append it to the list
        self.apis.append(api)
        pos = len(self.apis) - 1

        # do a post generating analysis
        # to save the return value in the ctx
        # and some analysis needs the position of the api
        # in the `apis` list, this step will call the per-api
        # post analysis code
        self.__post_analyze(api, pos)
        return pos

    def gen_args_for_api_and_add_to_program_by_name(self, api_name:str, **kwargs):
        '''
        Get an API by name, and generate argument values

        If there are multiple apis with the same name, we randomly choose one

        kwargs:

        values: a list of preset argument values
        constraints: a list of constraints for the argument, possible constraint values
                True: the generator/mutator need to keep the value in the same position in `values`
                False: the generator/mutator can generate a value as they like

        '''

        if api_name not in self.spec.apis_map:
            logger.error("api name (%s) not defined  in spec", api_name)
            return

        apis = self.spec.apis_map[api_name]
        api = choose_random_one_from_list(apis)
        new_api = api.get_copy()
        self.gen_args_for_api_and_add_to_program(new_api, **kwargs)

    def remove_api(self, at):
        if at < 0 or at >= len(self.apis):
            logger.warning("index(at) %d out of bound", at)
            return

        self.apis.pop(at)
        return

    def analyze(self):
        pass

    def to_json(self, **kwargs):
        return json.dumps(self, cls=WebGLProgramJSONEncoder, **kwargs)

    def _reset_states(self):
        '''
        reset all fields used in generating programs/analyzing apis
        specifically, resetting the following fields
        '''

        self.ctx = {}
        self.analyzer_states = {}

    def mutate(self, **kwargs):
        '''
        `Mutating`  a WebGLProgram (`self`) for purposes including:
        1. runtime message (feedback) guided mutation
        2. random mutation
        3. coverage guided mutation(?)

        In implementation,
        '''
        return self._runtime_log_guided_mutate(**kwargs)


    def _runtime_log_guided_mutate(self, **kwargs):
        # step 1: reset all the states info
        # that the generator and program analyzers saved.
        # because this will change
        # self._reset_states()

        ret = self.get_copy()

        # step 2: mutating the values of arguments

        # here iterating through the apis like this may be an issue
        # as we may change apis, i.e., adding, removing etc
        # we save the old list and generate the new apis in a new list
        assert len(self.apis) > 0
        for i in range(len(self.apis)):
            api = self.apis[i]
            new_api = api.get_copy()

            log_msg = None
            if self.log_msgs != None and i < len(self.log_msgs) and \
               self.log_msgs[i] != None and len(self.log_msgs[i]) > 0:
                log_msg = ChromeExecutionLog(self.log_msgs[i])

            if kwargs == None:
                kwargs = {}
            kwargs["log_message"] = log_msg

            logger.debug("===== before mutation: apiname:%s, arg_values: %s, message: %s", api.name, str(api.arg_values), str(log_msg) if log_msg != None else "None")
            ret.gen_args_for_api_and_add_to_program(new_api,
                                                    mutation=True,
                                                    values=api.arg_values,
                                                    **kwargs)

            logger.debug("===== after mutation, apiname: %s, arg_values:%s", new_api.name, str(new_api.arg_values))

        return ret

    def save_log_messages(self, r):
        self.log_msgs = []

        if r == None:
            return

        if not isinstance(r, list):
            return

        for i in range(len(r)):
            if "msg" in r[i]:
                self.log_msgs.append(r[i]["msg"])
            else:
                self.log_msgs.append("")

    def __str__(self):
        return json.dumps(self, indent=4, cls=WebGLProgramJSONEncoder)
