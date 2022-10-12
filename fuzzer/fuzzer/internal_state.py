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

class FuzzerInternalState(object):

    def __init__(self,
                 iter_seq:int,
                 queue_seq:int,
                 api_cov_info,
                 msg_cov_info,
                 rand_state,
                 trace:bool,
                 save_all:bool):
        self.__iter_seq=iter_seq
        self.__queue_seq=queue_seq
        self.__api_cov_info=api_cov_info
        self.__msg_cov_info=msg_cov_info
        self.__rand_state=rand_state
        self.__trace=trace
        self.__save_all = save_all

    @property
    def iter_seq(self):
        return self.__iter_seq

    @iter_seq.setter
    def iter_seq(self, value):
        self.__iter_seq = value

    @property
    def queue_seq(self):
        return self.__queue_seq

    @queue_seq.setter
    def queue_seq(self, value):
        self.__queue_seq = value

    @property
    def api_cov_info(self):
        return self.__api_cov_info

    @api_cov_info.setter
    def api_cov_info(self, val):
        self.__api_cov_info = val

    @property
    def msg_cov_info(self):
        return self.__msg_cov_info

    @msg_cov_info.setter
    def msg_cov_info(self, val):
        self.__msg_cov_info = val

    @property
    def rand_state(self):
        return self.__rand_state

    @rand_state.setter
    def rand_state(self, state):
        self.__rand_state = state

    @property
    def trace(self):
        return self.__trace

    @trace.setter
    def trace(self, value):
        self.__trace = value

    @property
    def save_all(self):
        return self.__save_all

    @save_all.setter
    def save_all(self, val):
        self.__save_all =val
