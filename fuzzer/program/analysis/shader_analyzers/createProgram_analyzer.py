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

class CreateProgramAnalyzer(ShaderBaseAnalyzer):


    def _post_analyze(self, program, api, **kwargs):
        if "pos" not in kwargs:
            logger.warning("pos argument is not passed in")
            return

        programs_info = self.get_programs_info(program)
        pos = kwargs["pos"]

        if pos in programs_info:
            logger.warning("program state for %d already recorded", pos)

        programs_info[pos] = self.new_program_state()
