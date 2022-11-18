#!/usr/bin/env python


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


import sys, os
import argparse
import json
import pickle

import program
from program.api_spec import WebGLSpec
from program.api_spec import WebGLMacro
from program.api_spec import WebGLArg
from program.api_spec import WebGLAPI

from program.api_spec.type_info import WebGLArgTypes

import json

from program.api_spec import WebGLSpecJSONEncoder

def main():
    parser = argparse.ArgumentParser(prog="import_webgl_api_spec",
                                     description="A tool for importing a webgl api spec")

    parser.add_argument("--glspec", required=True, help="the path to the webgl spec file")
    parser.add_argument("--output", required=True, help="where to write the serialized spec object")
    parser.add_argument("--json", required=False, help="where to write the json serialized spec object")
    args = parser.parse_args()

    json_spec_file = args.glspec
    output = args.output
    spec = gen_spec_obj(json_spec_file)

    with open(output, "wb") as of:
        pickle.dump(spec, of)

    if args.json != None:
        with open(args.json, "w") as of:
            json.dump(spec, of, cls=WebGLSpecJSONEncoder, indent=4)

def gen_spec_obj(json_spec_file):
    with open(json_spec_file) as json_f:
        spec_data = json.load(json_f)

        spec = None
        if spec_data["name"] == "WebGLRenderingContext":
            spec = WebGLSpec(1)
        else:
            spec = WebGLSpec(2)

        # setting up macros
        for m_name in spec_data["macros"]:
            m = spec_data["macros"][m_name]
            macro = WebGLMacro(m_name, int(m["value"], base=16))
            spec.macros[m_name] = macro

        # setting up apis
        a_id = 0
        # TODO: singleton
        for api_name in spec_data["apis"].keys():
            apis = spec_data["apis"][api_name]

            for a_api in apis:
                api = WebGLAPI(api_name)
                ### set up the id
                api.id = a_id
                a_id = a_id + 1

                ret_type = a_api["ret_type"]["name"]

                if ret_type.endswith("OrNull"):
                    ret_type = ret_type.replace("OrNull", "")
                api.ret_type = ret_type

                args = a_api["args"]
                for a_arg in args:
                    t = a_arg["type"]["name"]

                    if (t.startswith("WebGL")  or t == "ArrayBufferView" or t == "ArrayBuffer")  \
                       and not t.endswith("OrNull"):
                        t = t + "OrNull"
                    if t not in WebGLArgTypes:
                        print(t +  " is not defined")
                        sys.exit(-1)

                    arg = WebGLArg(a_arg["name"])

                    # create a type object
                    # here we can share some WebGLArgType object
                    # TODO: improve it
                    arg.arg_type = WebGLArgTypes[t]()

                    # accumulate constraints information
                    constraints = a_arg["constraints"]
                    if constraints != None:
                        m_names = constraints["valid"]

                        for m_name in m_names:
                            if m_name.startswith("GL_"):
                                m_name = m_name[3:]
                            if m_name not in spec.macros:
                                print("[warning]:" +  m_name + " is not a defined macroname")

                            arg.constraints.append(m_name)

                        # here we assume that valid_es3 should be added
                        # to constraints for webgl2
                        # TODO: confirm that this is correct
                        if spec.version == 2:
                            m_names = constraints["valid_es3"]
                            for m_name in m_names:
                                if m_name.startswith("GL_"):
                                    m_name = m_name[3:]
                                if m_name not in spec.macros:
                                    print("[warning]:" +  m_name + " is not a defined macroname")

                                arg.constraints.append(m_name)

                    elif t != "GLboolean" and t != "GLint" and t != "GLuint" and t != "String" and t != "GLintptr" and t != "GLuintptr"  and t != "GLenum":
                        depends_on = a_arg["depends_on"]

                        if depends_on != None:
                            for d in depends_on:
                                arg.depends_on.append(d)

                    # add the arg to the api
                    api.args.append(arg)
                # end for a_arg ...

                # add the api to spec
                spec.apis.append(api)
                assert spec.apis[api.id] == api

                if api_name not in spec.apis_map:
                    spec.apis_map[api_name] = [api]
                else:
                    spec.apis_map[api_name].append(api)


        return spec

if __name__ == '__main__':
    main()
