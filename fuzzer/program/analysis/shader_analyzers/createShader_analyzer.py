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

class CreateShaderAnalyzer(ShaderBaseAnalyzer):
    '''
    Analyzer for createShader api
    '''

    def __init__(self):
        pass

    def _analyze(self, program, api):

        vertex_shaders_info = self.get_vertex_shaders_info(program)
        fragment_shaders_info = self.get_fragment_shaders_info(program)

        if len(vertex_shaders_info) == 0:
            api.set_arg_val(0, "VERTEX_SHADER")
            return

        if len(fragment_shaders_info) == 0:
            api.set_arg_val(0, "FRAGMENT_SHADER")
            return


    def _post_analyze(self, program, api, **kwargs):

        if "pos" not in kwargs:
            return
        pos = kwargs["pos"]
        if api.arg_values[0] == "VERTEX_SHADER":
            shaders_info = self.get_vertex_shaders_info(program)
        else: 
            shaders_info = self.get_fragment_shaders_info(program)

        if pos in shaders_info:
            return

        shaders_info[pos] = self.new_shader_state()
