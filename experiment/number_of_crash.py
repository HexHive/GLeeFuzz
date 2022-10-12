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

import sys
import datetime

def convert_month_abbr_to_number(month_abbr):
    return {
        'Jan': 1,
        'Feb': 2,
        'Mar': 3,
        'Apr': 4,
        'May': 5,
        'Jun': 6,
        'Jul': 7,
        'Aug': 8,
        'Sep': 9,
        'Oct': 10,
        'Nov': 11,
        'Dec': 12
    }[month_abbr]

def decode_time_to_epoch_time(time_lst):
    month = convert_month_abbr_to_number(time_lst[0])
    day = int(time_lst[1])
    hour = int(time_lst[2].split(':')[0])
    minute = int(time_lst[2].split(':')[1])
    ts = (datetime.datetime(2022,month,day,hour,minute) - datetime.datetime(1970,1,1)).total_seconds()
    return ts

def open_file_return_lines(file_name):
    with open(file_name, 'r') as f:
        return f.readlines()

def get_first_argument():
    return sys.argv[1]

def generate_empty_list(length):
    return [0] * length

def list_to_accumulated_list(lst):
    return [sum(lst[:i+1]) for i in range(len(lst))]
    
if __name__ == '__main__':
    log_file = get_first_argument()
    log_lines = open_file_return_lines(log_file)
    report = generate_empty_list(24)
    first_line = True
    start_time = 0
    for line in log_lines:
        if first_line:
            start_time = decode_time_to_epoch_time(line.split())
            first_line = False
            continue
        if "pickle" in line:
            time_stamp = line.split()[5:8]
            elapsed = decode_time_to_epoch_time(time_stamp) - start_time
            report[int(elapsed / 3600)] += 1

    print(report)

