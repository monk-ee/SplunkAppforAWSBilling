#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
FetchOlderReport.py: This module provides an interface to the billing report
in the amazon S3 billing bucket

usage: FetchOlderReport.py [-h] [-d] year month user password

A utility for fetching/downloading older report files into SplunkAppforAWSBilling.

Be very careful, do not fetch the current months data - you will cause a double up of
records in the splunk index.


To be used in conjunction with ProcessOlderReport.py

positional arguments:
    year          The year in this format: 2014 (YYYY)
    month         The month in this format: 05 (MM)
    user          The username for a splunk user.
    password      The password for a splunk user

optional arguments:
    -h, --help    show this help message and exit
    -d, --dryrun  Fake runs for testing purposes.
    -p, --port          The port to post events to.
    -s, --serverport    The server to post events to.
  """

__author__ = "monkee"
__license__ = "GPLv3.0"
__version__ = "2.0.7"
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
import argparse


class FetchOlderReport:
    logger = ''
    appname = 'SplunkAppforAWSBilling'
    config = ''
    splunk_home = ''
    app_home = ''
    report_date = ''
    settings = ''

    def __init__(self, obj):
        """

        :param obj:
        :return:
        """
        self.splunk_home = os.environ['SPLUNK_HOME']
        self.app_home = os.path.join(self.splunk_home, 'etc', 'apps', self.appname)
        #get settings
        self.settings = splunk.clilib.cli_common.getConfStanza(appname, "default")
        self.set_date(obj)
        self.setup_logging()
        self.setup_config()
        self.process_files()


    def set_date(self, arg):
        """

        :param arg:
        :return:
        """
        self.report_date = str(arg.year) + '-' + str(arg.month).zfill(2)

    # Define the logging function
    def setup_logging(self):
        """

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
        splunk.setupSplunkLogger(self.logger, LOGGING_DEFAULT_CONFIG_FILE, LOGGING_LOCAL_CONFIG_FILE,
                                 LOGGING_STANZA_NAME)


    def setup_config(self):
        """

        :return:
        """
        try:
            aws_key_file = os.path.join(self.app_home, 'local', 'aws.yaml')
            config = open(aws_key_file, 'r')
            self.config = yaml.load(config)
        except IOError, err:
            self.logger.error("Failed to load configuration file aws.yaml: " + str(err))
            raise SystemExit


    def process_files(self):
        """

        :return:
        """
        for key in self.config['accounts']:
            self.fetch_file(key)


    def fetch_file(self, key):
        """

        :param key:
        :return:
        """
        zipped_report = os.path.join(self.app_home, 'tmp', str(key['account_number']) + '_detailed_billing.zip')
        try:
            conn = S3Connection(
                key['aws_access_key'],
                key['aws_secret_key'],
                proxy=self.settings['proxy_url'],
                proxy_port=self.settings['proxy_port'],
                proxy_user=self.settings['proxy_user'],
                proxy_pass=self.settings['proxy_pass'])
            s3_billing_report = str(key[
                'account_number']) + "-aws-billing-detailed-line-items-with-resources-and-tags-" + self.report_date + ".csv.zip"
            bucket = conn.get_bucket(key['billing_bucket'])
            FileObject = Key(bucket)
            FileObject.key = s3_billing_report
            FileObject.get_contents_to_filename(zipped_report)
        except boto.exception.S3ResponseError, emsg:
            self.logger.error("Failed to get file from s3: " + str(emsg))
            raise SystemExit
        except Exception, err:
            self.logger.error("No idea why this went wrong: " + str(err))
            raise SystemExit
        try:
            zip = zipfile.ZipFile(zipped_report, mode='r')
            for subfile in zip.namelist():
                zip.extract(subfile, os.path.join(self.app_home, 'csv'))
        except Exception, err:
            self.logger.error("Could not unzip report archive: " + str(err))


if __name__ == "__main__":
    # grab the arguments when the script is ran
    parser = argparse.ArgumentParser(
        description='A utility for fetching older report files into splunk for processing. '
                    'Be very careful, do not fetch the current months data - you will cause a double up of records in the splunk index.')
    parser.add_argument('-d', '--dryrun', action='store_true', default=False, help='Fake runs for testing purposes.')
    parser.add_argument('year', type=int, help='The year in this format: 2014 (YYYY)')
    parser.add_argument('month', type=int, help='The month in this format: 05 (MM)')
    args = parser.parse_args()
    foldr = FetchOlderReport(args)