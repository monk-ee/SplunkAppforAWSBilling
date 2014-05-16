#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""get_detailed_bill.py: This module provides an interface to the billing report
in the amazon S3 billing bucket."""

__author__ = "monkee"
__license__ = "GPLv3.0"
__version__ = "1.2"
__maintainer__ = "monk-ee"
__email__ = "magic.monkee.magic@gmail.com"
__status__ = "Development"

import boto
import zipfile
import yaml
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from splunk_utilities import *

#setup error handling file
if not os.path.isfile(ERRORLOGFILE):
        handleERRORLOGFILE = open(ERRORLOGFILE,'w')
else:
        handleERRORLOGFILE = open(ERRORLOGFILE,'ab')

#load configuration
configurationStream = open(AWSCONFIGFILE, 'r')
configurationObject =  yaml.load(configurationStream)

#now set detailed billing file
BILLINGREPORTZIPFILE = os.path.join(path,'etc','apps','SplunkAppforAWSBilling','tmp',str(configurationObject['s3']['account_number'])+'_detailed_billing.zip')

# get a bucket connection
billingBucketConnection = S3Connection(configurationObject['keys'][0]['aws_access_key'], configurationObject['keys'][0]['aws_secret_key'])

#make sure bucket exists before fetching - assume that this stops certain errors
try:
        billingBucket = billingBucketConnection.create_bucket(configurationObject['s3']['billing_bucket'])
except boto.exception.S3ResponseError, emsg1:
        handleERRORLOGFILE.write(timenow()+' S3ResponseError '+str(emsg1[0])+' '+emsg1[1]+' '+str(emsg1[2])+'\n')


#file name
billingFileName = str(configurationObject['s3']['account_number'])+"-aws-billing-detailed-line-items-with-resources-and-tags-"+datefilename()+".csv.zip"
billingBucketHandle = billingBucketConnection.get_bucket(configurationObject['s3']['billing_bucket'])

#key object fudging
billingFileNameKey = Key(billingBucketHandle)
billingFileNameKey.key = billingFileName

#fetch the file to a temporary place on the filesystem
try:
	retrieveFileContents = billingFileNameKey.get_contents_to_filename(BILLINGREPORTZIPFILE)
except boto.exception.S3ResponseError, emsg:
	handleERRORLOGFILE.write(timenow()+' S3ResponseError : '+billingFileName+' '+str(emsg[0])+' '+emsg[1]+' '+str(emsg[2])+'\n')

#now unzip it ready for splunk monitoring
#unzip
zipHandle = zipfile.ZipFile(BILLINGREPORTZIPFILE, mode='r')
for subfile in zipHandle.namelist():
    zipHandle.extract(subfile, BILLINGREPORTCSVDIR)
