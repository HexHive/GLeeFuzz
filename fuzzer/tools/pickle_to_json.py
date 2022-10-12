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

import os, sys
import pathlib
import pickle
import json
import argparse

def pickle_to_json(pickle_file_path, json_file_path):

    print("converting `" + str(pickle_file_path) + \
          "` to `" + str(json_file_path) + "`")


    if isinstance(pickle_file_path, str):
        with open(pickle_file_path, "rb") as inf:
            p = pickle.load(inf)
    elif isinstance(pickle_file_path, pathlib.Path):
        with pickle_file_path.open(mode="rb") as inf:
            p = pickle.load(inf)
    else:
        print("unsupported type for argument: pickle_file_path")
        return

    if isinstance(json_file_path, str):
        with open(json_file_path, "w") as outf:
            outf.write(p.to_json(indent=4))
    elif isinstance(json_file_path, pathlib.Path):
        with json_file_path.open(mode="w") as outf:
            outf.write(p.to_json(indent=4))
    else:
        print("unsupported type for argument: json_file_path")
        return

def main():
    parser = argparse.ArgumentParser(prog="a tool for converting a pickle format to json format")
    parser.add_argument("--pickle", type=str, required=False,
                        help="the path to a pickle format webgl program")
    parser.add_argument("--pickle_dir", type=str, required=False,
                        help="the directory containing pickle format webgl program files to convert")
    parser.add_argument("--output", type=str, required=False,
                        help="the path of the json file to write result to")
    parser.add_argument("--output_dir", type=str, required=False,
                        help="the directory to a batch converting pickle format json format")

    args = parser.parse_args()

    if args.pickle != None:
        if args.output == None:
            json_file = pathlib.Path(args.pickle + ".json")
        else:
            json_file = pathlib.Path(args.output)

        pickle_to_json(args.pickle, json_file)

    if args.pickle_dir != None:
        if args.output_dir == None:
            print("Please tell me the directory you want to write the converted results to")
            return

        print("converting pickle files in `" + args.pickle_dir + "` to `" + args.output_dir  + "`")
        # walk the input dir
        p_path = pathlib.Path(args.pickle_dir)
        o_path = pathlib.Path(args.output_dir)
        for root, dirs, files in os.walk(args.pickle_dir):
            # root = pathlib.Path(root).as_posix()
            _r_path = pathlib.Path(root)
            rel_path = _r_path.relative_to(p_path)
            outdir =  o_path / rel_path
            if not outdir.exists():
                outdir.mkdir()

            for f in files:
                if not f.endswith(".pickle"):
                    continue
                pickle_file_path  = _r_path / f
                json_file_path = outdir / (f + ".json")
                pickle_to_json(pickle_file_path, json_file_path)

if __name__ == '__main__':
    main()
