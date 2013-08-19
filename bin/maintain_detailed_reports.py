#!/usr/bin/python
__author__ = 'monk-ee'

"""This module cleans up the old reports and csvs
"""
import os
import sys
import calendar
import datetime
import time
import zipfile
import yaml
import csv
import splunk_utilities
from splunk_utilities import *
from datetime import datetime


#setup error handling file
if not os.path.isfile(ERRORLOGFILE):
    handleERRORLOGFILE = open(ERRORLOGFILE, 'w')
else:
    handleERRORLOGFILE = open(ERRORLOGFILE, 'ab')

#load configuration
configurationStream = open(AWSCONFIGFILE, 'r')
configurationObject = yaml.load(configurationStream)

#now set detailed billing file
BILLINGREPORTZIPFILE = os.path.join(path, 'etc', 'apps', 'SplunkAppforAWSBilling', 'tmp',
                                    str(configurationObject['s3']['account_number']) + 'detailed_billing.zip')

#old file names
oldBillingFileName = str(configurationObject['s3'][
    'account_number']) + "-aws-billing-detailed-line-items-with-resources-and-tags-" + subtract_one_month_datefilename() + ".csv"
oldBillingProcessedFileName = str(configurationObject['s3'][
    'account_number']) + "-aws-billing-detailed-line-items-with-resources-and-tags-" + subtract_one_month_datefilename() + ".processed.csv"

#now path it
BILLINGREPORTCSVOLDFILE = os.path.join(path, 'etc', 'apps', 'SplunkAppforAWSBilling', 'csv',oldBillingFileName)
BILLINGREPORTCSVOLDPROCESSEDFILE = os.path.join(path, 'etc', 'apps', 'SplunkAppforAWSBilling', 'csv',oldBillingProcessedFileName)

#now delete them try catch
try:
    os.remove(BILLINGREPORTCSVOLDFILE)
except OSError:
    pass
try:
    os.remove(BILLINGREPORTCSVOLDPROCESSEDFILE)
except OSError:
    pass


