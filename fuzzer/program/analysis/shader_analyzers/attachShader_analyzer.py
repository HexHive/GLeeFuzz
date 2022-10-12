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

from .shader_base_analyzer import ShaderBaseAnalyzer

import logging
logger = logging.getLogger(__name__)

class AttachShaderAnalyzer(ShaderBaseAnalyzer):

    '''
    void gl.attachShader(program, shader);

    update the 'vertex_shader_attached' or 'fragment_shader_attached'
    field in program state
    '''

    def _analyze(self, program, api):
        program_val = api.get_arg_val(0)

        programs_info = self.get_programs_info(program)

        if program_val not in programs_info:
            logger.warning("program not created yet:")
            return

        program_state = programs_info[program_val]

        shader_val = api.get_arg_val(1)

        if shader_val in self.get_vertex_shaders_info(program):

            program_state['vertex_shader_attached'] = True
            program_state['vertex_shader'] = shader_val
        elif shader_val in self.get_fragment_shaders_info(program):
            program_state['fragment_shader_attached'] = True
            program_state['fragment_shader'] = shader_val
        else:
            logger.warning("shader value not recorded: ")
