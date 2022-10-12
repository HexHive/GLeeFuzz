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

#!/usr/bin/env python

import sys, os
import argparse
import json


def main():
    parser = argparse.ArgumentParser(prog="import_webgl_api_spec",
                                     description="A tool for importing a webgl api spec")
    parser.add_argument("--glspec", required=True, help="the path to the webgl spec file")

    args = parser.parse_args()
    json_spec_file = args.glspec

    with open(json_spec_file) as inf:
        spec_data = json.load(inf)

        for api_name in spec_data["apis"].keys():

            apis = spec_data["apis"][api_name]

            for a_api in apis:

                for arg in a_api["args"]:
                    if arg["type"]["name"] == "GLenum" and arg["constraints"] == None:
                        print(api_name + " " + arg["name"] + " " + "constraints missing")

if __name__ == '__main__':
    main()
