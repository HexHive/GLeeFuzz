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

import sys,os
import json
import argparse

def main():
    parser = argparse.ArgumentParser(prog="get_all_api_names",
                                     description="A tool to get all the apinames")
    parser.add_argument("--spec_file", type=str, required=True,
                        help="the path to the weblgl spec json file")
    parser.add_argument("--out_file", type=str, required=True,
                        help="the file to write the result to")
    args = parser.parse_args()

    with open(args.spec_file) as jsonf:
        spec_json_obj = json.load(jsonf)

        with open(args.out_file, "w") as out_f:
            for api_name in spec_json_obj["apis_map"].keys():
                out_f.write(api_name + "\n")

if __name__ == '__main__':
    main()
