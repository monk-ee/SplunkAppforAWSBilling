#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""process_detailed_bill.py: Init for this module.

    The purpose of this script is to parse the csv report file into a stream that can be consumed by splunk. It has a
    concept of file position stored in a yaml position file. It uses this file to determine what parts of the file it
    has processed.

    This is due to the file changing in the S3 bucket with additional LineItems.

    Note: a merror is a recoverable error, it may not be critical to the functioning or parsing of the script

    We use the record type to determine position within the csv also whether an item is billable:
    RecordType
      - LineItem
      - Rounding
      - InvoiceTotal
      - AccountTotal
      - StatementTotal

    This is stored in a yaml file like so:

"""

__author__ = "monkee"
__license__ = "GPLv3.0"
__version__ = "2.0.0"
__maintainer__ = "monk-ee"
__email__ = "magic.monkee.magic@gmail.com"
__status__ = "Production"


import yaml
import csv
from splunk_utilities import *
import splunk.clilib.cli_common
import logging, logging.handlers
import splunk
from datetime import datetime
import os


class ProcessDetailedReport:
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
        self.set_date()
        self.setup_logging()
        self.setup_config()
        self.process_files()


    def set_date(self):
        """
        We calculate the month we are in just here.
        :return:
        """
        dt = datetime.now()
        self.report_date = dt.strftime("%Y-%m")

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
            self.process_file(key)

    def process_file(self, key):
        """
        Just a layer to clarify the processing chain for multiple accounts
        :param key:
        :return:
        """
        s3_billing_report = str(key[
            'account_number']) + "-aws-billing-detailed-line-items-with-resources-and-tags-" + self.report_date + ".csv"
        #reset this or stuff will break
        self.position = {}
        #ok go go go go go go go
        self.load_position(s3_billing_report)
        self.parse(s3_billing_report)


    def load_position(self, s3_billing_report):
        """
        :param s3_billing_report: this is the calculated name of the report file based on account number and month/year
        :return:
        """
        try:
            pos_file = "{0}.yaml".format(s3_billing_report)
            abs_file_path = os.path.join(self.app_home, 'local', pos_file)
            file = open(abs_file_path, 'r')
            self.position = yaml.load(file)
        except IOError, err:
            #self.logger.error("MERROR - Position File may not exist: " + str(err))
            #we dont care about this really - will happen first time a file is seen
            pass
        return

    def parse(self, report):
        """
        In this function we are going to process the file, we will do this based on the positional elements of a
        previous run. It will load the file each time but hopefully not waste too much time or resources doing this.
        :param report: this is the calculated name of the report file based on account number and month/year
        :return:
        """
        report_path = os.path.join(self.app_home, 'csv', report)
        try:
            ifile = open(report_path, 'rb')
        except IOError, err:
            self.logger.error("MERROR - Report File does not exist (IO): " + str(err))
            return
        except Exception,err:
            self.logger.error("MERROR - Report File does not exist (General): " + str(err))
            return

        #ok read the report file in
        reader = csv.reader(ifile)

        # we looooooooop here and do something re-org so splunk understands it better (that's the theory ;))
        # ps you can use csv.line_number instead of counting - it's better for the environment
        # you need to pop the positional logic in this loop if row.line_num < self.postion['lineitem']
        if len(self.position.keys()) == 0:
            # ok it's blank so it hasn't been set, let's set it
            print('blank set')
            self.position['LineItem'] = 0

        #let's process
        for row in reader:
            newrow = ""
            if  row[3] != "LineItem":
                #(Use LineItem instead) - also skips header - yay!
                continue
            elif reader.line_num <= self.position['LineItem']:
                #we have already processed these lines throw them away
                continue
            else:
                if row[15] != "":
                    try:
                        rowdate = datetime.strptime(row[15], '%Y-%m-%d %H:%M:%S')
                        newdate = rowdate.strftime("%b %d %Y %I:%M:%S %p %z")
                    except Exception:
                        sys.exc_clear()
                        falsedate = datefilename() + "-01 00:00:00"
                        rowdate = datetime.strptime(falsedate, '%Y-%m-%d %H:%M:%S')
                        newdate = rowdate.strftime("%b %d %Y %I:%M:%S %p %z")
                else:
                    falsedate = datefilename() + "-01 00:00:00"
                    rowdate = datetime.strptime(falsedate, '%Y-%m-%d %H:%M:%S')
                    newdate = rowdate.strftime("%b %d %Y %I:%M:%S %p %z")

                newrow = str(newdate) + ', '
                for col in row:
                    newrow += '"' + str(col) + '",'
                newrow = newrow[:-1]
                # set the last lineitem here
                self.position['LineItem'] = reader.line_num
                #we push this to standard out now for the parser to get
            print(newrow)
        #write positional info
        self.write_position(report)

    def write_position(self, report):
        """
        This function writes the json positional file ;)
        :param report:
        :return: writes out a positional file to the filesystem
        """
        try:
            pos_file = "{0}.yaml".format(report)
            abs_file_path = os.path.join(self.app_home, 'local', pos_file)
            with open(abs_file_path, 'w') as outfile:
                outfile.write( yaml.dump(self.position, default_flow_style=True) )
        except IOError, err:
            self.logger.error("ERROR - Position could not be written; this is bad because we now get \
                              duplicates : " + str(err))
            raise SystemExit

if __name__ == "__main__":
    pdr = ProcessDetailedReport()