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

from ..base_mutator import BaseMutator
import random

_api_names = "clientWaitSync"


def flagsclient_wait_sync_mutator_match(program, api, log_message, **kwargs):
    return "flags" in (log_message.message.lower()
                       if log_message.message is not None else "")


class FlagsclientWaitSyncMutator(BaseMutator):
    def __init__(self):
        self.name = "FlagsclientWaitSyncMutator"

    def _mutate(self, program, api, **kwargs):
        api.set_arg_val(1,
                        api.args[1].arg_type.gen_value(None, api, api.args[1]))
        print("FlagsclientWaitSync")
        return True
