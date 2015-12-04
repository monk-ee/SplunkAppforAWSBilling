#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""MaintainDetailedReports.py: clean up old reports."""

__author__ = "monkee"
__license__ = "GPLv3.0"
__version__ = "2.0.6"
__maintainer__ = "monk-ee"
__email__ = "magic.monkee.magic@gmail.com"
__status__ = "Production"

import yaml
from splunk_utilities import *


import yaml
import csv
from splunk_utilities import *
import splunk.clilib.cli_common
import logging, logging.handlers
import splunk
from datetime import datetime
import os
import json


class MaintainDetailedReports:
    logger = ''
    appname = 'SplunkAppforAWSBilling'
    config = ''
    splunk_home = ''
    app_home = ''
    report_date = ''
    linenumber = 0
    position = {}

    def __init__(self):
        """
        Set some class variables for later use and kick off the processing chain
        :return:
        """
        self.splunk_home = os.environ['SPLUNK_HOME']
        self.app_home = os.path.join(self.splunk_home, 'etc', 'apps', self.appname)
        self.setup_logging()
        self.setup_config()
        self.process_files()


    def set_date(self, date):
        """
        set the date for this months report here
        :return:
        """
        self.report_date = date.strftime("%Y-%m")

    def monthdelta(self, date, delta):
        m, y = (date.month+delta) % 12, date.year + ((date.month)+delta-1) // 12
        if not m: m = 12
        d = min(date.day, [31,
                           29 if y%4==0 and not y%400==0 else 28,31,30,31,30,31,31,30,31,30,31][m-1])
        return date.replace(day=d,month=m, year=y)

    # Define the logging function
    def setup_logging(self):
        """
        Just set up some splunky logging goodness.
        :return:
        """
        self.logger = logging.getLogger('splunk.SplunkAppforAWSBilling')
        LOGGING_DEFAULT_CONFIG_FILE = os.path.join(self.splunk_home, 'etc', 'log.cfg')
        LOGGING_LOCAL_CONFIG_FILE = os.path.join(self.splunk_home, 'etc', 'log-local.cfg')
        LOGGING_STANZA_NAME = 'python'
        LOGGING_FILE_NAME = "SplunkAppforAWSBilling.log"
        BASE_LOG_PATH = os.path.join('var', 'log', 'splunk')
        LOGGING_FORMAT = "%(asctime)s %(levelname)-s\t%(module)s:%(lineno)d - %(message)s"
        splunk_log_handler = logging.handlers.RotatingFileHandler(
            os.path.join(self.splunk_home, BASE_LOG_PATH, LOGGING_FILE_NAME), mode='a')
        splunk_log_handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
        self.logger.addHandler(splunk_log_handler)
        splunk.setupSplunkLogger(
            self.logger, LOGGING_DEFAULT_CONFIG_FILE, LOGGING_LOCAL_CONFIG_FILE, LOGGING_STANZA_NAME)

    def setup_config(self):
        """
        This just loads the yaml that contains the configuration required to calculate the report file name(s)
        :return:
        """
        try:
            aws_key_file = os.path.join(self.app_home, 'local', 'aws.yaml')
            config = open(aws_key_file, 'r')
            self.config =  yaml.load(config)
        except IOError, err:
            self.logger.error("Failed to load configuration file aws.yaml: " + str(err))
            raise SystemExit


    def process_files(self):
        """
        Adding some support for multiple files and accounts - for aggregation
        :return:
        """
        for key in self.config['accounts']:
            for month in range(-24, -12):
                self.set_date(self.monthdelta(datetime.now(), month))
                self.process_file(key)

    def process_file(self, key):
        #now set detailed billing file
        BILLINGREPORTZIPFILE = os.path.join(path, 'etc', 'apps', 'SplunkAppforAWSBilling', 'tmp',
                                            str(key['account_number']) + '_' + self.report_date + '_'
                                            + 'detailed_billing.zip')

        #old file names
        oldBillingFileName = str(key[
            'account_number']) + "-aws-billing-detailed-line-items-with-resources-and-tags-" + self.report_date + ".csv"

        #now path it
        BILLINGREPORTCSVOLDFILE = os.path.join(path, 'etc', 'apps', 'SplunkAppforAWSBilling', 'csv',oldBillingFileName)

        #now delete them try catch
        try:
            os.remove(BILLINGREPORTCSVOLDFILE)
            os.remove(BILLINGREPORTZIPFILE)
        except OSError:
            pass


if __name__ == "__main__":
    mdr = MaintainDetailedReports()

