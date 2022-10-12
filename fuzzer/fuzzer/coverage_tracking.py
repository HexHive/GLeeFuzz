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
This module contains several classes for tracking coverage
exercised by the fuzzer


APICoverageTracker:
   tracking the number of successfully executed APIs

MessageCoverageTracker:
   tracking the number of triggered Log messages of each API

'''



from bitmap import BitMap

class APICoverageTracker(object):
    '''
    This class tracks coverage using the number
    of successfully executed API
    '''

    def __init__(self, size):
        assert size > 0
        self.bitmap = BitMap(size)

    def set(self, pos):
        self.bitmap.set(pos)

    def get(self, pos):
        return self.bitmap.test(pos)

    def test_and_set(self, *positions):
        ret = []

        for pos in positions:
            if not self.get(pos):
                self.set(pos)
                ret.append(pos)

        return ret

    def count(self):
        return self.bitmap.count()

class MessageCoverageTracker(object):
    '''
    This class tracks the number of triggered
    log messages in each API

    '''

    def __init__(self, count) -> None:
        self.__cov = set()

    def set(self, item):
        self.__cov.add(item)

    def get(self, item):
        return item in self.__cov

    def test_and_set(self, *items):
        ret = []

        for i in items:
            if not self.get(i):
                self.set(i)
                ret.append(i)

        return ret

    def count(self):
        return len(self.__cov)
