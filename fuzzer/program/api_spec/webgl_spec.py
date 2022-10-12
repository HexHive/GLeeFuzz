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

import json

from .api import WebGLAPI, WebGLArg
from .macro import WebGLMacro

class WebGLSpecJSONEncoder(json.JSONEncoder):
    '''
    This encoder is only intended for dumping
    api in json format, not for WebGLProgram.
    WebGLProgram has its own serialization implementation
    '''

    def default(self, obj):
        if isinstance(obj, WebGLSpec):
            return {"version":obj.version,
               "apis": obj.apis,
               "apis_map": obj.apis_map,
               "macros": obj.macros}

        if isinstance(obj, WebGLAPI):
            return {
                "name":obj.name,
                "id": obj.id,
                "args": obj.args,
                "ret_type": obj.ret_type,
            }

        if isinstance(obj, WebGLArg):
            return {
                "name": obj.name,
                "constraints": obj.constraints,
                "depends_on": obj.depends_on,
                "arg_type": obj.arg_type.name
            }

        if isinstance(obj, WebGLMacro):
            return {
                "name": obj.name,
                "value": obj.value
            }

        return json.JSONEncoder.default(self, obj)

class WebGLSpec:

    def __init__(self, version):
        self.version = version
        self.apis = []
        self.apis_map = {}
        self.macros = {}
        self.disabled = []
        self.enabled = []

    def is_enabled(self, api_id):
        if len(self.enabled) > 0 and api_id not in self.enabled:
            return False

        if api_id in self.disabled:
            return False

        return True

    def choose_an_api(self, r=None):
        pass
