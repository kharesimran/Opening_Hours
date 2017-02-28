"""
Notes:
"oh" has been used as a short form for Opening Hours
The pgSQL code shared by Prof. Keller was a useful guide

Code summary:
1. Read the oh string from the input csv file
2. Clean extraneous spaces
3. Check if oh string is valid
4. If oh string is valid, parse it and store the result in a list
5. Determine if a place is open at the current day and time
"""

import argparse
import re
import sys
import logging
import csv
# Datetime ref: http://stackoverflow.com/a/10112119
from datetime import datetime, timedelta

weekdays = ["mo", "tu", "we", "th", "fr", "sa", "su"]


def write_output_to_file(write_row, output_file_path):

    """ Writes clean string, validity, open/close, oh_list to csv file"""

    with open(output_file_path, "a", newline='') as output_file:
        writer = csv.writer(output_file)
        writer.writerow(write_row)


def check_if_open(final_oh_list, current_day, current_time):

    """ Checks if the place is open at a day and time """

    current_day = current_day.lower()
    current_time = datetime.strptime(current_time, '%H:%M')

    for item in final_oh_list:
        # For eg. item = [["mo", "tu", "we"], [9:00, 12:00], [14:00, 18:00]]
        if current_day in item[0]:
            for index in range(1, len(item)):
                start_time = item[index][0]
                end_time = item[index][1]
                if start_time <= current_time <= end_time:
                    return True
    return False


def remove_day(day, final_oh_list):

    """
    If day is repeated in the oh string, remove it to overwrite its time range
    For eg. oh = "9:00-23:00; fr 10:00-22:00"
    final_oh_list = [[["mo", "tu", "we", "th", "sa", "su"], [9:00, 23:00]]
                     [["fr"], [10:00, 22:00]]]
    """

    for x in range(0, len(final_oh_list)):
        if day in final_oh_list[x][0]:
            final_oh_list[x][0].remove(day)
    return final_oh_list


def get_time_open(time_ranges):

    """ Accepts the time range part of the oh string, and returns
        a list of the time ranges in datetime format"""

    # This will contain the final time ranges
    # Format: [[start_time1, end_time1], [start_time2, end_time2]]
    time_open = []

    # Check if the time range only contains numbers and some characters
    # Eg. in case of "7:30-23:00, sa 09:00-12:00, 14:00-18:00"
    # The parsing will be incorrect
    valid_characters = [str(x) for x in range(0, 10)]
    valid_characters.extend([",", ":", "-", " "])
    for c in time_ranges:
        if c not in valid_characters:
            return []

    # time_ranges = "7:30-12:00, 13:45-18:00"
    time_ranges_list = time_ranges.split(",")
    # time_ranges_list = [" 7:30-12:00", "13:45-18:00"]

    for time_range in time_ranges_list:  # " 7:30-12:00 "
        try:
            time_range = time_range.strip()
            # time_ranges = "7:30-12:00"
            [start, end] = time_range.split("-")
            # start = "7:30" end = "12:00 "
            start_time = datetime.strptime(start, '%H:%M')
            # datetime does not support time = "24:00", so change time to
            # "00:00" of the next day instead
            if end == "24:00":
                end_time = datetime.strptime("00:00", '%H:%M') \
                           + timedelta(days=1)
            else:
                end_time = datetime.strptime(end, '%H:%M')
            # To handle cases of time ranges "23:00-02:00@
            if end_time < start_time:
                end_time += timedelta(days=1)
            time_open.append([start_time, end_time])

        except ValueError as e:
            logging.debug("Error: %s" % (str(e)))
    return time_open


def search_regex_pattern(day_time_part):
    """ Searches the string, captures the day part, and returns it """

    day_range = re.search(r'^[a-z][a-z]-[a-z][a-z]', day_time_part)
    # day_range = "mo-fr"

    single_day = re.search(r'^[a-z][a-z](?=\s\d)', day_time_part)
    # single_day = "mo"
    # Lookahead assertion to ensure that day range is followed by time range

    non_consecutive = re.search(r'^([a-z][a-z],?\s?)+(?=\d)',
                                day_time_part)
    # non_consecutive = "mo, we, fr "

    time_range_only = re.search(r'^[0-2]?[0-9]:[0-5][0-9]',
                                day_time_part)
    # time_range_only = "7:30-12:00, 13:45-18:00"

    return [day_range, single_day, non_consecutive, time_range_only]


