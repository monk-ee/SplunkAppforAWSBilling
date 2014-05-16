#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""get_detailed_bill.py: Init for this module."""

__author__ = "monkee"
__license__ = "GPLv3.0"
__version__ = "1.2"
__maintainer__ = "monk-ee"
__email__ = "magic.monkee.magic@gmail.com"
__status__ = "Development"
"""This module cleans up the old reports and csvs
"""
import yaml
from splunk_utilities import *


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


