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

from .base_mutator import BaseMutator

_api_names = "drawArrays,drawElements,drawElementsInstanced,drawArraysInstanced,drawRangeElements"


def use_program_mutator_match(program, api, log_message, **kwargs):
    return log_message.message == "no valid shader program in use"


class UseProgramMutator(BaseMutator):
    '''

    Use to handle `program not used` message
    '''
    def __init__(self):
        self.name = "UseProgramMutator"

    def _mutate(self, program, api, **kwargs):
        program.gen_args_for_api_and_add_to_program_by_name("useProgram")
        return True
