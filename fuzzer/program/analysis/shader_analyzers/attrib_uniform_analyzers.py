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

from utils.utils import choose_random_int_in_range
from .shader_base_analyzer import ShaderBaseAnalyzer

import logging
logger = logging.getLogger(__name__)

class AttribUniformNameAnalyzer(ShaderBaseAnalyzer):
    '''
    this analyzer is for the string argument used  in the following apis:

    getAttribLocation
    bindAttribLocation
    getUniformLocation

    '''

    def update_value(self, program, api, v_index):
        if api.name == "getAttribLocation" or api.name == "bindAttribLocation":
            l = len(program.shader_group.attributes)
            if l > 0:
                r  = choose_random_int_in_range(0, l - 1)
                v = program.shader_group.attributes[r]
            else:
                logger.warning("attrbute list empty")
                return
        elif api.name == "getUniformLocation":
            l = len(program.shader_group.uniforms)
            if l > 0:
                r = choose_random_int_in_range(0, l - 1)
                v =  program.shader_group.uniforms[r]
            else:
                logger.warning("uniform list empty")
                return
        else:
            return

        api.set_arg_val(v_index, v)

    def _analyze(self, program, api):

        for i in range(len(api.args)):
            arg = api.args[i]
            if arg.arg_type.name == "String":
                self.update_value(program, api, i)
