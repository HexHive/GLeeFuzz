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

import logging
import random
import string
import copy

from . import WebGLArgTypes
from utils.utils import choose_random_one_from_list
from utils.utils import choose_random_float_in_range
from utils.utils import choose_random_int_in_range
from utils.utils import gen_rand_float, gen_ran_float_array, gen_rand_int, gen_rand_int_array
from utils.utils import gen_rand_string, gen_rand_string_array

l = logging.getLogger(__name__)


def is_browser_compound_type(typename):
    if typename.startswith("WebGL"):
        return True

    other_typenames = [ "ImageData", "ImageBitmap",
                       "HTMLImageElement", "HTMLCanvasElement",
                       "OffscreenCanvas", "HTMLVideoElement"]

    return typename in other_typenames

class BaseType(object):

    def __init__(self):
        pass

    def gen_value(self, program, api, arg, **kwargs):

        if 'value' in kwargs and kwargs['value'] != None:
            if 'constraint' in kwargs and kwargs['constraint'] == True:
                return kwargs['value']

        return self._gen_value(program, api, arg, **kwargs)

    def _gen_value(self, program, api, arg, **kwargs):
        '''
        BaseType, doing nothing
        '''
        pass

class GLboolean(BaseType):
    def __init__(self):
        self.name = "GLboolean"

    def _gen_value(self, program, api, arg, **kwargs):
        r = choose_random_float_in_range(0.0, 1.0)

        if r <= 0.5:
            return True

        return False

class GLenum(BaseType):
    def __init__(self):
        self.name = "GLenum"

    def _gen_value(self, program, api, arg, **kwargs):

        if len(arg.constraints) > 0:
            constraints_len = len(arg.constraints)
            r = choose_random_int_in_range(0, constraints_len - 1)

            return arg.constraints[r]

        else:
            l.warning(api.name +  " " + arg.name  + " has no constraints")
            return int(random.random()*0xffffffff)

class GLenumSequence(BaseType):
    def __init__(self):
        self.name = "GLenumSequence"

    def _gen_value(self, program, api, arg, **kwargs):
        assert len(arg.constraints) > 0
        r = random.uniform(0.0, len(arg.constraints))
        r = int(r)
        return random.sample(arg.constraints, r)

class GLfloat(BaseType):
    def __init__(self):
        self.name = "GLfloat"

    def _gen_value(self, program, api, arg, **kwargs):
        return gen_rand_float()

class GLclampf(GLfloat):
    def __init__(self):
        self.name = "GLclampf"

class Float32Array(BaseType):
    def __init__(self):
        self.name = "Float32Array"

    def _gen_value(self, program, api, arg, **kwargs):
        n_elem = int(random.random()*128)

        return gen_ran_float_array(n_elem)

class GLfloatSequence(Float32Array):
    def __init__(self):
        self.name = "GLfloatSequence"

class GLint(BaseType):
    def __init__(self):
        self.name = "GLint"

    def _gen_value(self, program, api, arg, **kwargs):
        if len(arg.constraints) > 0:
            r = random.uniform(0.0, float(len(arg.constraints)))
            r = int(r)
            try:
                v = int(arg.constraints[r])
            except:
                v = arg.constraints[r]

            return v

        return gen_rand_int()

class GLuint(GLint):
    def __init__(self):
        self.name = "GLuint"

class Int32Array(BaseType):
    def __init__(self):
        self.name = "Int32Array"

    def _gen_value(self, program, api, arg, **kwargs):
        n_elem = int(random.random() * 128)

        return gen_rand_int_array(n_elem)

class Uint32Array(Int32Array):
    def __init__(self):
        self.name = "Uint32Array"

class GLintSequence(Int32Array):
    def __init__(self):
        self.name = "GLintSequence"

class GLuintSequence(Int32Array):
    def __init__(self):
        self.name = "GLuintSequence"

class GLint64(BaseType):
    def __init__(self):
        self.name = "GLint64"

    def _gen_value(self, program, api, arg, **kwargs):
        return gen_rand_int(n_bits=64)

class GLuint64(GLint64):
    def __init__(self):
        self.name = "GLuint64"

class GLsizei(GLint):
    def __init__(self):
        self.name = "GLsizei"

class GLsizeiptr(BaseType):
    def __init__(self):
        self.name = "GLsizeiptr"

    def _gen_value(self, program, api, arg, **kwargs):
        return gen_rand_int(n_bits=64)

