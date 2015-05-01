#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""get_detailed_bill.py: This module provides an interface to the billing report
in the amazon S3 billing bucket."""

__author__ = "monkee"
__license__ = "GPLv3.0"
__version__ = "2.0.0"
__maintainer__ = "monk-ee"
__email__ = "magic.monkee.magic@gmail.com"
__status__ = "Production"

import boto
import zipfile
import yaml
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from splunk_utilities import *
import splunk.clilib.cli_common
import logging, logging.handlers
import splunk
import os
from datetime import datetime,timedelta


class FetchDetailedReport():
    logger = ''
    appname = 'SplunkAppforAWSBilling'
    config = ''
    splunk_home = ''
    app_home = ''
    report_date = ''

    def __init__(self):
        self.splunk_home = os.environ['SPLUNK_HOME']
        self.app_home = os.path.join(self.splunk_home, 'etc', 'apps', self.appname)
        self.set_date()
        self.setup_logging()
        self.setup_config()
        self.process_files()


    def set_date(self):
        dt = datetime.now()
        self.report_date = dt.strftime("%Y-%m")

    # Define the logging function
    def setup_logging(self):
        self.logger = logging.getLogger('splunk.SplunkAppforAWSBilling')
        LOGGING_DEFAULT_CONFIG_FILE = os.path.join(self.splunk_home, 'etc', 'log.cfg')
        LOGGING_LOCAL_CONFIG_FILE = os.path.join(self.splunk_home, 'etc', 'log-local.cfg')
        LOGGING_STANZA_NAME = 'python'
        LOGGING_FILE_NAME = "SplunkAppforAWSBilling.log"
        BASE_LOG_PATH = os.path.join('var', 'log', 'splunk')
        LOGGING_FORMAT = "%(asctime)s %(levelname)-s\t%(module)s:%(lineno)d - %(message)s"
        splunk_log_handler = logging.handlers.RotatingFileHandler(os.path.join(self.splunk_home, BASE_LOG_PATH, LOGGING_FILE_NAME), mode='a')
        splunk_log_handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
        self.logger.addHandler(splunk_log_handler)
        splunk.setupSplunkLogger(self.logger, LOGGING_DEFAULT_CONFIG_FILE, LOGGING_LOCAL_CONFIG_FILE, LOGGING_STANZA_NAME)


    def setup_config(self):
        try:
            aws_key_file = os.path.join(self.app_home, 'local', 'aws.yaml')
            config = open(aws_key_file, 'r')
            self.config =  yaml.load(config)
        except IOError, err:
            self.logger.error("Failed to load configuration file aws.yaml: " + str(err))
            raise SystemExit


    def process_files(self):
        for key in self.config['accounts']:
            self.fetch_file(key)


    def fetch_file(self, key):

        zipped_report = os.path.join(self.app_home ,'tmp' , str(key['account_number']) + '_detailed_billing.zip')
        try:
            conn = S3Connection(key['aws_access_key'], key['aws_secret_key'])
            s3_billing_report = str(key['account_number']) + "-aws-billing-detailed-line-items-with-resources-and-tags-" + self.report_date + ".csv.zip"
            bucket = conn.get_bucket(key['billing_bucket'])
            FileObject = Key(bucket)
            FileObject.key = s3_billing_report
            FileObject.get_contents_to_filename(zipped_report)
        except boto.exception.S3ResponseError, emsg:
            self.logger.error("Failed to get file from s3: " + str(emsg.reason))
            raise SystemExit
        except Exception, err:
            self.logger.error("No idea why this went wrong: " + str(err.reason))
            raise SystemExit

        zip = zipfile.ZipFile(zipped_report, mode='r')
        for subfile in zip.namelist():
            zip.extract(subfile, os.path.join(self.app_home, 'csv'))

if __name__ == "__main__":
    fdr = FetchDetailedReport()