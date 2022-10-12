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

class CompileShaderAnalyzer(ShaderBaseAnalyzer):

    def _analyze(self, program, api):
        '''
        we need to make sure that the source has been setup
        before we can compile it
        '''

        shader_val = api.get_arg_val(0)

        vertex_shaders_info = self.get_vertex_shaders_info(program)
        if shader_val in vertex_shaders_info:

            if not vertex_shaders_info[shader_val]["source"]:
                program.gen_args_for_api_and_add_to_program_by_name("shaderSource",
                                                                    values=[shader_val],
                                                                    constraints=[True])
            assert vertex_shaders_info[shader_val]["source"]
            vertex_shaders_info[shader_val]['compiled'] = True
        else:
            fragment_shaders_info = self.get_fragment_shaders_info(program)
            if shader_val in fragment_shaders_info:

                if not fragment_shaders_info[shader_val]["source"]:
                    program.gen_args_for_api_and_add_to_program_by_name("shaderSource",
                                                                        values=[shader_val],
                                                                        constraints=[True])

                assert fragment_shaders_info[shader_val]["source"]
                fragment_shaders_info[shader_val]['compiled'] = True
            else:
                logger.error("the shader object is not recorded")
