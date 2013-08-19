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
import csv
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

now = time.strftime("%m-%d-%Y %H:%M:%S", time.localtime())+" "+time.strftime("%z")

#time related malarkey for guessing billing file name - i mean building
if time.localtime()[1] > 9:
	t = str(time.localtime()[0])+'-'+str(time.localtime()[1])
else:
        t = str(time.localtime()[0])+'-0'+str(time.localtime()[1])

dday = time.localtime()[2]
#t = str(d.year)+'-'+str(d.month)

#file name
billingFileName = str(configurationObject['s3']['account_number'])+"-aws-billing-detailed-line-items-with-resources-and-tags-"+t+".csv.zip"

#now read that stupid file
csvFileName = str(configurationObject['s3']['account_number'])+"-aws-billing-detailed-line-items-with-resources-and-tags-"+t+".csv"
BILLINGREPORTZIPDIRCSV = os.path.join(path,'etc','apps','SplunkAppforAWS','csv',csvFileName)
ifile = open(BILLINGREPORTZIPDIRCSV,'rb')
#processnewcsv
processedCSVFileName = str(configurationObject['s3']['account_number'])+"-aws-billing-detailed-line-items-with-resources-and-tags-"+t+".processed.csv"
BILLINGREPORTZIPDIRPROCESSEDCSV = os.path.join(path,'etc','apps','SplunkAppforAWS','csv',processedCSVFileName)
processedCSVHandle = open(BILLINGREPORTZIPDIRPROCESSEDCSV,'wb')

#ok read this file
reader = csv.reader(ifile)

# go loop go
rownum = 0 
for InvoiceID,PayerAccountId,LinkedAccountId,RecordType,RecordId,ProductName,RateId,SubscriptionId,PricingPlanId,UsageType,Operation,AvailabilityZone,ReservedInstance,ItemDescription,UsageStartDate,UsageEndDate,UsageQuantity,BlendedRate,BlendedCost,UnBlendedRate,UnBlendedCost,ResourceId,Name,OWNER_T3,SERVICE_ENVIRONMENT,SERVICE_NAME,SUPPORT_T3  in reader:
        if rownum == 0:
	   	#do nothing
 		header = InvoiceID
        else: 
 		if UsageStartDate != "":
                        try:
                        	rowdate = datetime.strptime(UsageStartDate,'%Y-%m-%d %H:%M:%S')
				newdate =  rowdate.strftime("%b %d %Y %I:%M:%S %p %z")
			except Exception:
				sys.exc_clear()
       		else:
			row = t + "-01 00:00:00" 
		#print row,InvoiceID,PayerAccountId,LinkedAccountId,RecordType,RecordId,ProductName,RateId,SubscriptionId,PricingPlanId,UsageType,Operation,AvailabilityZone,ReservedInstance,ItemDescription,UsageStartDate,UsageEndDate,UsageQuantity,BlendedRate,BlendedCost,UnBlendedRate,UnBlendedCost,ResourceId,Name,OWNER_T3,SERVICE_ENVIRONMENT,SERVICE_NAME,SUPPORT_T3
		newrow =  str(newdate)
		newrow +=  ' InvoiceID="' + InvoiceID
		newrow +=  '"'
		newrow +=  ' PayerAccountId="' + PayerAccountId
		newrow +=  '"'
		newrow +=  ' LinkedAccountId="' + LinkedAccountId
		newrow +=  '"'
		newrow +=  ' RecordType="' + RecordType
		newrow +=  '"'
		newrow +=  ' ProductName="' + ProductName
		newrow +=  '"'
		newrow +=  ' RateId="' + RateId
		newrow +=  '"'
		newrow +=  ' SubscriptionId="' + SubscriptionId
		newrow +=  '"'
		newrow +=  ' PricingPlanId="' + PricingPlanId
		newrow +=  '"'
		newrow +=  ' UsageType="' + UsageType
		newrow +=  '"'
		newrow +=  ' Operation="' + Operation
		newrow +=  '"'
		newrow +=  ' AvailabilityZone="' + AvailabilityZone
		newrow +=  '"'
		newrow +=  ' ReservedInstance="' + ReservedInstance
		newrow +=  '"'
		newrow +=  ' ItemDescription="' + ItemDescription
		newrow +=  '"'
		newrow +=  ' UsageStartDate="' + UsageStartDate
		newrow +=  '"'
		newrow +=  ' UsageEndDate="' + UsageEndDate
		newrow +=  '"'
		newrow +=  ' UsageQuantity="' + UsageQuantity
		newrow +=  '"'
		newrow +=  ' BlendedRate="' + BlendedRate
		newrow +=  '"'
		newrow +=  ' BlendedCost="' + BlendedCost
		newrow +=  '"'
		newrow +=  ' UnBlendedRate="' + UnBlendedRate
		newrow +=  '"'
		newrow +=  ' UnBlendedCost="' + UnBlendedCost
		newrow +=  '"'
		newrow +=  ' ResourceId="' + ResourceId
		newrow +=  '"'
		newrow +=  ' Name="' + Name
		newrow +=  '"'
		newrow +=  ' OWNER_T3="' + OWNER_T3
		newrow +=  '"'
		newrow +=  ' SERVICE_ENVIRONMENT="' + SERVICE_ENVIRONMENT
		newrow +=  '"'
		newrow +=  ' SERVICE_NAME="' + SERVICE_NAME
		newrow +=  '"'
		newrow +=  ' SUPPORT_T3="' + SUPPORT_T3
		newrow +=  '"'
		newrow +=  '\r\n'
        	processedCSVHandle.write(newrow)
	rownum += 1
#dont shut it you idiot
processedCSVHandle.close()
ifile.close()
