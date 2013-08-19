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
import ConfigParser
import boto
import zipfile
import yaml
from pprint import pprint
from boto.s3.connection import S3Connection
from datetime import datetime
from boto.s3.key import Key
from ConfigParser import SafeConfigParser

path = os.environ["SPLUNK_HOME"]

BILLINGREPORTZIPFILE = os.path.join(path,'etc','apps','SplunkAppforAWS','log','detailed_billing.zip')
AWSCONFIGFILE = os.path.join(path,'etc','apps','SplunkAppforAWS','local','aws.yaml')
ERRORLOGFILE = os.path.join(path,'etc','apps','SplunkAppforAWS','log','errors.txt')

if not os.path.isfile(ERRORLOGFILE):
        handleERRORLOGFILE = open(ERRORLOGFILE,'w')
else:   
        handleERRORLOGFILE = open(ERRORLOGFILE,'ab')

import yaml

configurationStream = open(AWSCONFIGFILE, 'r')
print yaml.load(stream)

corpkey1 = parser.get('misc', 'corpkey').rstrip().split()
s3bucket1 = parser.get('misc', 's3bucket').rstrip()
acno1 = parser.get('misc', 'acno').rstrip()

conn = S3Connection(corpkey1[1], corpkey1[2])
now=time.strftime("%m-%d-%Y %H:%M:%S", time.localtime())+" "+time.strftime("%z")

try:
        a = conn.create_bucket(s3bucket1)
except boto.exception.S3ResponseError, emsg1:
        handleERRORLOGFILE.write(now+' S3ResponseError '+str(emsg1[0])+' '+emsg1[1]+' '+str(emsg1[2])+'\n')
	
if time.localtime()[1] > 9:
	t = str(time.localtime()[0])+'-'+str(time.localtime()[1])
else:
        t = str(time.localtime()[0])+'-0'+str(time.localtime()[1])

dday = time.localtime()[2]
#t = str(d.year)+'-'+str(d.month)
bfile = acno1+"-aws-billing-csv-"+t+".csv"
b = conn.get_bucket(s3bucket1)
k = Key(b)
k.key = bfile
try:
	rs = k.get_contents_to_filename(BLTMP2)
except boto.exception.S3ResponseError, emsg: 
	fERRFL.write(now+' S3ResponseError : '+bfile+' '+str(emsg[0])+' '+emsg[1]+' '+str(emsg[2])+'\n')

search = 'total for linked account'
reader = csv.reader(open(BLTMP2),skipinitialspace=True, delimiter=',', quotechar='"')
fBLTMP1 = open(BLTMP1,'w')
for rrow in reader:
	row1 = str(rrow)[1 : -1]
	if row1.lower().find(search) >= 0:
		row1 = row1.rstrip()
		amt = int(round(float(rrow[28])))
		mproj = amt*30/dday
		mlimit = '0'
		dlimit = 0
		acc = ''
	        try:
			acc=parser.get('keys',str(rrow[2])).rstrip()
		except ConfigParser.NoOptionError:
		    fERRFL.write(now+' '+str(rrow[2])+' not found in aws.conf'+'\n')
                    continue
	        if len(acc) > 0:
			cols = acc.rstrip().split()
			if len(cols)> 3:
				mlimit = cols[3]
				dlimit = int(cols[3])*dday/30
	        fBLTMP1.write(now+' masteraccount='+rrow[1]+' subaccountid='+rrow[2]+' subaccount=['+rrow[9]+'] amount='+str(amt)+' mprojection='+str(mproj)+' dlimit='+str(dlimit)+' mlimit='+mlimit+'\n')	

fERRFL.close()

fBLTMP1.close()

fBLFINAL = open(BLFINAL,'ab')
for line in open(BLTMP1):
#        fBLFINAL.write(line)
	print line
fBLFINAL.close()

#fBLCSV = open(BLCSV,'ab')
#for line in open(BLTMP2):
#        fBLCSV.write(line)
#fBLCSV.close()

