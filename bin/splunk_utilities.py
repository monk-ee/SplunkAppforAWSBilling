#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""splunk_utilities.py: Init for this module."""

__author__ = "monkee"
__license__ = "GPLv3.0"
__version__ = "2.0.8"
__maintainer__ = "monk-ee"
__email__ = "magic.monkee.magic@gmail.com"
__status__ = "Production"

"""This module provides some handy utilities
"""
import os
import time
from datetime import datetime,timedelta

#path and file stuff
path = os.environ["SPLUNK_HOME"]
appname = 'SplunkAppforAWSBilling'
BILLINGREPORTZIPDIR = os.path.join(path, 'etc', 'apps', appname, 'tmp')
BILLINGREPORTCSVDIR = os.path.join(path, 'etc', 'apps', appname, 'csv')
AWSCONFIGFILE = os.path.join(path, 'etc', 'apps', appname, 'local', 'aws.yaml')
ERRORLOGFILE = os.path.join(path, 'etc', 'apps', appname, 'log', 'detailed_bill_errors.txt')

#time related malarkey for guessing last months billing file name - i mean building
def datefilename():
    dt = datetime.now()
    return dt.strftime("%Y-%m")

def subtract_one_month_datefilename():
    "just a timenow function to minimize code repeats"
    dt = datetime.now()
    dt1 = dt.replace(day=1)
    dt2 = dt1 - timedelta(days=1)
    dt3 = dt2.replace(day=1)
    return dt3.strftime("%Y-%m")

def timenow():
    "just a timenow function to minimize code repeats"
    return time.strftime("%m-%d-%Y %H:%M:%S", time.localtime()) + " " + time.strftime("%z")