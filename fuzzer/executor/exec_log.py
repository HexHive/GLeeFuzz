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

import json
import re

class ExecutionLog(object):
    '''
    This class represents an execution log message
    '''
    def __init__(self, raw_log):
        self.raw_log = raw_log
        self._runtime_msg = None
        self._parse_runtime_msg()

    def _parse_runtime_msg(self):
        pass

    @property
    def message(self):
        if self._runtime_msg != None:
            return self._runtime_msg.message
        return None

    @property
    def message_type(self):
        if self._runtime_msg != None:
            return self._runtime_msg.message_type
        return None

    @property
    def api_name(self):
        if self._runtime_msg != None:
            return self._runtime_msg.api_name
        return None

class RuntimeMessage(object):
    def __init__(self, msg):
        self._raw_msg = msg.strip()
        self._api_name = None
        self._message_type = None
        self._message = None
        self._parse_message()

    def _parse_message(self):
        if self._raw_msg == None or len(self._raw_msg) == 0:
            return

        msg_splits = re.split(":(?!//)", self._raw_msg)

        if len(msg_splits) != 4:
            return

        self._api_name = msg_splits[2].strip()

        self._message_type = msg_splits[1].strip()
        self._message = msg_splits[3].strip()

    @property
    def message(self):
        return self._message

    @property
    def message_type(self):
        return self._message_type

    @property
    def api_name(self):
        return self._api_name

class ChromeExecutionLog(ExecutionLog):

    def __parse_json_formt_msg(self):
        self.raw_message = self.raw_log["message"]

    def _parse_runtime_msg(self):
        '''

        parse raw_log and construct _runtime_msg

        A message looks like this:

        {'level': 'WARNING',
        'message': 'https://hexdump.cs.purdue.edu/webgl-executor/js/test_runner.js 381 WebGL: INVALID_ENUM: getSamplerParameter: invalid parameter name',
        'source': 'rendering',
        'timestamp': 1597472402184}
        '''

        if isinstance(self.raw_log, dict):
            self.__parse_json_formt_msg()
        elif isinstance(self.raw_log, str):
            try:
                raw_str = self.raw_log.replace("\'", "\"")
                self.raw_log = json.loads(raw_str)
                self.__parse_json_formt_msg()
            except json.JSONDecodeError as de:
                self.raw_message = self.raw_log

        self._runtime_msg = RuntimeMessage(self.raw_message)


    def __str__(self):
        message_type = self.message_type if self.message_type != None else "None"
        api_name = self.api_name if self.api_name != None else "None"
        message = self.message if self.message != None else "None"
        return "message_type: " + message_type + ", api_name: " \
            + api_name + ", message: " + message





