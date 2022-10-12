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
logger = logging.getLogger(__name__)

class BaseAnalyzer(object):

    def __init__(self):
        pass

    def analyze(self, program, api, **kwargs):
        '''
        here the api has its values generated
        do the post generation analysis
        for a value
        '''
        self._analyze(program, api, **kwargs)

    def _analyze(self, program, api, **kwargs):
        pass

    def post_analyze(self, program, api, **kwargs):
        self._post_analyze(program, api, **kwargs)

    def _post_analyze(self, program, api, **kwargs):
        pass

    def get_or_create_element_from_dict(self, d, k, cls = dict):
        '''
        this helper class retrieves an element with key `k` if it exists
        otherwise create a new element with cls and insert it to d
        '''
        if d == None:
            logger.error("dict d is None")
            return

        if k not in d:
            d[k] = cls()

        return d[k]