class GLintptr(BaseType):
    def __init__(self):
        self.name = "GLintptr"

    def _gen_value(self, program, api, arg, **kwargs):
        return gen_rand_int()

class GLbitfield(GLuint):
    def __init__(self):
        self.name = "GLbitfield"

class String(BaseType):
    def __init__(self):
        self.name = "String"

    def _gen_value(self, program, api, arg, **kwargs):
        return gen_rand_string()

class StringSequence(BaseType):
    def __init__(self):
        self.name = "StringSequence"

    def _gen_value(self, program, api, arg, **kwargs):
        return gen_rand_string_array()

# Ref:
# https://www.html5rocks.com/en/tutorials/webgl/typed_arrays/
class ArrayBufferOrNull(BaseType):
    def __init__(self):
        self.name = "ArrayBufferOrNull"

    def _gen_value(self, program, api, arg, **kwargs):
        r = random.random()

        if r <= 0.05:
            return None

        def gen_rand_bytes():
            n_bytes = int(random.random() * 256)
            ret = []
            for i in range(n_bytes):
                ret.append(random.getrandbits(8))
            return ret

        if self.name in program.ctx:
            r = random.random()

            if r <= 0.05:
                ret = gen_rand_bytes()
                program.ctx[self.name] = program.ctx[self.name] + 1
                return ret
            r = int(random.random() * program.ctx[self.name])
            return r
        else:
            ret = gen_rand_bytes()

            program.ctx[self.name] = 1

            return ret

# Ref:
# https://www.javascripture.com/DataView
class ArrayBufferViewOrNull(ArrayBufferOrNull):
    def __init__(self):
        self.name = "ArrayBufferViewOrNull"

# Ref:
# https://stackoverflow.com/questions/60031536/difference-between-imagebitmap-and-imagedata
class ImageData(BaseType):
    def __init__(self):
        self.name = "ImageData"

    def _gen_value(self, program, api, arg, **kwargs):

        r = random.random()

        if self.name not in program.ctx:
            program.ctx[self.name] = 1
            r1 = int(random.random()*128)
            r2 = int(random.random()*128)
            return [r1, r2]
        else:
            if r <= 0.1:
                r1 = int(random.random()*128)
                r2 = int(random.random()*128)
                program.ctx[self.name] = program.ctx[self.name] + 1
                return [r1, r2]
            # refer to an existing one
            r = int(random.random() * program.ctx[self.name])
            return r

# Ref:
# https://developer.mozilla.org/en-US/docs/Web/API/WindowOrWorkerGlobalScope/createImageBitmap
class ImageBitmap(BaseType):
    def __init__(self):
        self.name = "ImageBitmap"

    def _gen_value(self, program, api, arg, **kwargs):
        # https://developer.mozilla.org/en-US/docs/Web/API/WindowOrWorkerGlobalScope/createImageBitmap
        possible_elements = ["HTMLImageElement", "HTMLVideoElement", "HTMLCanvasElement",
                             "OffscreenCanvas", "ImageData"]
        r = int(random.random() * len(possible_elements))
        elem = possible_elements[r]
        t = WebGLArgTypes[elem]()
        v = t.gen_value(program, api, arg)
        return {"ref": elem, "value":v}

class HTMLBaseElement(BaseType):
    def __init__(self):
        self.name = "HTMLBaseElement"

    def _gen_value(self, program, api, arg, **kwargs):
        r = random.random()

        if self.name in program.ctx:
            if r <= 0.1:
                program.ctx[self.name] = program.ctx[self.name] + 1
                return {"html_element_type": self.name}
            else:
                return int(random.random() * program.ctx[self.name])
        else:
            program.ctx[self.name] = 1
            return {"html_element_type": self.name}

class HTMLImageElement(HTMLBaseElement):
    def __init__(self):
        self.name = "HTMLImageElement"

class HTMLCanvasElement(HTMLBaseElement):
    def __init__(self):
        self.name = "HTMLCanvasElement"

class OffscreenCanvas(HTMLBaseElement):
    def __init__(self):
        self.name = "OffscreenCanvas"

class HTMLVideoElement(HTMLBaseElement):
    def __init__(self):
        self.name = "HTMLVideoElement"

