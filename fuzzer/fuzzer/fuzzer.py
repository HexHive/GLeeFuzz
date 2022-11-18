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

'''
Implemmentation of WebGL Fuzzer

Internally, it uses interfaces provided by WebGLProgram to generate
a new program or mutate an existing program, and execute the 
program on WebGLExecutor(s).
'''

from fuzzer.internal_state import FuzzerInternalState
import os
import sys
import random
import pickle
import shutil
import logging

from typing import List

import time
logger = logging.getLogger(__name__)

from utils.utils import alphanum_key
from utils.utils import choose_random_one_from_list
from utils.utils import rand_in_hundred

from program import WebGLProgram
from program.api_spec import WebGLSpecs
from executor import WebGLExecutor
from .coverage_tracking import APICoverageTracker, MessageCoverageTracker

from .signal_handler import should_stop

class WebGLFuzzer(object):

    def __init__(self, work_dir:str,
                 seed_dir:str,
                 executors:List[WebGLExecutor],
                 random_seed:int=None,
                 trace:bool=False,
                 save_all:bool=False):
        self.work_dir = os.path.abspath(work_dir)
        self.seed_dir = os.path.abspath(seed_dir)
        self.internal_seeds_dir = os.path.join(self.work_dir, "seeds")
        self.internal_queue_dir = os.path.join(self.work_dir, "queue")
        self.internal_crashes_dir = os.path.join(self.work_dir, "crashes")
        self.internal_ctx_lost_dir = os.path.join(self.work_dir, "ctx_lost")
        self.internal_exception_dir = os.path.join(self.work_dir, "exeptions")
        self.internal_all_programs_dir = os.path.join(self.work_dir, "all-programs")

        self.executors = executors
        self.master_executor = None
        self.__detect_master_executor()

        self.__program_ext = ".pickle"
        self.__program_info_ext = ".info"
        self.__program_log_ext = ".log"
        self.seeds = []
        self.queue = []
        self.__cur_program_fname = "__cur_program" + self.__program_ext
        self.__cur_program_fname_prev = "__cur_program_prev" + self.__program_ext
        self.__cur_program_path = os.path.join(self.work_dir, self.__cur_program_fname)
        self.__cur_program_path_prev = os.path.join(self.work_dir, self.__cur_program_fname_prev)
        self.__fuzzer_args_file = os.path.join(self.work_dir, "fuzzer_args.txt")
        self.__execute_track_file = os.path.join(self.work_dir, "exec_track.txt")
        self.__internal_state_file = os.path.join(self.work_dir, "fuzzer_internal_state.pickle")

        self.api_cov = {}
        self.msg_cov = {}
        self.__init_cov()

        self.__queue_seq = 0
        self.check_seed_dir()

        if random_seed == None:
            self.random_seed = random.getrandbits(32)
        else:
            self.random_seed = random_seed
        random.seed(self.random_seed)

        self.trace = trace
        self.save_all = save_all
        self.init_workdir()

        self.__iter_seq:int = 0
        self.__execute_track_fd = None
        self.__open_exec_track_file()

    def __open_exec_track_file(self):
        self.__execute_track_fd = open(self.__execute_track_file, "a+")

    def __del__(self):
        if self.__execute_track_fd != None:
            self.__execute_track_fd.close()

    def __write_fuzzer_args_file(self):
        with open(self.__fuzzer_args_file, "w") as state_file:
            state_file.write("command:" + str(sys.argv) + "\n")
            state_file.write("executors:" + str(self.executors) + "\n")
            state_file.write("seed_dir:" + str(self.seed_dir) + "\n")
            state_file.write("random_seed:" + str(self.random_seed) + "\n")
            state_file.write("trace:" + str(self.trace) + "\n")

    def __init_cov(self):
        self.api_cov = {}
        self.msg_cov = {}
        for k, spec in WebGLSpecs.items():
            self.api_cov[k] = APICoverageTracker(len(spec.apis))
            self.msg_cov[k] = MessageCoverageTracker(len(spec.apis))

    def __detect_master_executor(self):
        if self.executors == None or len(self.executors) == 0:
            logger.fatal("No executors defined, exiting")
            sys.exit(-1)

        for exe in self.executors:
            if exe.master:
                self.master_executor = exe
                return

    def init_workdir(self):
        '''

        1. create directories if needed
        2. load seeds if needed
        '''
        self.__check_and_prepare_workdir()

        if not self.__try_resume_from_existing_workdir():
            self._load_seeds()

        self.__write_fuzzer_args_file()


    def __check_and_load_existing_queue(self):
        ignored = [".", ".."]
        q_files = [i for i in os.listdir(self.internal_queue_dir) if i not in ignored]

        q_files.sort()

        logger.debug("starting to load existing queue files")

        for q in q_files:
            f_path = os.path.join(self.internal_queue_dir, q)
            try:
                logger.debug("Loading queue file: `%s`", f_path)
                with open(f_path, "rb") as sf:
                    p = pickle.load(sf)
                    self.queue.append(p)
            except e:
                logger.warning("there was an exception loading program from '%s'", f_path)

        logger.debug("Successfully loaded %d programs in queue", len(self.queue))


    def __load_internal_state(self)->bool:

        if not os.path.exists(self.__internal_state_file):
            return False

        with open(self.__internal_state_file, "rb") as inf:
            try:
                __internal_state:FuzzerInternalState = pickle.load(inf)

                self.__queue_seq = __internal_state.queue_seq
                self.__iter_seq = __internal_state.iter_seq
                self.trace = __internal_state.trace
                self.api_cov = __internal_state.api_cov_info
                self.msg_cov = __internal_state.msg_cov_info
                random.setstate(__internal_state.rand_state)
                self.save_all = __internal_state.save_all
                logger.debug("Internal fuzzer state loaded")
            except:
                logger.warn("loading fuzzer internal state failure: `%s`",
                            self.__internal_state_file)
                return False

        return True

    def __try_resume_from_existing_workdir(self):

        if os.path.exists(self.__internal_state_file):
            load_res = self.__load_internal_state()
            if not load_res:
                return False

            self.__check_and_load_existing_queue()
            if len(self.queue) != self.__queue_seq:
                logger.warn("# of programs in queue is not the same " + \
                            "as queue_seq, len(queue)=%d, queue_seq=%d",
                            len(self.queue), self.__queue_seq)

            return True

        if os.path.exists(self.__cur_program_path):
            logger.warning("there is an existing program, backed up in '%s'",
                           self.__cur_program_fname + ".backup")
            shutil.copyfile(self.__cur_program_path, self.__cur_program_path + ".backup")
        return False

    def _load_seeds(self):
        ignored = [".", ".."]
        seed_filenames = [s for s in os.listdir(self.seed_dir) if s not in ignored]
        seed_filenames.sort(key=alphanum_key)


        logger.debug("starting to load seeds ....")
        for s in seed_filenames:
            s_path = os.path.join(self.seed_dir, s)
            s_save_path = os.path.join(self.internal_seeds_dir, s)
            shutil.copyfile(s_path, s_save_path)
            logger.debug("Loading seed: `%s`", s_path)
            try:
                with open(s_save_path, "rb") as sf:
                    program = pickle.load(sf)

                new_cov = self.run_program_and_check_results(program, save_to_queue=False)
                if new_cov:
                    self._save_program_to_queue(program, s, prefix="seed-")
            except:
                logger.warning("loading seed `%s` failed", s_path)

    def __check_and_prepare_workdir(self):
        if os.path.exists(self.work_dir):
            logger.warn('workdir (%s) exists', self.work_dir)
        else:
            os.makedirs(self.work_dir)
        if not os.path.exists(self.internal_seeds_dir):
            os.makedirs(self.internal_seeds_dir)
        if not os.path.exists(self.internal_queue_dir):
            os.makedirs(self.internal_queue_dir)
        if not os.path.exists(self.internal_crashes_dir):
            os.makedirs(self.internal_crashes_dir)
        if not os.path.exists(self.internal_ctx_lost_dir):
            os.makedirs(self.internal_ctx_lost_dir)
        if not os.path.exists(self.internal_all_programs_dir):
            os.makedirs(self.internal_all_programs_dir)

    def check_seed_dir(self):
        '''
        check the external seed dir
        '''
        if not os.path.exists(self.seed_dir):
            logger.fatal("seed dir %s does not exist", self.seed_dir)
            sys.exit(-1)

        if len(os.listdir(self.seed_dir)) == 0:
            logger.warn("seed dir %s is empty", self.seed_dir)

    def __save_program(self, program:WebGLProgram,
                       dirname:str,
                       filename:str,
                       prefix:str=None,
                       sync:bool=False)->str:

        if filename != None:
            fname_root = filename
        else:
            fname_root = str(hash(program)) + "-" + str(time.time()) + self.__program_ext

        if prefix != None:
            fname_root = prefix + fname_root

        if dirname != None:
            full_path = os.path.join(dirname, fname_root)
        else:
            full_path = fname_root

        with open(full_path, "wb") as sf:
            pickle.dump(program, sf)
            if sync:
                sf.flush()
                os.fsync(sf.fileno())

        return full_path

    def __save_file(self, content, path:str, sync:bool=False):
        '''
        Save content in a file identified by path
        '''
        with open(path, "w") as sf:
            sf.write(content)
            if sync:
                sf.flush()
                os.fsync(sf.fileno())

    def __format_log(self, log):
        ret = ""
        if log == None:
            return ret

        for i, log in enumerate(log):
            ret = "{ret}\n{idx} %% {api}:{msg}".format(ret=ret, idx=i, api=log[0], msg=log[1])

        return ret

    def _save_program_and_related_info(self, program:WebGLProgram,
                                       dirname:str,
                                       executor:WebGLExecutor,
                                       ex, res=None):

        executor_name = executor.name
        executor_specific_path = os.path.join(dirname, executor_name)

        if not os.path.exists(executor_specific_path):
            os.makedirs(executor_specific_path)

        p_path = self.__save_program(program, executor_specific_path, None, sync=True)

        if ex != None:
            fname_info = p_path.replace(self.__program_ext, self.__program_info_ext)
            self.__save_file(str(ex), fname_info, sync=True)

        if self.trace and executor == self.master_executor and res != None:
            fname_log = p_path.replace(self.__program_ext, self.__program_log_ext)

            log = []
            for i in range(len(program.apis)):
                log.append((program.apis[i].name, res[i]["msg"]))

            self.__save_file(self.__format_log(log), fname_log)

    def _backup_current_program_to_prev(self):
        if not os.path.exists(self.__cur_program_path):
            return

        shutil.copyfile(self.__cur_program_path, self.__cur_program_path_prev)

    def _save_current_program(self, program:WebGLProgram):
        if program == None:
            return
        self.__save_program(program, self.work_dir, self.__cur_program_fname, sync=True)

    def __check_coverage(self, program:WebGLProgram,
                         res):

        if not isinstance(res, list):
            return False

        ok_api_ids = []
        api_msgs = []
        for i in range(len(program.apis)):
            if "msg" not in res[i] or res[i]["msg"] == None or res[i]["msg"] == "":
                ok_api_ids.append(program.apis[i].id)
            else:
                api_msgs.append((program.apis[i].id, res[i]["msg"]))

        new_apis = self.api_cov[program.version].test_and_set(*ok_api_ids)
        new_msgs = self.msg_cov[program.version].test_and_set(*api_msgs)

        if len(new_apis) > 0:
            logger.debug("== version: {version}, new apis: {apis}".format(version=program.version, apis=str(new_apis)))

        if len(new_msgs) > 0:
            logger.debug("== version: {version}, new msgs: {msgs}".format(version=program.version, msgs=str(new_msgs)))

        return len(new_apis) > 0 or len(new_msgs) > 0

    def __record_execution_track(self, program, generate):
        if self.__execute_track_fd != None:
            track_msg = "{ts}:{seq}:{gen}:{version}:{api_cov1}:{api_cov2}:{msg_cov1}:{msg_cov2}".format(
                ts=time.time(),
                seq=self.__iter_seq,
                gen=generate,
                version=program.version,
                api_cov1=self.api_cov[1].count(),
                api_cov2=self.api_cov[2].count(),
                msg_cov1=self.msg_cov[1].count(),
                msg_cov2=self.msg_cov[2].count()
            )
            self.__iter_seq += 1
            self.__execute_track_fd.write(track_msg + "\n")
            os.fsync(self.__execute_track_fd.fileno())

    def _save_program_to_queue(self, program:WebGLProgram,
                               filename:str,
                               prefix:str=None):

        '''
        If filename is provided as a None value,
        filename part will be created using its hash values etc.
        '''

        queue_prefix = "{x:010d}".format(x=self.__queue_seq) + "-"
        self.__queue_seq += 1
        logger.debug("**** queue_seq=%d", self.__queue_seq)
        if prefix == None:
            prefix = queue_prefix
        else:
            prefix = queue_prefix + prefix

        self.__save_program_to_queue(program,
                                     filename,
                                     prefix)

    def __save_program_to_queue(self, program:WebGLProgram,
                               filename:str,
                               prefix:str=None):
        path = os.path.join(self.work_dir, self.internal_queue_dir)
        if program not in self.queue:
            self.__save_program(program, path, filename, prefix, sync=True)
            self.queue.append(program)

    def _verify_ctx_lost_or_crash(self, program:WebGLProgram,
                                  executor:WebGLExecutor,
                                  need_refresh:bool) -> bool:
        '''
        This routine is used to verify context lost triggered by programs

        program: the input program
        executor: the executor to verify on
        need_refresh: whether this function needs to refresh the test page

        return: whether the caller (of this function) needs to refresh
        '''

        if need_refresh:
            if not executor.refresh_test_page():
                logger.debug("time out happened while refreshing in %s, restarting", executor.name)
                executor.restart()

        res = executor.execute(program)
        ex, r = executor.get_result(res)

        if need_refresh:
            logger.debug("need_refresh: True, results: %s", str(r))
        else:
            logger.debug("need_refresh: False, results: %s", str(r))

        if executor.is_crash(ex, r):
            logger.debug("crash detected in _verify_ctx_lost_or_crasg, saving the POC and restart the browser")
            self._save_program_and_related_info(program, self.internal_crashes_dir , executor, ex)
            executor.restart()
            return False

        if r != None and "gl_create_failure" in r and r["gl_create_failure"] == True:
            logger.debug("ctx lost verified in _verify_ctx_lost_or_crash")
            self._save_program_and_related_info(program, self.internal_ctx_lost_dir, executor, ex)
            return True

        if need_refresh:
            return self._verify_ctx_lost_or_crash(program, executor, False)

        return False

    def _load_program(self, path:str):
        try:
            with open(path, "rb") as inf:
                return pickle.load(inf)
        except:
            return None


    def run_program_on_exucutors(self, program:WebGLProgram):
        '''
        return the results object
        '''

        exe_results = []

        for exe in self.executors:
            if exe.enabled:
                exe_results.append(exe.execute(program))
            else:
                exe_results.append(None)

        return exe_results


    def __save_to_all_programs(self, program):

        if self.save_all:
            prefix = "{x:010d}".format(x=self.__iter_seq) + "-"
            self.__save_program(program,
                                self.internal_all_programs_dir,
                                None,
                                prefix,
                                True)

    def start(self):
        versions = [1, 2]
        p = None
        generate = False

        while True:

            if should_stop():
                self.__save_internal_state_and_exit()

            if (p == None or len(self.queue) == 0 or rand_in_hundred() < 30) or "EXCLUDE_LOG_GUIDED_MUTATORS" in os.environ:
                ver = choose_random_one_from_list(versions)
                logger.debug("== Generating a program of version:" + str(ver))
                p = WebGLProgram.generate(ver)
                generate = True
            else:
                logger.debug("== Mutating an existing program")
                s = choose_random_one_from_list(self.queue)
                p = s.mutate()

            self._backup_current_program_to_prev()
            self._save_current_program(p)

            self.__save_to_all_programs(p)

            self.run_program_and_check_results(p)

            self.__record_execution_track(p, generate)

    def run_program_and_check_results(self, program:WebGLProgram,
                                      save_to_queue=True):

        exe_results = self.run_program_on_exucutors(program)
        return self.check_exe_results(exe_results, program,
                                      save_to_queue=save_to_queue)

    def __save_internal_state_and_exit(self):

        _internal_state = FuzzerInternalState(self.__iter_seq,
                                              self.__queue_seq,
                                              self.api_cov,
                                              self.msg_cov,
                                              random.getstate(),
                                              self.trace,
                                              self.save_all)
        with open(self.__internal_state_file, "wb") as state_f:
            pickle.dump(_internal_state, state_f)

        logger.debug("fuzzer internal state saved")
        sys.exit()

    def check_exe_results(self, exe_results,
                          program:WebGLProgram,
                          save_to_queue=True):
        '''
        If program triggers new coverage in master executor,
        return True

        '''

        ret = False
        for i in range(len(self.executors)):
            res = exe_results[i]

            pres = self.__check_result_for_one_executor(self.executors[i],
                                                        res,
                                                        program,
                                                        save_to_queue=save_to_queue)
            if pres:
                ret = True

        return ret

    def __check_result_for_one_executor(self,
                                        executor:WebGLExecutor,
                                        res,
                                        program:WebGLProgram,
                                        save_to_queue=True):
        '''
        check the result `res` for executor `executor`

        If executor is a master executor, and new coverage
        is seen, True is returned, else return False
        '''

        ret = False
        if res == None:
            logger.debug("%s is not enabled due to some" +
                         " restart failures, trying to" +
                         " restart again", executor.name)
            executor.restart()
            return ret

        logger.debug("Checking result for '%s'", executor.name)
        ex, r = executor.get_result(res)

        if r == None:
            logger.debug("We got a None result")

        if r != None and "gl_create_failure" in r and \
           r["gl_create_failure"] == True:
            logger.debug("A gl_create_failure is detected, "
                         "trying to verify the previous program")
            p_prog = self._load_program(self.__cur_program_path_prev)
            if self._verify_ctx_lost_or_crash(p_prog, executor, True):
                if not executor.refresh_test_page():
                    logger.debug("[B]time out happened refreshing %s, " +\
                                 "restarting",
                                 executor.name)
                    executor.restart()

                res = executor.execute(program)
                ex, r = executor.get_result(res)

        if executor.is_crash(ex, r):
            logger.debug("a crash is detected, " + \
                         "saving the POC and restarting the browser")
            self._save_program_and_related_info(program,
                                                self.internal_crashes_dir,
                                                executor,
                                                ex)
            executor.restart()

        if self.trace:
            self._save_program_and_related_info(program,
                                                self.internal_exception_dir,
                                                executor,
                                                ex,
                                                res=r)

        if executor == self.master_executor:
            logger.debug("checking coverage on master executor")
            if r == None:
                return ret
            if self.__check_coverage(program, r) > 0:
                logger.debug("new coverage triggered")

                program.save_log_messages(r)

                if save_to_queue:
                    self._save_program_to_queue(program, None)

                ret = True

        return ret
