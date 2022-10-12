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

from .type_info.type import is_browser_compound_type
from ..mutation.mutator_dispatcher import MutateDispatcher

logger = logging.getLogger(__name__)

class WebGLArg:

    def __init__(self, name):
        self.name = name
        self.constraints = []
        self.depends_on = []

        self.arg_type = None


class WebGLAPI:

    def __init__(self, name):
        '''
        These fields are intended to be
        initialized by our initialization code
        '''

        self.name = name
        self.id = None

        self.args = []
        self.ret_type = None
        self.arg_values = []

        self.analyzers = []

        self.__mutate_dispatcher = MutateDispatcher()

    @property
    def mutate_dispatcher(self):
        return self.__mutate_dispatcher

    @mutate_dispatcher.setter
    def mutate_dispatcher(self, md):
        self.__mutate_dispatcher = md

    def add_analyzer(self, analyzer, index = -1):
        if analyzer == None or analyzer in self.analyzers:
            return

        if index == -1:
            self.analyzers.append(analyzer)

        self.analyzers.insert(index, analyzer)

    def create_arg_constraints(self, **kwargs):
        '''
        This method is for generating constraints
        Now the implementation is not correct
        only returning False for non builtin argument types
        and  True for builtin types
        '''

        ret = []
        for arg in self.args:
            if is_browser_compound_type(arg.arg_type.name):
                ret.append(False)
            else:
                ret.append(True)


        return ret

    def mutate(self, program, values, **kwargs):
        '''

        In this method, this api is still not added to the program
        '''
        assert values != None

        self._gen_args(program, values=values,
                      constraints=self.create_arg_constraints())

        log_msg = kwargs.get("log_message")
        if self.__mutate_dispatcher != None and log_msg != None:
            logger.debug("===== log message not None, dispatching mutation")
            if not self.__mutate_dispatcher.dispatch_mutation(program, self, **kwargs):
                logger.warning("after applying mutation, arguments are not mutated")

        self._check_and_apply_analysis(program, **kwargs)

    def gen_args(self, program, **kwargs):
        self._gen_args(program, **kwargs)
        self._check_and_apply_analysis(program, **kwargs)

    def _gen_args(self, program, **kwargs):

        '''
        Generate the argument values for this API, with
        a lot of options for customization the
        argument generation
        ================================================

        :param program: the program this API is going to be added to
        :type program: WebGLProgram

        kwargs include:
        :values list or single element: if there is only one argument
                                       in this API, we can provide a single  element
        :constraints list or single element: same as above
        :skip_analyzers bool: whether analyzers will be run or not, default: False

        :return: no value
        :rtype: None

        '''

        o_arg_values = kwargs.get("values")
        constraints = kwargs.get("constraints")

        if o_arg_values != None and not isinstance(o_arg_values, list):
            o_arg_values = [o_arg_values]
        if constraints != None and not isinstance(constraints, list):
            constraints = [constraints]

        assert o_arg_values == None or isinstance(o_arg_values, list)
        assert constraints == None or isinstance(constraints, list)

        for i in range(len(self.args)):
            arg = self.args[i]
            o_v = None
            if o_arg_values != None and i < len(o_arg_values):
                o_v = o_arg_values[i]

            cnt = None
            if constraints != None and i < len(constraints):
                cnt = constraints[i]

            if o_v == None and cnt != None:
                logger.warning("constraint is not set but arg value is not")

            if o_v == None:
                v =  arg.arg_type.gen_value(program, self, arg)
            else:
                v =  arg.arg_type.gen_value(program, self, arg, value=o_v, constraint=cnt)
            self.arg_values.append(v)

    def _check_and_apply_analysis(self, program, **kwargs):
        skip_analyzers = kwargs.get("skip_analyzers")
        if not skip_analyzers:
            self.analyze(program)

    def mutate_args(self, program, **kwargs):
        pass

    def get_arg_val(self, arg_index, **kwargs):
        if arg_index < 0 or arg_index >= len(self.arg_values):
            arg_name = kwargs.get("arg_name")
            if arg_name == None:
                return None

            i = 0
            for arg in self.args:
                if arg.name == arg_name:
                    return self.arg_values[i]
                i = i + 1

            return None
        else:
            return self.arg_values[arg_index]

    def set_arg_val(self, arg_index, val):
        if arg_index < 0 or arg_index >= len(self.arg_values):
            logger.error("index out of bounds of arg_values")
            return

        self.arg_values[arg_index] = val

    def get_copy(self):
        '''
        Get a fresh copy of the API

        The generated values are not saved
        '''
        c = WebGLAPI(self.name)
        c.id = self.id

        c.args = self.args
        c.ret_type = self.ret_type
        c.analyzers = self.analyzers
        c.arg_values = []
        c.mutate_dispatcher = self.__mutate_dispatcher

        return c

    def analyze(self, program, **kwargs):
        for analyzer in self.analyzers:
            analyzer.analyze(program, self, **kwargs)

    def post_analyze(self, program, **kwargs):
        for analyzer in self.analyzers:
            analyzer.post_analyze(program, self, **kwargs)
