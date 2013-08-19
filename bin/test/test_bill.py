#!/usr/bin/python
# get_detailed_bill.py

"""This module provides an interface to the billing report
in the amazon S3 billing bucket.
"""
import os
import sys
import boto.ec2
import calendar
import datetime
import time
import boto
import zipfile
import yaml
from boto.s3.connection import S3Connection
from datetime import datetime
from boto.s3.key import Key

#path and file stuff
path = os.environ["SPLUNK_HOME"]
BILLINGREPORTZIPFILE = os.path.join(path,'etc','apps','SplunkAppforAWS','tmp','detailed_billing.zip')
BILLINGREPORTZIPDIR = os.path.join(path,'etc','apps','SplunkAppforAWS','tmp')
BILLINGREPORTCSVDIR = os.path.join(path,'etc','apps','SplunkAppforAWS','csv')
AWSCONFIGFILE = os.path.join(path,'etc','apps','SplunkAppforAWS','local','aws.yaml')
ERRORLOGFILE = os.path.join(path,'etc','apps','SplunkAppforAWS','log','detailed_bill_errors.txt')

#setup error handling file
if not os.path.isfile(ERRORLOGFILE):
        handleERRORLOGFILE = open(ERRORLOGFILE,'w')
else:   
        handleERRORLOGFILE = open(ERRORLOGFILE,'ab')

#load configuration
configurationStream = open(AWSCONFIGFILE, 'r')
configurationObject =  yaml.load(configurationStream)

# get a bucket connection
billingBucketConnection = S3Connection(configurationObject['keys'][0]['aws_access_key'], configurationObject['keys'][0]['aws_secret_key'])
now = time.strftime("%m-%d-%Y %H:%M:%S", time.localtime())+" "+time.strftime("%z")

#make sure bucket exists before fetching - assum that this stops certain errors
try:
        billingBucket = billingBucketConnection.create_bucket(configurationObject['s3']['billing_bucket'])
except boto.exception.S3ResponseError, emsg1:
        handleERRORLOGFILE.write(now+' S3ResponseError '+str(emsg1[0])+' '+emsg1[1]+' '+str(emsg1[2])+'\n')
	
#time related malarkey for guessing billing file name - i mean building
if time.localtime()[1] > 9:
	t = str(time.localtime()[0])+'-'+str(time.localtime()[1])
else:
        t = str(time.localtime()[0])+'-0'+str(time.localtime()[1])

dday = time.localtime()[2]
#t = str(d.year)+'-'+str(d.month)

#file name
billingFileName = str(configurationObject['s3']['account_number'])+"-aws-billing-detailed-line-items-with-resources-and-tags-"+t+".csv.zip"
billingBucketHandle = billingBucketConnection.get_bucket(configurationObject['s3']['billing_bucket'])

#key object fudging
billingFileNameKey = Key(billingBucketHandle)
billingFileNameKey.key = billingFileName

#fetch the file to a temporary place on the filesystem
try:
	retrieveFileContents = billingFileNameKey.get_contents_to_filename(BILLINGREPORTZIPFILE)
except boto.exception.S3ResponseError, emsg: 
	handleERRORLOGFILE.write(now+' S3ResponseError : '+billingFileName+' '+str(emsg[0])+' '+emsg[1]+' '+str(emsg[2])+'\n')

#now unzip it ready for splunk monitoring
#unzip
#with zipfile.ZipFile(BILLINGREPORTZIPFILE, "r") as z:
#    z.extractall(BILLINGREPORTZIPDIR)
zipHandle = zipfile.ZipFile(BILLINGREPORTZIPFILE, mode='r')
for subfile in zipHandle.namelist():
    zipHandle.extract(subfile, BILLINGREPORTCSVDIR)
