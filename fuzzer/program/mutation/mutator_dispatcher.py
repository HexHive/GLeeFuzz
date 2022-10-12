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
logger = logging.getLogger(__name__)
import utils
import re
import os
import json

path = os.path.dirname(os.path.abspath(__file__))
__log_analysis_files = {1: "__log_analysis_v1.json",
                       2: "__log_analysis_v2.json"}
__log_analysis_res = {}
def __setup_mutators():
    for v, log_anal_file in __log_analysis_files.items():
        log_file = os.path.join(path, log_anal_file)
        with open(log_file) as inf:
            anal_res_list = json.load(inf)
            __log_analysis_res[v] = anal_res_list
            logger.debug(f"version: {v}, log_file: {log_file} loaded")

def get_log_analysis_res():
    if len(__log_analysis_res) == 0 and "EXCLUDE_LOG_GUIDED_MUTATORS" not in os.environ:
        __setup_mutators()

    return __log_analysis_res


__global_match_mutate_list = []

def add_mutator_to_global_list(match_func, mutate_cls):
    tpl = (match_func, mutate_cls())
    __global_match_mutate_list.append(tpl)


def get_global_match_mutate_list():
    return __global_match_mutate_list


__api_dep_info = {}


def setup_apidep_info(version, depinfo):
    __api_dep_info[version] = depinfo


def get_apidep_info(version):
    if version in __api_dep_info:
        return __api_dep_info[version]
    return None


class MutateDispatcher(object):
    def __init__(self):
        '''
        This is intended to be a list of tuples
        (m_function, mutate)
        '''
        self.match_mutate_list = []

    def __dispatch_mutator_in_list(self, match_mutate_list, list_name, program,
                                   api, **kwargs):
        if 'log_message' not in kwargs:
            logger.debug("No log message was passed in")
            return False, False

        for m_m in match_mutate_list:
            match_func = m_m[0]
            mutator = m_m[1]

            if match_func(program, api, **kwargs):
                logger.debug(
                    "a mutator matched mutator:%s in list:%s, api_name:%s",
                    mutator.name, list_name, api.name)
                return True, mutator.mutate(program, api, **kwargs)

        return False, False

    def __dispatch_dep_mutation(self, program, api, **kwargs):
        if 'log_message' not in kwargs:
            logger.debug("No log message was passed in")
            return False, False

        msg = kwargs["log_message"].message
        version = program.version
        depinfo = get_apidep_info(version)
        if depinfo is None or api.id not in depinfo or \
           msg not in depinfo[api.id] or \
           len(depinfo[api.id][msg]) <= 0:
            logger.debug("No dep info found: api.name=%s, api.id=%d, msg=%s",
                         api.name, api.id, msg)
            return False, False

        all_deps = depinfo[api.id][msg]

        dep_api_id = utils.utils.choose_random_one_from_list(list(all_deps))
        dep_api = program.spec.apis[dep_api_id]
        api_copy = dep_api.get_copy()
        program.gen_args_for_api_and_add_to_program(api_copy)

        return True, True

    def log_guided_mutation(self, program, api, **kwargs):

        if 'log_message' not in kwargs:
            logger.debug("No log message was passed in")
            return False

        version = program.version
        msg = kwargs["log_message"].message

        if msg is None:
            logger.debug("msg field is None?")
            return False

        log_analysis_res = get_log_analysis_res()
        log_analysis_res_v = log_analysis_res[version]

        if api.id >= len(log_analysis_res_v):
            logger.debug("api id too big?")
            return False

        log_mutate_rules = log_analysis_res_v[api.id]["logs"]
        mutated = False

        for r in log_mutate_rules:
            if "exact" not in r:
                logger.warning("`exact` not in rule?")
                exact = False
            else:
                exact = r["exact"]

            if exact:
                if msg != r["log"]:
                    logger.debug("message does not match")
                    continue

            match = "regex"

            if "match" in r:
                match = r["match"]

            if match == "prefix":
                if not msg.startswith(r["log"]):
                    logger.debug("message does not match")
                    continue
            else:
                p = re.compile(r["log"])
                if not p.match(msg):
                    logger.debug("message does not match")
                    continue


            dep_list = r["deps"]
            dep = utils.utils.choose_random_one_from_list(dep_list)

            if "type" not in dep or "index" not in dep:
                logger.debug("`type` or `index` not included in dep")
                continue

            if  dep["type"] != "arg" and dep["type"] != "api":
                logger.debug("dep type neither arg nor api")
                continue

            if dep["type"] == "arg":
                arg_idx = dep["index"]

                if arg_idx >= len(api.args):
                    logger.warning("dep index >= len(api.args)")
                    continue

                the_arg = api.args[arg_idx]
                api.arg_values[arg_idx] = the_arg.arg_type.gen_value(program, api, the_arg)
            else:
                api_idx = dep["index"]
                if api_idx >= len(program.spec.apis):
                    logger.warning("dep index >= len(apis)")
                    continue
                dep_api = program.spec.apis[api_idx]
                api_copy = dep_api.get_copy()
                program.gen_args_for_api_and_add_to_program(api_copy)

            mutated = True
            break

        return mutated

    def dispatch_mutation(self, program, api, **kwargs):
        '''
        This method dispatches a mutation algorithm according to
        its arguments

        For now, we only consider a log message (retrieved from Chrome)
        '''
        return self.log_guided_mutation(program, api, **kwargs)