def get_days_open(day_time_part):
    """ Generates a list of the days open and returns it along with the
        corresponding opening time """

    days_open = []
    time_ranges = ""
    [day_range, single_day, non_consecutive, time_range_only] =\
        search_regex_pattern(day_time_part)

    if day_range is not None:
        # 1. day_range = "mo-fr"
        day_range = day_range.group(0)
        [start_day, end_day] = day_range.split("-")
        start_day_index = weekdays.index(start_day)
        end_day_index = weekdays.index(end_day)
        days_open = weekdays[start_day_index:end_day_index + 1]
        # days_open should be ["mo", tu", "we", "th", "fr"]
        # The day range will be followed by the time range
        time_ranges = day_time_part[len(day_range):]

    elif single_day is not None:
        # 2. single_day = "mo"
        single_day = single_day.group(0)
        days_open.append(single_day)
        time_ranges = day_time_part[len(single_day):]

    elif non_consecutive is not None:
        # 3. non_consecutive = "mo, we, fr"
        non_consecutive = non_consecutive.group(0)
        non_consecutive_list = non_consecutive.split(",")
        non_consecutive_list = [x.strip() for x in non_consecutive_list]
        days_open.extend(non_consecutive_list)
        time_ranges = day_time_part[len(non_consecutive):]

    elif time_range_only is not None:
        # 4. time_range_only = "7:30-12:00, 13:45-18:00"
        days_open = weekdays[:]
        time_ranges = day_time_part

    if time_ranges is not None:
        time_open = get_time_open(time_ranges)

    # Contains the days open along with the time ranges
    # Format: [["sa"], [9:00, 12:00], [14:00, 18:00]]
    day_time_list = [days_open]
    day_time_list.extend(time_open)
    
    return day_time_list


def parse_oh_string(oh):
    """ Parses the oh string """

    # Example: oh = "mo-fr 7:30-23:00; sa 09:00-12:00, 14:00-18:00"
    final_oh_list = []
    ''' final_oh_list = [
                         [["mo", tu", "we", "th", "fr"], [7:30, 23:00]]
                         [["sa"], [9:00, 12:00], [14:00, 18:00]]
                         ]
    '''
    days_off_list = []

    # The oh string may still not be OK after checking its validity
    # For example, "mo-fr 7:30-23:00, sa 09:00-12:00, 14:00-18:00"
    # There must be a semi colon instead of the comma before 'Sa'
    oh_string_ok = True
    
    if oh == "24/7":
        final_oh_list.append([weekdays,
                             [datetime.strptime("00:00", '%H:%M'),
                              datetime.strptime("23:59", '%H:%M')]])
        return [final_oh_list, oh_string_ok]

    oh_list = oh.split(";")
    logging.debug("oh_list: " + str(oh_list))
    # oh_list = ["mo-fr 7:30-23:00", "sa 09:00-12:00, 14:00-18:00"]

    # List of possible day_time_part formats:
    # 1. day_time_part = "mo-fr 7:30-12:00, 13:45-18:00"
    # 2. day_time_part = "mo 7:30-12:00, 13:45-18:00"
    # 3. day_time_part = "mo, we 7:30-12:00, 13:45-18:00"
    # 4. day_time_part = "7:30-12:00, 13:45-18:00"
    # 5. day_time_part = "th off"

    for day_time_part in oh_list:

        if day_time_part is not None:
            if "off" in day_time_part:
                # 5. day_time_part = "th off"
                days_off = day_time_part[:day_time_part.index("off") - 1]
                days_off_list = days_off.split(",")
                days_off_list = [x.strip() for x in days_off_list]
            else:
                day_time_list = get_days_open(day_time_part.strip())
                
                # If time range is different for a specific day
                # remove it from the list
                days_open = day_time_list[0]
                time_open = day_time_list[1:]
                for day in days_open:
                    final_oh_list = remove_day(day, final_oh_list)        
                if not time_open:
                    final_oh_list = \
                        "oh string not OK. Check the commas and semi colons."
                    oh_string_ok = False
                    return [final_oh_list, oh_string_ok]
                else:
                    final_oh_list.append(day_time_list)

    # Remove days that are off
    # For eg. oh = "9:00-23:00; sa, su off"
    # final_oh_list should be [[["mo", "tu, "we", "th", "fr"], [9:00, 23:00]]]
    if oh_string_ok:
        for day in days_off_list:
            final_oh_list = remove_day(day, final_oh_list)

    return [final_oh_list, oh_string_ok]


