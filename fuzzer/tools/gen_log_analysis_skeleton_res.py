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

import sys
import os
import json
import argparse

__cur_dir = os.path.dirname(__file__)
v1_spec_file = os.path.join(__cur_dir, "v1.json")
v2_spec_file = os.path.join(__cur_dir, "v2.json")

def dump_log_dep_res_skel(spec_filename):
    if not os.path.exists(spec_filename):
        print(f"`{spec_filename}` does not exist")
        return

    version = None
    apis = []
    with open(spec_filename) as spec_f:
        spec = json.load(spec_f)

        version = spec["version"]

        for a in spec["apis"]:
            a_obj = {}
            a_obj["id"] = a["id"]
            a_obj["name"] = a["name"]
            a_obj["logs"] = []

            apis.append(a_obj)


    bName = os.path.basename(spec_filename)
    output_fname = "__log_analysis_" + bName
    fo_name = os.path.join(os.path.dirname(spec_filename), output_fname)
    with open(fo_name, "w") as out_f:
        json.dump(apis, out_f, indent=4)

def main():
    spec_files = [v1_spec_file, v2_spec_file]

    for sf in spec_files:
        dump_log_dep_res_skel(sf)

    return 0

if __name__ == '__main__':
    sys.exit(main())
