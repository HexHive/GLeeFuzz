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

from .shader_base_analyzer import ShaderBaseAnalyzer

import logging
logger = logging.getLogger(__name__)

class UseProgramAnalyzer(ShaderBaseAnalyzer):

    def _analyze(self, program, api):
        program_val = api.get_arg_val(0)
        programs_info = self.get_programs_info(program)

        if program_val not in programs_info:
            logger.warning("program '%d' not recorded", program_val)
            return
        program_state = programs_info[program_val]
        program_state["used"] = True
