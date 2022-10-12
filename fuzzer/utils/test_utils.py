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

import os
import time
import pickle
from selenium import webdriver
from program import WebGLProgram
from program.api_spec import get_apis_by_name

def get_first_api_with_name(name, spec):
    apis = spec.apis_map[name]

    return apis[0].get_copy()

def create_program_from_api_list(api_names, version):
    program = WebGLProgram(version)

    for api_name in api_names:
        api = get_first_api_with_name(api_name, program.spec)
        program.gen_args_for_api_and_add_to_program(api)

    return program

def prepare_program_save_dir(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)

def make_program_filename(program, seq):
    return str(seq) + "-" + str(program.spec.version) + "-" + str(time.time())

def get_test_filename(filename):
    bname = os.path.basename(filename)
    splits = os.path.splitext(bname)

    return splits[0]

def save_program(program, seq, dirname):
    filename = make_program_filename(program, seq)
    with open(os.path.join(dirname, filename + ".pickle"), "wb") as of:
        pickle.dump(program, of)

    with open(os.path.join(dirname, filename + ".json"), "w") as of:
        of.write(program.to_json())
