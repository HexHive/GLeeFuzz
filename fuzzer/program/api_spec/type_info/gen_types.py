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


import sys
import os
import string

def main():

    if len(sys.argv) < 2:
        print("Please provide the file containing types")
        sys.exit(-1)


    input_file = sys.argv[1]

    with file(input_file) as inf:
        for l in inf.readlines():
            l = l.strip()

            tmpl =string.Template("class $type_name:\n\tdef __init__(self):\n\t\tself.name=\"$type_name\"\n\tdef gen_value(self, program, api, arg):\n\t\tpass")

            v = tmpl.substitute(type_name=l)
            print(v)

if __name__ == "__main__":
    main()