def validate_oh_string(oh):
    """ Check if the oh string is valid, i.e.
        It only contains some valid substrings
        If the oh string contains German words etc. it cannot be parsed
    """

    valid_substrings = weekdays[:]
    valid_substrings.extend(["ph", "off", "24/7", " "])

    # oh = "mo-fr 7:30-23:00; sa 09:00-12:00, 14:00-18:00"
    oh_substrings_list = re.split(r'[\s,:;-]', oh)
    # oh_substrings_list = ["mo", "fr", "7", "30", "23", "00", "sa", "09",
    #                       "00", "12", "00", "14", "00", "18", "00"]

    for substring in oh_substrings_list:
        if not((substring in valid_substrings) or\
               (substring is "") or\
               (re.search(r'^[0-9]?[0-9]$', substring) is not None)):
                logging.debug("invalid word found: " + substring)
                # Opening hours string contains an invalid word
                return False

    return True


def clean_oh_string(oh):
    """ Cleans extra spaces from the oh string """

    # Example: oh = " Mo -Fr    7:30-23: 00 ; Sa 09:00 -12:00 , 14:00-18:00 "
    # 1. Remove leading and trailing spaces
    oh = oh.strip()
    # 2. Remove multiple consecutive spaces
    oh = re.sub(' +', ' ', oh)
    # 3. Remove spaces adjacent to "," ";" "-" and ":"
    oh = re.sub(' ,', ',', oh)
    oh = re.sub(' ;', ';', oh)
    oh = re.sub('\s*-\s*', '-', oh)
    oh = re.sub('\s*:\s*', ':', oh)
    # 4. Convert all characters to lower case for easy comparison
    oh = oh.lower()
    # oh = "mo-fr 7:30-23:00; sa 09:00-12:00, 14:00-18:00"
    return oh


def parse_arguments():
    """ Parses the command line arguments and provides defaults """

    # Get the current day and time
    now = datetime.now()
    current_day_index = now.weekday()
    current_day = weekdays[current_day_index]
    current_time = str(now.hour) + ":" + str(now.minute)
    output_filename = "output_" + current_day + "_" + str(now.hour) + "." +\
                      str(now.minute) + ".csv"

    parser = argparse.ArgumentParser()
    parser.add_argument("oh_file_path",
                        help="Path to the file containing Opening Hours data")
    parser.add_argument("-o",
                        help="Path to the output file.\
                            \nDefault is oh_output.csv",
                        default=output_filename)
    parser.add_argument("--day",
                        help="The day to check. Default is the current day",
                        default=current_day)
    parser.add_argument("--time",
                        help="The time to check. Default is the current time",
                        default=current_time)
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Get a verbose output")
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    oh_file_path = args.oh_file_path
    output_file_path = args.o
    current_day = args.day
    current_time = args.time

    return [oh_file_path, output_file_path, current_day, current_time]


def main():
    """ Calls other functions to evaluate the oh string """

    [oh_file_path, output_file_path, current_day, current_time] =\
        parse_arguments()
        
    logging.debug([oh_file_path, output_file_path, current_day, current_time])

    # Write headers to the output file
    headers = ["oh_clean", "valid/invalid", "open", "oh_list",]
    write_output_to_file(headers, output_file_path)
            
    try:
        with open(oh_file_path, "r") as input_file:
            reader = csv.reader(input_file, delimiter=';')
            next(reader)                          # first row contains headers
            
            for row in reader:
                # This list will be written back to the output file
                write_row = []
                # Get the oh string
                oh = row[3]
                # Clean oh string
                oh_clean = clean_oh_string(oh)
                write_row.append(oh_clean)

                if validate_oh_string(oh_clean):
                    write_row.append("valid")
                    # If the oh string is valid, parse it
                    [final_oh_list, oh_string_ok] = parse_oh_string(oh_clean)

                    if final_oh_list and oh_string_ok:
                        open_now = check_if_open(final_oh_list,
                                                 current_day, current_time)
                        write_row.append("open") if open_now else \
                            write_row.append("closed")
                    else:
                        write_row.append("")

                    write_row.append(final_oh_list)
                else:
                    write_row.append("invalid")
            
                write_output_to_file(write_row, output_file_path)
        logging.info("\nComplete! Please check " + output_file_path)
    except IOError as e:
        sys.exit("An I/O error was encountered:\n %s" % (str(e)))


if __name__ == "__main__":
    main()
