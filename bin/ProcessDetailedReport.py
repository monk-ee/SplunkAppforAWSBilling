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
    LineItem: !!python/long '16467'}

    This file branches as of ab16476f08071f9da1492f8df5a459374586a452 to output a yaml format rather than lines from
    the csv.
    The dashboards will need to understand estimated versus actual

"""

__author__ = "monkee"
__license__ = "GPLv3.0"
__version__ = "2.0.10"
__maintainer__ = "monk-ee"
__email__ = "magic.monkee.magic@gmail.com"
__status__ = "Production"


import yaml
import csv
import logging, logging.handlers
import splunk
from datetime import datetime
import os
import json
import base64

#we would rather use cpickle but if it's not there that is ok too
try:
    import cPickle as pickle
except:
    import pickle


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

    def filesafe(self, name):
        """
        just pulled this out because i was not sure the best way to make a filename safe
        this could be anything really - i chose this way
        :param name:
        :return:
        """
        return base64.urlsafe_b64encode(name)

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
            #so here we look back at least 12 months see aws.yaml for current setting
            #calculate now back to the history
            for month in range(-int(self.config['history']), 0):
                self.set_date(self.monthdelta(datetime.now(), month))
                self.process_file(key)

    def process_file(self, key):
        """
        Just a layer to clarify the processing chain for multiple accounts
        :param key:
        :return:
        """
        s3_billing_report = str(key[
            'account_number']) + "-aws-billing-detailed-line-items-with-resources-and-tags-" + self.report_date + ".csv"
        #ok go go go go go go go
        self.parse(s3_billing_report)


    def load_position(self, s3_billing_report, product):
        """
        :param s3_billing_report: this is the calculated name of the report file based on account number and month/year
        :return:
        """
        try:
            pos_file = "{0}.{1}.p".format(s3_billing_report, self.filesafe(product))
            abs_file_path = os.path.join(self.app_home, 'local', pos_file)
            self.position[product] = pickle.load( open( abs_file_path, "rb" ) )
        except IOError, err:
            # so this file doesnt exist lets set it up
            self.position.update({product: set()})
            pass
        return

    def game_set_and_match(self, report, newjson):
        """
        this method does all the hard work of tracking whether a record has been imported or not
        we keep sets of recordid's around to do a comparison on - seems the only way to do it
        with some sanity
        :param report:
        :param newjson:
        :return:
        """
        #first define the set
        product = newjson['ProductName']
        try:
            self.position[product]
        except:
            #go fetch
            self.load_position(report, product)
        # now let's check it
        if newjson['RecordId'] in self.position[product]:
            #ok we got this one move on
            return
        else:
            #ok add us in dano
            self.position[product].add(newjson['RecordId'])
            #there seems to be an issue around this to do with the usage start date
            # really existing UsageStartDate 'fudge' misfiring #5
            #it also seems that the amazon format ensures this is no longer so
            #disabling this for now
            if newjson['UsageStartDate'] == '':
                self.logger.error("MERROR - This field should never be blank here! Check Record Line: " +
                                  str(newjson['RecordId']))
                return

            self.output_json(newjson)

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

        #let's reset headers - just in case new custom tags have been added in the interim
        headers = ""

        #time to build a dictionary of this stuff
        for row in reader:
            newjson = {}
            if reader.line_num == 1:
                headers = row
                continue
            elif row[3] != "LineItem":
                #(Use LineItem instead) - throw it away
                continue
            elif row[5] == 0:
                #throw it away it is gst - don't want it right now - or ever really - there is currency conversion mess
                # associated with this
                continue
            elif row[5] == "":
                #ha this breaks lots of stuff to do with my set logic - so no no no
                continue
            elif row[4] == "":
                #so these are calculated aws support costs but not used unless you have broken the thresholds
                #then they get recordids because they are chargeable - throw them away if they are blank
                continue
            else:
                count = 0
                for col in headers:
                    if row[count] != '':
                        newjson[col] = row[count]
                    count=count+1
                self.game_set_and_match(report, newjson)
        self.write_position(report)

    def output_json(self, newjson):
        """
        just pushed this out to a method that can be modified independently
        :param newjson:
        :return:
        """
        print(json.dumps(newjson, encoding="utf-8", ensure_ascii=True))


    def write_position(self, report):
        """
        This function writes the json positional file ;)
        :param report:
        :return: writes out a positional file to the filesystem
        """
        for product in self.position.iterkeys():
            try:
                pos_file = "{0}.{1}.p".format(report, self.filesafe(product))
                abs_file_path = os.path.join(self.app_home, 'local', pos_file)
                pickle.dump( self.position[product], open( abs_file_path, "wb" ) )
            except IOError, err:
                self.logger.error("ERROR - Position could not be written; this is bad because we now get \
                                  duplicates : " + str(err))
                raise SystemExit
        #it would probably behoove us to unset this value
        self.position = {}


if __name__ == "__main__":
    pdr = ProcessDetailedReport()