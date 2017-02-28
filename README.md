# Opening_Hours
Program to parse the opening hours strings and determine which places are open on a given day and time

# Notes
- The program *opening_hours.py* reads the opening hours strings from a CSV file. The file *opening_hours_of_City_of_Zurich* from Prof Keller's [github gist](https://gist.github.com/sfkeller/c71dcba17bba244bf9e4c9b985517872) has been used for testing. 

- The output file's name is of the format 'output_[day]_[time]'. It consists of the following fields, the cleaned oh string, whether is is valid, whether the place is open at the current day and time (or the day and time entered by the user), and the list containing the opening day and time ranges.

- An excel file *output_tu_13.56.xlsx* has also been attached. It has been conditionally formatted with red for invalid strings and green for some of the different kinds of strings that the program can parse correctly. 

# Usage
```opening_hours.py oh_file_path [-h][-o][--day][--time][-v]```

**Positional Arguments**
- oh_file_path: Path to the *opening_hours_of_City_of_Zurich* file containing the opening hours strings. 

**Optional Arguments**
- -h, --help: Enabling this flag will display the help message and exit.
- -o: Optional argument to specify the output file name. The default is 'output_[day]_[time]'.
- --day: Optional argument to specify the day to check. The default is the current day.
- --time: Optional argument to specify the time to check. The default is the current time.
- -v, --verbose: Enabling this flag will produce a verbose output on the command line.

# Further Enhancements
- Parse opening hours strings containing months.
- Parse opening hours strings of the type "Sa[1]" i.e. if a place is open on the first Saturday of every month.
