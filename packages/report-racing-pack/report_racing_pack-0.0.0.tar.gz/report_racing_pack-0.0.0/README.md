# Racing report


**Installation**

To use this package in your project, use dependency manager to install it:

`pip install report-racing-pack==0.0.1
`

**Usage**

The result of use this program - reads logs of statistics from the specified catalog, and returns statistics on the result of the best round in the qualification

arguments

1) --folder argument "folder" should be a name of folder where placed files with datas
2) --asc sort by first to last, asc is default
3) --desc sort by last to first
4) --driver information about the pilot, enter the name in '  '


python -m log_report <path to dir with logs> --desc

python -m log_report <path to dir with logs> --driver <name driver in "">

Documentation function and classes
the package has 2 classes and 2 function

args_parser()
add arguments and parse, return namespace with them

parse_call(args_cm=<namespace_args>)
takes namespace of args from previous func and call something it depends what args were parsed

class Log

obj Log parameters path

Log.read_data

read data from files in path

Log.get_logs

validate for usage and return three lists with abbreviations start_time and end_time

class Report

obj Report parameters abbr_list, start_list, end_list

Report.get_diff calculate difference

between start and end time

Report.concatenate_sort_data

concatenate diff time with abbr and then sort it

Report.output

print statistic about all drivers

Report.driver

takes name and get statistic about driver

Report.solo_output

print statistic about driver work with previous method