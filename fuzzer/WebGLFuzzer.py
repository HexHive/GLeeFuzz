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
import logging
import time
from logging.config import fileConfig
from fuzzer import WebGLFuzzer
from fuzzer import setup_signal_handler
from executor.executor_builder import build_executors_from_config, get_default_executors
from getpass import getpass
from subprocess import Popen, PIPE

def freeze_monitor(password):
    proc = subprocess.Popen(["dmesg"], stdout=subprocess.PIPE)
    for i in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
        if "gpu hang" in i.lower():
            proc = Popen("sudo -S systemctl restart display-manager.service".split(), stdin=PIPE, stdout=PIPE, stderr=PIPE)
            proc.communicate(password.encode())


def main():
    password = ""

    parser = argparse.ArgumentParser(prog="WebGLFuzzer",
                                     description="A fuzzer for webgl")
    parser.add_argument("--workdir",
                        type=str,
                        required=True,
                        help="The work dir of the fuzzer")
    parser.add_argument("--seeddir",
                        type=str,
                        required=True,
                        help="the dir where the seeds are provided")
    parser.add_argument("--exec_conf",
                        type=str,
                        help="the path to the config file of executors")
    parser.add_argument("--random_seed",
                        type=int,
                        help="the seed for the random number generator")
    parser.add_argument("--trace",
                        default=False,
                        action='store_true',
                        help="whether to save execution logs or not")

    parser.add_argument("--save_all",
                        default=False,
                        action='store_true',
                        help="whether to save all the programs or not")
    parser.add_argument(
        "--test_page_url",
        type=str,
        default="https://hexdump.cs.purdue.edu/webgl-executor/",
        help="The url of the test page")
    parser.add_argument("--log_cfg",
                        type=str,
                        default="logging.ini",
                        help="config file for controlling logging output")
    parser.add_argument("--freezebot",
                        default=False,
                        help="whether to restart xserver when gpu freeze")

    args = parser.parse_args()

    if args.freezebot:
        password = getpass("Please enter sudo password:")

    if os.path.exists(args.log_cfg):
        print("reading log config from " + args.log_cfg)
        # https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/
        fileConfig(args.log_cfg, disable_existing_loggers=False)

    print("building executors ......")

    if args.exec_conf == None:
        executors = get_default_executors()
    else:
        if not os.path.exists(args.exec_conf):
            print("executor config file not exists")
            sys.exit(-1)
        else:
            executors = build_executors_from_config(args.exec_conf)

    print(str(len(executors)) + " executors built, starting the fuzzer ...")
    fuzzer = WebGLFuzzer(args.workdir,
                         args.seeddir,
                         executors,
                         random_seed=args.random_seed,
                         trace=args.trace,
                         save_all=args.save_all)

    setup_signal_handler()

    fuzzer.start()

    if args.freezebot:
        while True:
            sleep(1)
            freeze_monitor(password)


if __name__ == '__main__':
    main()
