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

from ..base_analyzer import BaseAnalyzer

class ShaderBaseAnalyzer(BaseAnalyzer):
    '''
    This is a base class containing some common functions
    '''

    def get_shader_info(self, program):
        shader_info_key = "shader_info"
        return self.get_or_create_element_from_dict(program.analyzer_states, shader_info_key, cls=dict)

    def __get_shader_info_by_type(self, program, info_type):

        shader_info = self.get_shader_info(program)
        return self.get_or_create_element_from_dict(shader_info, info_type);

    def get_programs_info(self, program):

        '''
        State info of shader programs
        '''
        return self.__get_shader_info_by_type(program, "programs");

    def get_vertex_shaders_info(self, program):
        '''
        State info of vertex shaders
        '''
        return self.__get_shader_info_by_type(program, "vertex_shaders")

    def get_fragment_shaders_info(self, program):
        '''
        State info of fragment shaders
        '''
        return self.__get_shader_info_by_type(program, "fragment_shaders")

    def new_program_state(self):
        return {"vertex_shader_attached": False,
           "vertex_shader": None,
           "fragment_shader_attached": False,
           "fragment_shader": None,
           "linked": False,
           "used": False}

    def new_shader_state(self):
        return {'source': False, 'compiled':False}
