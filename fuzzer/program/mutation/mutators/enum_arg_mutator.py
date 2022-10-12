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

import logging
from fuzzywuzzy import fuzz
from .base_mutator import BaseMutator
logger = logging.getLogger(__name__)


def enum_arg_mutator_match(program, api, log_message, **kwargs):
    logger.debug("[enum_arg_mutator_match]log_message: %s", log_message)

    if log_message.message_type != "INVALID_ENUM":
        logger.debug(
            "[enum_arg_mutator_match] log message type is not INVALID_ENUM")
        return False

    if fuzz.partial_ratio(log_message.api_name, api.name) != 100:
        # we use a partial match on the api name
        logger.debug(
            "[enum_arg_mutator_match] partial match of apiname with message not returning 100"
        )
        return False

    logger.debug("[enum_arg_mutator_match] matching worked, returning True")
    return True


class EnumArgMutator(BaseMutator):
    '''
    Use to handle INVALID_ENUM message
    '''
    def __init__(self, **kwargs):
        self.name = "EnumArgMutator"

    def _mutate(self, program, api, **kwargs):

        log_message = kwargs.get("log_message")

        assert log_message != None

        # if log_message == None:
        #     return False

        msg = log_message.message

        # choose the argument
        # of type GLenum and with max overlap in name
        m_arg = None
        m_diff = 0
        m_idx = -1

        for i in range(len(api.args)):
            arg = api.args[i]
            if arg.arg_type.name != "GLenum":
                continue

            diff = fuzz.ratio(arg.name, msg)
            if diff > m_diff:
                m_diff = diff
                m_arg = arg
                m_idx = i

        # if we found one
        ret = False
        if m_arg != None:
            logger.debug("a matching argument is found, argname: %s, index:%d",
                         m_arg.name, m_idx)
            m_num = 0
            o_val = api.arg_values[m_idx]
            while m_num < 5:
                v = m_arg.arg_type.gen_value(program, api, m_arg)
                if v != o_val:
                    ret = True
                    api.arg_values[m_idx] = v
                    break

                m_num = m_num + 1
        else:
            logger.debug("No matching argument was found")

        return ret
