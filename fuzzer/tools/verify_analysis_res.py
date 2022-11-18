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


import sys, os
import json
import re

def main():
    if len(sys.argv) < 2:
        print("please provide the result file")
        sys.exit(-1)

    json_file = sys.argv[1]

    if not os.path.exists(json_file):
        print(f"`{json_file}` does not exist")
        sys.exit(-1)

    all_matches = set()
    nr_logs = 0
    with open(json_file) as inf:
        json_obj = json.load(inf)
        for obj in json_obj:
            api_id = obj["id"]
            nr_logs = nr_logs + len(obj["logs"])

            for lr  in obj["logs"]:
                for dep in lr["deps"]:
                    if dep["type"] != "arg" and dep["type"] != "api":
                        print(dep["type"])

    print(f"nr_logs: {nr_logs}")

if __name__ == '__main__':
    main()