class WebGLBaseObject(BaseType):
    '''
    A base class for all following
    Hope that this implementation factors out
    all the individual implementation
    '''
    def __init__(self):
        self.name = "WebGLBaseObject"

    def _get_existing_values(self, program, **kwargs):
        '''
        return a list of existing values (generated by previous API calls)
        or None if none exists of  this type

        this method is intended to be re-implemented by individual APIs
        if necessary.
        '''

        if self.name in program.ctx:
            return program.ctx[self.name]
        return None

    def _gen_a_dep_api_returning_value_for_arg(self, program, arg, **kwargs):
        '''
        This method inserts an API that returns this an object
        of this JS type (at the current end) of the program


        In cases where we want to pass some constraints to the arguments
        of inserted api, we can use a kwarg named `transit`
        '''

        assert len(arg.depends_on) == 1
        dep_name = arg.depends_on[0]
        assert dep_name in program.spec.apis_map
        deps = program.spec.apis_map[dep_name]
        assert len(deps) == 1
        ins_api = deps[0].get_copy()

        if "constraint" in kwargs and kwargs["constraint"] == "transit":
            kwargs = kwargs["value"]
        else:
            kwargs = {}

        return program.gen_args_for_api_and_add_to_program(ins_api, **kwargs)

    def _gen_value(self, program, api, arg, **kwargs):
        '''
        Generate (return) a value for a type of complex WebGL* object

        This is usually done by inserting an API that returns such an object
        in the program and this method will return the index of the inserted
        API.

        In the executor, the return values of each API is recorded,
        when the return value of some API is referred, the executor will
        pass in the return value of the API generated (returned) by this
        method.


        kwargs:
        constraint:  only handles `transit` to handle passed in values to dependent APIs
                     used in _gen_a_dep_api_returning_value_for_arg
        value     :  the value(s) to be passed to the dependent API as arguments

        Ret value: the index of the API call whose return value will be passed
        to this argument of this API

        '''

        existing_values = self._get_existing_values(program, **kwargs)
        if existing_values == None or len(existing_values) == 0:
            return self._gen_a_dep_api_returning_value_for_arg(program, arg, **kwargs)
        else:
            pass

        return choose_random_one_from_list(existing_values)

###################################
# types available in both GL1 and GL2
###################################
class WebGLUniformLocationOrNull(WebGLBaseObject):
    def __init__(self):
        self.name = "WebGLUniformLocation"

class WebGLProgramOrNull(WebGLBaseObject):
    def __init__(self):
        self.name = "WebGLProgram"

class WebGLShaderOrNull(WebGLBaseObject):
    def __init__(self):
        self.name = "WebGLShader"

    def _get_existing_values(self, program, **kwargs):

        if ("constraint" not in kwargs or "value" not in kwargs) or kwargs["constraint"] != "transit":
            if self.name in program.ctx:
                return program.ctx[self.name]
            return None

        d = program.analyzer_states

        if "shader_info" not in d:
            return None

        val_field = kwargs["value"]
        val_passedin = None
        if isinstance(val_field, str):
            val_passedin = val_field
        elif isinstance(val_field, dict):
            val_passedin = val_field["values"][0]

        k_name = None
        if val_passedin == "VERTEX_SHADER":
             k_name = "vertex_shaders"
        elif val_passedin == "FRAGMENT_SHADER":
             k_name = "fragment_shaders"
        assert k_name != None

        if k_name not in d["shader_info"]:
            return None

        return list(d["shader_info"][k_name].keys())

class WebGLTextureOrNull(WebGLBaseObject):
    def __init__(self):
        self.name = "WebGLTexture"

class WebGLBufferOrNull(WebGLBaseObject):
    def __init__(self):
        self.name = "WebGLBuffer"

class WebGLRenderbufferOrNull(WebGLBaseObject):
    def __init__(self):
        self.name = "WebGLRenderbuffer"

class WebGLFramebufferOrNull(WebGLBaseObject):
    def __init__(self):
        self.name = "WebGLFramebuffer"

###################################
# types only available in WebGL2
###################################
class WebGLVertexArrayObjectOrNull(WebGLBaseObject):
    def __init__(self):
        self.name = "WebGLVertexArrayObject"

class WebGLSamplerOrNull(WebGLBaseObject):
    def __init__(self):
        self.name = "WebGLSampler"

class WebGLTransformFeedbackOrNull(WebGLBaseObject):
    def __init__(self):
        self.name = "WebGLTransformFeedback"

class WebGLSyncOrNull(WebGLBaseObject):
    def __init__(self):
        self.name = "WebGLSync"

class WebGLQueryOrNull(WebGLBaseObject):
    def __init__(self):
        self.name = "WebGLQuery"
