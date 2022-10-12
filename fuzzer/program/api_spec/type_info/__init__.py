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

import sys, inspect
import os
import logging

logger = logging.getLogger(__name__)

WebGLArgTypes = {}
path = os.path.dirname(os.path.abspath(__file__))

import importlib

def load_arg_types():
    m = importlib.import_module(".type", "program.api_spec.type_info")

    for name, obj in inspect.getmembers(m):
        if inspect.isclass(obj):
            WebGLArgTypes[name] = obj

load_arg_types()

from .type import BaseType
