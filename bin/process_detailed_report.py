#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""process_detailed_bill.py: Init for this module."""

__author__ = "monkee"
__license__ = "GPLv3.0"
__version__ = "2.0.0"
__maintainer__ = "monk-ee"
__email__ = "magic.monkee.magic@gmail.com"
__status__ = "Production"


import yaml
import csv
from splunk_utilities import *
from datetime import datetime

class ProcessDetailedReport:
    logger = ''
    appname = 'SplunkAppforAWSBilling'
    config = ''
    splunk_home = ''
    app_home = ''
    report_date = ''
    linenumber = 0

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

    def process_file(self, key):
        s3_billing_report = str(key[
            'account_number']) + "-aws-billing-detailed-line-items-with-resources-and-tags-" + self.report_date + ".csv"
        try:
            pos_file = "{0}.pos".format(s3_billing_report)
            abs_file_path = os.path.join(self.app_home, 'local', pos_file)
            f = open(abs_file_path, 'r')
            d = csv.DictReader(f, quoting=csv.QUOTE_ALL)
            for row in d:
                if row['object'] == s3_billing_report:
                    self.linenumber = row['latest']
        except IOError, err:
            self.logger.error("MERROR - Position File may not exist: " + str(err))
            return
        self.parse(s3_billing_report)

    def parse(self, report):
        report_path = os.path.join(self.app_home, 'csv', report)
        try:
            ifile = open(report_path, 'rb')
        except IOError, err:
            self.logger.error("MERROR - Report File may not exist: " + str(err))
            return
        except Exception,err:
            self.logger.error("MERROR - Report File may not exist: " + str(err))
            return

        #ok read this file
        reader = csv.reader(ifile)

        #processnewcsv
        processedCSVFileName = str(configurationObject['s3'][
            'account_number']) + "-aws-billing-detailed-line-items-with-resources-and-tags-" + datefilename() + ".processed.csv"
        BILLINGREPORTZIPDIRPROCESSEDCSV = os.path.join(path, 'etc', 'apps', 'SplunkAppforAWSBilling', 'csv',
                                                       processedCSVFileName)

        #more complex file situation - the processed file already exists
        #we only want to append the file differences and throw away the header row
        processedFileExists = True
        try:
            with open(BILLINGREPORTZIPDIRPROCESSEDCSV):
                pass
        except IOError:
            #ok now we need to take another path
            processedFileExists = False

        if processedFileExists == False:
            #process new csv
            print "processing a totally new file"
            processedCSVHandle = open(BILLINGREPORTZIPDIRPROCESSEDCSV, 'wb')

            # go loop go
            rownum = 0
            for row in reader:
                newrow = ""
                if rownum == 0:
                    #format the header row
                    newrow += '"Timestamp",'
                    newrow += '"AccountNumber",'
                    for col in row:
                        newrow += '"' + str(col) + '",'
                    newrow = newrow[:-1]
                    newrow += '\r\n'
                elif row[8] == "":
                     #if the subscriptionid is blank - i dont want that record
                    rownum += 1
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
                    newrow += str(configurationObject['s3']['account_number']) + ', '
                    for col in row:
                        newrow += '"' + str(col) + '",'
                    newrow = newrow[:-1]
                    newrow += '\r\n'
                processedCSVHandle.write(newrow)
                rownum += 1
            #dont shut it you idiot
            processedCSVHandle.close()
        else:
            #process old csv
            #ok at this point we need to count the row total difference
            processedCSVRowCount = sum(1 for row in csv.reader(open(BILLINGREPORTZIPDIRPROCESSEDCSV)))

            #process old csv
            processedCSVHandle = open(BILLINGREPORTZIPDIRPROCESSEDCSV, 'ab')

            # go loop go
            rownum = 0
            for row in reader:
                newrow = ""
                #if the subscriptionid is blank - i dont want that record
                if row[8] == "":
                    rownum += 1
                    continue
                    #format the header row
                if rownum < processedCSVRowCount:
                    #do nothing
                    rownum += 1
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
                    newrow += str(configurationObject['s3']['account_number']) + ', '
                    for col in row:
                        newrow += '"' + str(col) + '",'
                    newrow = newrow[:-1]
                    newrow += '\r\n'
                processedCSVHandle.write(newrow)
                rownum += 1
            #dont shut it you idiot
            processedCSVHandle.close()
        #close that pesky open file
        ifile.close()

if __name__ == "__main__":
    fdr = FetchDetailedReport()