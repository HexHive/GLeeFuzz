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

class ShaderSourceAnalyzer(ShaderBaseAnalyzer):

    def _analyze(self, program, api):
        shader_val = api.get_arg_val(0)

        if shader_val == None:
            return


        vertex_shaders_info = self.get_vertex_shaders_info(program)
        fragment_shaders_info = self.get_fragment_shaders_info(program)
        if shader_val in vertex_shaders_info:
            src = program.shader_group.vshader.src
            api.set_arg_val(1, src)
            vertex_shaders_info[shader_val]['source'] = True
        if shader_val in fragment_shaders_info:
            src = program.shader_group.fshader.src
            api.set_arg_val(1, src)
            fragment_shaders_info[shader_val]['source'] = True
