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

import signal

__should_stop=False

def __ctrl_c_handler(sig, frame):
    global __should_stop
    print("****** Ctrl-C pressed *****, __should_stop=" + str(__should_stop))
    __should_stop=True

def should_stop():
    global __should_stop
    return __should_stop

def setup_signal_handler():
    signal.signal(signal.SIGINT, __ctrl_c_handler)
