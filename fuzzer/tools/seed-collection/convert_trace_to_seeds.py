#!/usr/bin/env python3
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
logging.basicConfig(level=logging.CRITICAL)

from inspect import getargvalues
import os, sys
from program.api_spec.api import WebGLAPI, WebGLArg
import json
import pickle
import argparse
import re

from typing import List

from utils.utils import choose_random_one_from_list
from program import WebGLProgram
from program.api_spec import WebGLSpecs
from program.api_spec import get_apis_by_name

def __match_cmd_arg_with_spec(cmd_arg, api_arg:WebGLArg) -> bool:
    '''
    Handling all the quirks from spectorjs
    output for arguments
    '''

    if type(cmd_arg) == str:
        if cmd_arg.startswith("Array Length"):
            # ok, this should be an ArrayBuffer?, Or
            # ArrayBufferView?
            # TODO: Invistigate
            if api_arg.arg_type.name.startswith("Array"):
                return True

        # if api_arg.arg_type.name != "String":
        #     return False
        return api_arg.arg_type.name == "String"

    if type(cmd_arg) == bool:
        return api_arg.arg_type.name == "GLboolean"

    if type(cmd_arg) == list:
        return api_arg.arg_type.name.endswith("Sequence")

    # https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/Types
    int_typenames = ["GLint", "GLuint", "GLsizei",
                     "GLsizeiptr", "GLintptr",
                     "GLenum",
                     "GLbitfield", "GLbyte",
                     "GLshort", "GLubyte",
                     "GLushort", "GLint64"]
    float_typenames = ["GLfloat", "GLclampf"]

    if type(cmd_arg) == int:
        # integers can also be converted to float
        return api_arg.arg_type.name in int_typenames or \
            api_arg.arg_type.name in float_typenames

    if type(cmd_arg) == float:
        return api_arg.arg_type.name in float_typenames

    # compound data types
    if type(cmd_arg) == dict:
        if "__SPECTOR_Object_TAG" not in cmd_arg:
            for i in range(len(cmd_arg)):
                if str(i) not in cmd_arg:
                    return False
            return api_arg.arg_type.name.startswith("Array")
        else:
            cmd_arg_type_name = cmd_arg["__SPECTOR_Object_TAG"]["typeName"]
            return api_arg.arg_type.name.startswith(cmd_arg_type_name)

    if cmd_arg is None:
        return True

    return False

def choose_api_from_spectorjs_cmd(apis:List[WebGLAPI], cmd:dict) -> WebGLAPI:
    cmd_args = cmd["commandArguments"]
    cmd_nr_args = len(cmd_args)
    apis_filtered_by_args = []
    apis_filtered_by_nr_args = []
    for api in apis:
        matched = True
        if api.name.startswith("uniform") and api.name.endswith("v"):
            pass
        elif len(api.args) == cmd_nr_args:
            apis_filtered_by_nr_args.append(api)
            for i in range(len(api.args)):
                cmd_arg = cmd_args[i]
                api_arg = api.args[i]
                if not __match_cmd_arg_with_spec(cmd_arg, api_arg):
                    matched = False
                    break

        if matched:
            apis_filtered_by_args.append(api)

    if len(apis_filtered_by_args) == 0:
        print("WARNING, No APIs identified")
        print("CMD:")
        print(cmd)
        return choose_random_one_from_list(apis_filtered_by_nr_args)

    elif len(apis_filtered_by_args) > 1:
        print("WARNING, there are multipe APIs identified, name:"
              + str(api.name))
        print("CMD:")
        print(cmd)
        for api in apis_filtered_by_args:
            print("\t id:{id}, name:{name}".format(id=api.id, name=api.name))

    return apis_filtered_by_args[0]

