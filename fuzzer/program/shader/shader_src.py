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

from typing import List

class ShaderSrc:
    VERTER_SHADER = 1
    FRAGMENT_SHADER = 2

    def __init__(self, type:int,
                 src:str,
                 version:int):
        self.type = type
        self.src = src
        self.version = version

class ShaderGroup:

    def __init__(self, vshader:ShaderSrc,
                 fshader:ShaderSrc):
        self.vshader = vshader
        self.fshader = fshader
        self.attributes:List[str] = []
        self.uniforms:List[str] = []

    def get_attributes(self):
        return self.attributes

    def get_uniforms(self):
        return self.uniforms
