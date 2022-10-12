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
import time
import pickle
import argparse

from executor import ExecutorsConfig
from executor import build_executors_from_config
from executor import build_one_executor_from_cfg

def execute_program(executor, program):
    res = executor.execute(program)
    ex, r = executor.get_result(res)

    if executor.is_crash(ex, r):
        print("crash detected")

    print("======= result =======")
    print(r)
    print("------- result -------")

    print("======= ex =======")
    print(ex)
    print("------- ex --------")

    # print(r)
    if r is None:
        print("result is None")
    elif not isinstance(r, list):
        print("Not a list result")
    else:
        for i in range(len(program.apis)):
            ir = r[i]
            api_i = program.apis[i]
            if "msg" in ir:
                print("{api_name}:{message}".format(api_name=api_i.name, message=ir['msg']))

    print("=======\nconsole logs are as follows")
    try:
        for entry in executor.get_execution_log():
            print(entry)
    except:
        print("BOOMMMMMMM!..... Exception happened when trying to get console logs")


def main():
    parser = argparse.ArgumentParser(prog="execute_program",
                                     description="a tool for executing a webgl program on a browser")
    parser.add_argument("--program", type=str, required=True, help="path to the webgl program file")
    parser.add_argument("--exec_conf", type=str, help="the path to the config file of executors")
    parser.add_argument("--executor", type=str, required=False, help="the name of the executor to use")
    parser.add_argument("--times", type=int, default=1)
    parser.add_argument("--pdb", default=False, action="store_true")
    parser.add_argument("--ipython", default=False, action="store_true")

    args = parser.parse_args()

    if not os.path.exists(args.program):
        print("program %s does not exist" % (args.program))
        sys.exit(-1)

    # executors_cfg = ExecutorsConfig(args.exec_conf)


    if args.executor is None:
        if not os.path.exists(args.exec_conf):
            print("exec conf file not exist")
            sys.exit(-1)

        executors = build_executors_from_config(args.exec_conf)
    else:
        executors_cfg = ExecutorsConfig(args.exec_conf)
        exe_name = args.executor
        if exe_name in executors_cfg.local_executor_cfgs:
            exe = build_one_executor_from_cfg(exe_name,
                                              executors_cfg.local_executor_cfgs[exe_name],
                                              executors_cfg)
        elif exe_name in executors_cfg.remote_executor_cfgs:
            exe = build_one_executor_from_cfg(exe_name,
                                              executors_cfg.remote_executor_cfgs[exe_name],
                                              executors_cfg,
                                              remote=True)

        else:
            print("could not locate the executor `" +  exe_name + "`")
            sys.exit(-1)


        executors = [exe]

    # load the program
    program = None
    program_paths = []

    if os.path.isdir(args.program):
        for f in os.listdir(args.program):
            if f.endswith(".pickle"):
                program_paths.append(os.path.join(args.program, f))

    elif os.path.isfile(args.program):
        program_paths = [args.program]

    else:
        print("cannot open %s" % (args.program))
        sys.exit(-1)

    for p in program_paths:
        with open(p, "rb") as inf:
            program = pickle.load(inf)

        if args.pdb and not args.ipython:
            import pdb
            pdb.set_trace()

        if args.ipython and not args.pdb:
            import IPython
            IPython.embed()

        for executor in executors:
            print("executor name:{}".format(executor.name))

            if args.executor != None and args.executor != executor.name:
                continue

            for i in range(args.times):
                print("time: {time}".format(time=i))
                execute_program(executor, program)

        time.sleep(5)

if __name__ == '__main__':
    main()
