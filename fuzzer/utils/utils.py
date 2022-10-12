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

import re
import random
import logging
import string
logger = logging.getLogger(__name__)


# functions related to generating random values
def rand_seed(seed_val):
    random.seed(seed_val)

def x_out_of_n(x, n):
    r = int(random.random()*n)

def choose_random_one_from_list(lst):

    if lst == None or len(lst) == 0:
        logger.error("list is None or empty")
        return None

    l = len(lst)
    r = int(random.random() * l)
    return lst[r]

def choose_random_int_in_range(start, end):
    '''
    Return random integer in range [start, end], including both end points.
    '''

    return random.randint(start, end)

def choose_random_float_in_range(start, end):
    return random.uniform(start, end)

def gen_rand_float():
    r = choose_random_float_in_range(0.0, 1.0)
    # generate 0.0 and rand float number half-half
    if r <= 0.5:
        return 0.0

    return choose_random_float_in_range(-32.0, 32.0)

def gen_ran_float_array(n_elem):
    ret = []
    for i in range(n_elem):
        ret.append(gen_rand_float())

    return ret

def gen_rand_int(n_bits=32):
    r = random.getrandbits(n_bits)
    return r

def gen_rand_int_array(n_elem, n_bits=32):
    ret = []

    for i in range(n_elem):
        ret.append(gen_rand_int(n_bits))

    return ret

def gen_rand_string(size = 10):
    letters = string.printable
    # TODO: need to tune this a ...lot
    ret = ''.join(random.choice(letters) for i in range(size))
    return ret

def gen_rand_string_array(size=10, n_elem=3):
    ret = []

    for i in range(n_elem):
        ret.append(gen_rand_string(size))

    return ret

def rand_in_hundred():
    return int(random.random() * 100)

# other utility functions
def tryint(s):
    try:
        return int(s)
    except:
        return s

def alphanum_key(s:str):
    """ Turn a string into a list of string and number chunks.
        "z23a" -> ["z", 23, "a"]

    used in list.sort(key=alphanum_key)
    """
    return [ tryint(c) for c in re.split('([0-9]+)', s) ]
