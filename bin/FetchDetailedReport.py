#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""get_detailed_bill.py: This module provides an interface to the billing report
in the amazon S3 billing bucket."""

__author__ = "monkee"
__license__ = "GPLv3.0"
__version__ = "2.0.11"
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
import hashlib


class FetchDetailedReport:
    logger = ''
    appname = 'SplunkAppforAWSBilling'
    config = ''
    splunk_home = ''
    app_home = ''
    report_date = ''
    settings = ''

    def __init__(self):
        """
        set up some handy variables and start processing
        :return:
        """
        self.splunk_home = os.environ['SPLUNK_HOME']
        self.app_home = os.path.join(self.splunk_home, 'etc', 'apps', self.appname)
        #get settings
        self.settings = splunk.clilib.cli_common.getConfStanza(appname, "default")
        self.setup_logging()
        self.setup_config()
        self.process_files()

    def set_date(self, dt):
        """
        set the date for this months report here
        :return:
        """
        self.report_date = dt.strftime("%Y-%m")

    def monthdelta(self, date, delta):
        m, y = (date.month+delta) % 12, date.year + ((date.month)+delta-1) // 12
        if not m: m = 12
        d = min(date.day, [31,
                           29 if y%4==0 and not y%400==0 else 28,31,30,31,30,31,31,30,31,30,31][m-1])
        return date.replace(day=d,month=m, year=y)

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
        """

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
        OK so here is the mod, at this point I am going to go and get 12 months worth of files
        :return:
        """
        #set this value, then reset it from config file - saves everything going boing
        # https://github.com/monk-ee/SplunkAppforAWSBilling/issues/12
        history = 12
        try:
            history = int(self.config['history'])
        except KeyError, kerr:
            self.logger.error("Failed to find history stanza from the configuration file aws.yaml. This is a known "
                              "upgrade problem, see README for fix. Fudging value to 12 months for now,"
                              "Error Details: " + str(kerr))

        for key in self.config['accounts']:
            #so here we look back at least 12 months see aws.yaml for current setting
            #calculate now back to the history
            for month in range(-history, 0):
                self.set_date(self.monthdelta(datetime.now(), month))
                self.fetch_file(key)

    def fetch_file(self, key):
        """
        @todo I want to check the etag header so i dont download files i already have
        for key_val in rs_keys:
            print key_val, key_val.etag

        so at this point we will need to have individual zip files so we can check md5sum and ensure we dont keep
        pulling down the same file unnecessarily - this could get quite big - but hey
        :param key:
        :return:
        """
        zipped_report = os.path.join(self.app_home ,'tmp' , str(key['account_number']) + '_'
                                     + str(self.report_date) + '_' + 'detailed_billing.zip')

        """
        check file exists; if so calculate it's md5sum
        """
        filemd5sum = None
        try:
            hash = hashlib.md5()
            with open(zipped_report, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash.update(chunk)
            filemd5sum = hash.hexdigest()
        except:
            self.logger.error("File may not exist, or permissions could be wrong. This is Ok if the file really "
                              "doesn't exist")

        try:
            conn = S3Connection(
                key['aws_access_key'],
                key['aws_secret_key'],
                proxy=self.settings['proxy_url'],
                proxy_port=self.settings['proxy_port'],
                proxy_user=self.settings['proxy_user'],
                proxy_pass=self.settings['proxy_pass'])
            s3_billing_report = str(key['account_number']) \
                                + "-aws-billing-detailed-line-items-with-resources-and-tags-" \
                                + str(self.report_date) + ".csv.zip"
            #check the billing buckets name is actually set
            if key['billing_bucket'] == "":
                self.logger.error("Bucket Name needs to be set in the aws.yaml local file.")
                raise SystemExit
            bucket = conn.get_bucket(key['billing_bucket'])
            """
            I think it is here that I can check the md5 sum
            """
            etag = None
            try:
                #oh bugger using try catch for flow control - yuck
                #guess how this doesnt work - if it errors because the key is non-existent you hide the problem
                # you ideeeeot stimpy
                file_key = bucket.get_key(s3_billing_report)
                etag = file_key.etag
                #the etag seems to contain quotes for some reason
                if etag.startswith('"') and etag.endswith('"'):
                    etag = etag[1:-1]
            except boto.exception.S3ResponseError, s3err:
                #so take that - the file must not exist in the bucket - bail here
                self.logger.error("404 - nosuchkey - because the file DOES NOT exist, nobody panic this is an ok "
                                  "error: " + str(s3err))
                return
            except:
                #I think any other errors are recoverable - I could be wrong
                pass

            if filemd5sum is not None and filemd5sum == etag:
                #stop here - we already have this file we can forget continuing wasting bandwidth
                return
            else:
                #so this is the point it breaks from the error we failed to capture in the try/catch above
                #ok so use the exception properly and return above ---->
                # https://github.com/monk-ee/SplunkAppforAWSBilling/issues/11
                FileObject = Key(bucket)
                FileObject.key = s3_billing_report
                FileObject.get_contents_to_filename(zipped_report)
                # wunzip the file
                try:
                    zip = zipfile.ZipFile(zipped_report, mode='r')
                    for subfile in zip.namelist():
                        zip.extract(subfile, os.path.join(self.app_home, 'csv'))
                except Exception, err:
                    self.logger.error("Could not unzip report archive: " + str(err))
                    raise SystemExit
        except boto.exception.S3ResponseError, emsg:
            self.logger.error("Failed to lookup the bucket name in s3: " + str(emsg))
            raise SystemExit
        except Exception, err:
            self.logger.error("No idea why this went wrong: " + str(err))
            raise SystemExit


if __name__ == "__main__":
    fdr = FetchDetailedReport()