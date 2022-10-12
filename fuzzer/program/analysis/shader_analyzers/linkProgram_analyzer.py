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

class LinkProgramAnalyzer(ShaderBaseAnalyzer):

    def _analyze(self, program, api):
        '''
        we need to make sure that
        the program has 2 shaders and
        they are compiled

        void gl.linkProgram(program);
        '''

        program_val = api.get_arg_val(0)

        programs_info = self.get_programs_info(program)

        if program_val not in programs_info:
            logger.warning("program not recorded")
            return

        program_state = programs_info[program_val]

        self.check_shader_attach_and_compiled(program, program_state, program_val, "vertex_shader")
        self.check_shader_attach_and_compiled(program, program_state, program_val, "fragment_shader")

        program_state["linked"] = True

    def check_shader_attach_and_compiled(self, program, program_state, program_val, shader_type):
        '''
        A program state looks like this:

        {
           "vertex_shader_attached": False,
           "vertex_shader": None,
           "fragment_shader_attached": False,
           "fragment_shader": None,
           "linked": False,
           "used": False
        }

        '''

        attached_state_key = shader_type + "_attached"
        shader_key = shader_type

        if not program_state[attached_state_key]:
            program.gen_args_for_api_and_add_to_program_by_name("attachShader",
                                                                values=[program_val,
                                                                            {'constraints': [True],
                                                                             'values':[shader_type.upper()]}],
                                                                constraints=[True, "transit"])


        if not program_state[attached_state_key]:
            import pdb
            pdb.set_trace()

        assert program_state[attached_state_key]
        assert program_state[shader_key] != None

        if shader_type == "vertex_shader":
            shaders_info = self.get_vertex_shaders_info(program)
        else:
            shaders_info = self.get_fragment_shaders_info(program)

        if program_state[shader_key] not in shaders_info:
            logger.error("shader not recorded")
        else:
            shader_state = shaders_info[program_state[shader_key]]

        if not shader_state['compiled']:
            program.gen_args_for_api_and_add_to_program_by_name("compileShader",
                                                                values=[program_state[shader_key]],
                                                                constraints=[True])
        assert shader_state['compiled']
