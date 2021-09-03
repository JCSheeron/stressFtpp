#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
import os  # operating system related
import re  # regular expressions

# Stress file patten
filePattern = re.compile(r'CSM_(\d{8})_(\d{4}).csv')

# get a list of all the files matching the pattern
files = [f for f in os.listdir('.') if re.match(filePattern, f)]
print(files)
