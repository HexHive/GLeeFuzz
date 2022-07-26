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

# This is a script to gather statistics from the logs generated by GLeeFuzz.

import re
import datetime
import sys

def load_file_by_lines(file_name):
    with open(file_name, 'r') as f:
        return f.readlines()

def convert_each_item_in_list_to_int(list_of_items):
    return [int(item) for item in list_of_items]

def decode_time_stamp(time_stamp):
    """Format: 2022-05-19 07:37:49,758"""
    time_str = re.split(',| |-|:', time_stamp)[:7]
    return convert_each_item_in_list_to_int(time_str)

def calc_diff_in_time(time1, time2):
    time_obj1 = datetime.datetime(time1[0], time1[1], time1[2], time1[3], time1[4], time1[5], time1[6] * 1000)
    time_obj2 = datetime.datetime(time2[0], time2[1], time2[2], time2[3], time2[4], time2[5], time2[6] * 1000)
    return (time_obj2 - time_obj1).total_seconds()

def get_previous_status(dictionary):
    status = None
    for key, value in dictionary.items():
        # There should be only one status active at a time
        if value[3]:
            assert status is None
            status = key
    assert status is not None
    return status

def nice_print_records(time, dictionary, mutation_total):
    print(time)
    print(">" * 30)
    for key, value in dictionary.items():
        print(key, "elapsed:", value[1], " count:", value[2])
    print("Total mutation count:", mutation_total)
    print("<" * 30)
    print("")

def get_first_argument():
    return sys.argv[1]

def dump_hourly_report_to_file(file_name, dictionary):
    with open(file_name, 'w') as f:
        f.write('\t' + '\t')
        for i in range(24):
            f.write(str(i + 1) + '\t')
        f.write('\n')
        for key, value in dictionary.items():
            if key == "start":
                continue
            f.write(key + '\t')
            for i in range(24):
                f.write(str(value[4][i]) + '\t')
            f.write('\n')

def dump_str_to_file(file_name, s):
    with open(file_name, 'w') as f:
        f.write(s)

def print_dict_lines(dictionary):
    for key, value in dictionary.items():
        print(key, value)

def float_precision_round(value, precision):
    return round(value, precision)

if __name__ == '__main__':
    log_file = get_first_argument()
    log_lines = load_file_by_lines(log_file)
    last_timestamp = 0

    hourly_report = {}
    seconds_passed = 0

    # Value format: [match_string, total_time_elapsed, total_instance, active_flag, [hourly_elapsed], this_hour_elapsed, hourly_instance, this_hour_instance]
    record_category = \
        {"start": ["", 0, 0, True, [], 0, [], 0],
        "web_driver_init": ["WebDriver manager", 0, 0, False, [], 0, [], 0],
        "seed_init": ["seed dir", 0, 0, False, [], 0, [], 0],
        "program_gen": ["BEGIN generate", 0, 0, False, [], 0, [], 0],
        "check_result": ["BEGIN run", 0, 0, False, [], 0, [], 0],
        "mutation": ["BEGIN mutate", 0, 0, False, [], 0, [], 0]}
        
    mutation_total = 0

    for line in log_lines:
        # we want to collect mutation instances saperately
        # because there may be multiple mutations in one single fuzzing loop
        if "before mutation" in line:
            mutation_total += 1
        
        # only care about the first line in multi-line log entries
        # the keywords are always in the first line
        if not line.startswith("20"):
            continue
        time_stamp_decoded = decode_time_stamp(line)
        
        if record_category["start"][3]:
            last_timestamp = time_stamp_decoded
        
        for key in record_category.keys():
            if key == "start":
                continue
            # if caught any category keyword in line,
            # meaning the previous category is finished
            # and the current category is starting.
            if record_category[key][0] in line:
                previous_status = get_previous_status(record_category)
                # start the new status and end the previous status
                record_category[previous_status][3] = False
                record_category[key][3] = True
                # update the stats of previous status
                record_category[previous_status][2] += 1
                record_category[previous_status][7] += 1
                time_difference = calc_diff_in_time(last_timestamp, time_stamp_decoded)
                record_category[previous_status][1] += time_difference
                
                seconds_passed += float_precision_round(time_difference, 6)
                record_category[previous_status][5] += time_difference
                if seconds_passed >= 3600:
                    # save the hourly report
                    for idx in record_category.keys():
                        record_category[idx][4].append(record_category[idx][5])
                        # reset hourly report
                        record_category[idx][5] = 0
                        record_category[idx][6].append(record_category[idx][7])
                        record_category[idx][7] = 0
                    seconds_passed = 0

                last_timestamp = time_stamp_decoded
                nice_print_records(time_stamp_decoded, record_category, mutation_total)
                break
        
    print(record_category)
    dump_str_to_file(log_file + ".dat", str(record_category))
