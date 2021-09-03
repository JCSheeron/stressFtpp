#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# stressFtpp.python3
#
import sys
import os  # operating system related
import re  # regular expressions
import pprint  # pretty printer -- helpful for troubleshooting

# TODO: Specify source directory as an argument
# TODO: Specify destination pattern/prefix/suffix and an argument.
# TODO: Handle any number of daily files by creating intermediate files and merging.
# TODO: Add pattern as an argument
# TODO: Specify ftpp path as an argument
# Stress file patten
# Should be in the form: r'(prefix)(datecode)_(daycode)(suffix)'
# Where the prefix can be word characters and may end in an underscore,
# and the suffix may begin with an underscore, but must end with an optional
# underscore and 'raw.csv or Raw.csv'
#
# The below code assumes these capture groups:
# group(1): prefix -- 1 or more 'word' characters followed by an underscore '_'.g: 'CSM1_'
# group(2): datecode, 8 digits -- intended to denote files for a specific day (daily files)
# group(3): daycode 4 digits -- intended to denote partial daily files
# group(4): suffix -- zero or more word characters followed by '_Raw.csv' e.g. '_Raw.csv'
filePattern = re.compile(r'(\w+)(\d{8})_(\d{4})(_?\w*[Rr]aw.csv)')
destFileSuffix = '_ForExport.csv'

# Get a list of all the files matching the pattern.
stressFiles = [f for f in os.listdir('.') if re.match(filePattern, f)]

# Leave if there were no stress files found
if not stressFiles:
    print('There were no files found that match the filter! Nothing to do.')
    sys.exit('No Files Found')

# Iterate thru the list of files and create a dictionary for each datecode (key).
# The dictionay item for each datecode will be another dictionary entry that
# used the file name as the key, and contains the parts of the file name:
# dayBatches = {
#   datecode1: {
#       filename1: {
#           prefix: '...',
#           daycode: ...,
#           suffix: '...'
#           },
#       filename2: {
#           prefix: '...',
#           daycode: ...,
#           suffix: '...'
#       },
#       ...
#   },
#   datecode2: {
#       filename3: {
#           prefix: '...',
#           daycode: ...,
#           suffix: '...'
#           },
#       filename4: {
#           prefix: '...',
#           daycode: ...,
#           suffix: '...'
#       },
#       ...
#   }
#   ...
# }
# This is done to make working by date code easier later on, and so files with different
# suffix or prefix but with the  same date code are still associated with each other.

dayBatches = {}
fileMeta = {}
for fileName in stressFiles:
    # Get the file name capture groups.
    dailyFile = re.match(filePattern, fileName)
    # Populate a file name dict with the file meta data
    fileMeta = {
        'prefix': dailyFile.group(1),
        'daycode': dailyFile.group(3),
        'suffix': dailyFile.group(4)
    }
    # See if the date code is in the dayBatches yet.
    # If it isn't, create a new file name entry in the dayBatches dictionary,
    # otherwise update the entry, which will generally add a new file name entry.
    if dailyFile.group(2) not in dayBatches:
        # New datecode
        # Update the dayBatches dictionary with data about a new file
        dayBatches[dailyFile.group(2)] = {fileName: fileMeta}
    else:
        # The date code is already in the dictionary. Since
        # the file name is unique, the dictionary is getting updated with
        # a new file name (as opposed to an existing entry being changed).
        dayBatches[dailyFile.group(2)].update({fileName: fileMeta})

# pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(dayBatches)

# Now we have a dictionary organized by datecode.
# Iterate thru the dictionary and  For each datecode, build a command string for ftpp.
# Store the command strings in a list and iterate through them later
cmdList = []
for dateCode in dayBatches:
    dayFiles = list(dayBatches[dateCode].keys())
    for count, fileName in enumerate(dayFiles):
        # TODO: Add functionality to have more than 5 files for a day.
        # This requires a change to ftpp.
        # For now, just live with it and print a message.
        if count == 0:
            # The initial file. Create the beginning of the command string.
            # Assume there may or may not be more files.
            ftppCmd = 'ftpp -s ' + fileName
        elif 1 <= count and 4 >= count:
            # Merge the additional files after the first one using the -amn arguments
            ftppCmd = ftppCmd + ' -am' + str(count) + ' ' + fileName
        else:
            # More than 5 files not supported!!!
            print('NOTE NOTE NOTE:')
            print('This program only supports a maximum of 5 files per day.')
            print('The file: ' + fileName + ' was not merged.')

    # At this point the command string contains the source file(s). Append the destination file name.
    # Use the prefix from the first file, the datecode, and the suffix specified in the beginning of this file.
    # print(dayBatches[dateCode])
    # print(dayFiles[0])

    destFileName = dayBatches[dateCode][dayFiles[0]]['prefix'] + \
        str(dateCode) + destFileSuffix
    ftppCmd = ftppCmd + ' ' + destFileName
    cmdList.append(ftppCmd)

# iterate through the command list and call ftpp
for cmd in cmdList:
    print(cmd)
    os.system(cmd)

sys.exit('Test Endpoint')