def __build_arguments_from_cmd(api:WebGLAPI, cmd):
    api.arg_values.clear()

    cmd_args = cmd["commandArguments"]
    for cmd_arg in cmd_args:
        if cmd_arg is None:
            api.arg_values.append(cmd_arg)
        elif type(cmd_arg) == int or type(cmd_arg) == float:
            api.arg_values.append(cmd_arg)

        elif type(cmd_arg) == list:
            api.arg_values.append(cmd_arg)

        elif type(cmd_arg) == str:
            if cmd_arg.startswith("Array Length"):
                m = re.search("Array Length:(.*)", cmd_arg)
                if m == None:
                    assert(False, "re search error")

                ll = int(m.group(1).strip())

                if api.name == "shaderSource":
                    v = cmd["text"][-1 * ll:]
                    api.arg_values.append(v)
                else:
                    assert(False, "Unhandled type")
            pass
        elif type(cmd_arg) == dict:
            if "__SPECTOR_Object_TAG" not in cmd_arg:
                is_array = True
                for i in range(len(cmd_arg)):
                    if str(i) not in cmd_arg:
                        is_array = False
                        break

                if is_array:
                    v = []
                    for i in range(len(cmd_arg)):
                        v.append(cmd_arg[str(i)])
                    api.arg_values.append(v)
                else:
                    assert False, "Unhandled types"
            else:
                obj_id = cmd_arg["__SPECTOR_Object_TAG"]['id']
                api.arg_values.append(obj_id)

def build_progam_from_trace_file(trace_file:str,
                                 limit:int) ->WebGLProgram:
    with open(trace_file) as inf:
        trace_json = json.load(inf)

    version = trace_json["context"]["version"]
    p = WebGLProgram(version)

    cnt:int = 0
    for c in trace_json["commands"]:
        api_name = c["name"]
        apis_for_name = get_apis_by_name(WebGLSpecs[version],
                                         api_name)

        print("=== cmd-name:" + str(api_name))

        if apis_for_name == None or len(apis_for_name) == 0:
            api_spec = get_apis_by_name(WebGLSpecs[version],"getError")[0]
        else:
            api_spec = choose_api_from_spectorjs_cmd(apis_for_name, c)
            print("=== api-spec: name={name}, id={id}".format(name=api_spec.name,
                                                              id=api_spec.id))

        api = api_spec.get_copy()
        __build_arguments_from_cmd(api, c)
        p.add_api(api, skip_analyzers=True)

        cnt += 1
        if cnt >= limit:
            break

    return p

def convert_trace_file_and_save_pickle(trace_file:str,
                                       pickle_file:str,
                                       limit:int):

    program = build_progam_from_trace_file(trace_file, limit)
    with open(pickle_file, "wb") as outf:
        pickle.dump(program, outf)


def contert_trace_dir_and_save_pickle(trace_dir:str,
                                      output_dir:str,
                                      prefix:str,
                                      limit:int):
    idx = 0
    for root, dirs, files in os.walk(trace_dir):
        for f in files:
            if f.endswith(".json"):
                pickle_file_name = os.path.join(output_dir,
                                                prefix + str(idx) + ".pickle")
                idx = idx + 1
                convert_trace_file_and_save_pickle(os.path.join(root, f),
                                                   pickle_file_name,
                                                   limit)

def main():
    parser = argparse.ArgumentParser(prog="convert_trace_to_seeds",
                                     description="A tool for converting " +
                                     "spectorjs traces to WebGLFuzzer seeds")
    parser.add_argument("--trace_file", type=str, required=False,
                        help="The spectorjs trace file (in json format)")
    parser.add_argument("--trace_file_dir", type=str, required=False,
                        help="The dirctory containing trace files (in json format)")
    parser.add_argument("--api_limit", type=int, default=30,
                        help="the max number of APIs to take from the trace")
    parser.add_argument("--output", type=str, required=False, default="save.pickle",
                        help="The output file to save the " + \
                        "program (pickle format)")
    parser.add_argument("--output_dir", type=str, required=False,
                        help="The output file to save the " + \
                        "program (pickle format)")
    parser.add_argument("--prefix", type=str, required=False, default="seed-",
                        help="The prefix of the saved files")

    args = parser.parse_args()

    if args.trace_file is not None and os.path.exists(args.trace_file):
        convert_trace_file_and_save_pickle(args.trace_file,
                                      args.output,
                                      args.api_limit)

    if args.trace_file_dir is not None and os.path.exists(args.trace_file_dir):
        if not os.path.exists(args.output_dir):
            os.makedirs(args.output_dir)

        contert_trace_dir_and_save_pickle(args.trace_file_dir,
                                          args.output_dir,
                                          args.prefix,
                                          args.api_limit)


if __name__ == '__main__':
    main()
