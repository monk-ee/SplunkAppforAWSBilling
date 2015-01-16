#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""get_detailed_bill.py: This module provides an interface to the billing report
in the amazon S3 billing bucket."""

__author__ = "monkee"
__license__ = "GPLv3.0"
__version__ = "2.0.0"
__maintainer__ = "monk-ee"
__email__ = "magic.monkee.magic@gmail.com"
__status__ = "Development"

import boto
import zipfile
import yaml
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from splunk_utilities import *


class FetchReport():
    logHandle = ""
    configurationObject = ""

    def __init__(self):
        self.setup()
        self.load()
        self.fetch()

    def setup(self):
        #setup error handling file
        if not os.path.isfile(ERRORLOGFILE):
            self.logHandle = open(ERRORLOGFILE,'w')
        else:
            self.logHandle = open(ERRORLOGFILE,'ab')

    def load(self):
        #load configuration
        configurationStream = open(AWSCONFIGFILE, 'r')
        self.configurationObject =  yaml.load(configurationStream)

    def fetch(self):
        for account in self.configurationObject['s3']:
            #now set detailed billing file
            BILLINGREPORTZIPFILE = os.path.join(path,'etc','apps','SplunkAppforAWSBilling','tmp',str(account['account']['account_number'])+'_detailed_billing.zip')
            # get a bucket connection
            billingBucketConnection = S3Connection(account['account']['aws_access_key'], account['account']['aws_secret_key'])
            #make sure bucket exists before fetching - assume that this stops certain errors
            try:
                billingBucket = billingBucketConnection.get_bucket(account['account']['billing_bucket'])
            except boto.exception.S3ResponseError, emsg1:
                self.logHandle.write(timenow()+' S3ResponseError '+str(emsg1[0])+' '+emsg1[1]+' '+str(emsg1[2])+'\n')
            #file name
            billingFileName = str(account['account']['account_number'])+"-aws-billing-detailed-line-items-with-resources-and-tags-"+datefilename()+".csv.zip"
            billingBucketHandle = billingBucketConnection.get_bucket(account['account']['billing_bucket'])
            #key object fudging
            billingFileNameKey = Key(billingBucketHandle)
            billingFileNameKey.key = billingFileName
            #fetch the file to a temporary place on the filesystem
            try:
                retrieveFileContents = billingFileNameKey.get_contents_to_filename(BILLINGREPORTZIPFILE)
            except boto.exception.S3ResponseError, emsg:
                self.logHandle.write(timenow()+' S3ResponseError : '+billingFileName+' '+str(emsg[0])+' '+emsg[1]+' '+str(emsg[2])+'\n')
            #now unzip it ready for splunk monitoring
            #unzip
            zipHandle = zipfile.ZipFile(BILLINGREPORTZIPFILE, mode='r')
            for subfile in zipHandle.namelist():
                zipHandle.extract(subfile, BILLINGREPORTCSVDIR)


if __name__ == "__main__":
    fr = FetchReport()