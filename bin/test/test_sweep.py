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
from datetime import datetime
from pprint import pprint

#path and file stuff
path = os.environ["SPLUNK_HOME"]
BILLINGREPORTZIPFILE = os.path.join(path,'etc','apps','SplunkAppforAWS','tmp','detailed_billing.zip')
BILLINGREPORTZIPDIR = os.path.join(path,'etc','apps','SplunkAppforAWS','tmp')
BILLINGREPORTCSVDIR = os.path.join(path,'etc','apps','SplunkAppforAWS','csv')
AWSCONFIGFILE = os.path.join(path,'etc','apps','SplunkAppforAWS','local','sweeper.yaml')
ERRORLOGFILE = os.path.join(path,'etc','apps','SplunkAppforAWS','log','sweeper_errors.txt')

#setup error handling file
if not os.path.isfile(ERRORLOGFILE):
        handleERRORLOGFILE = open(ERRORLOGFILE,'w')
else:   
        handleERRORLOGFILE = open(ERRORLOGFILE,'ab')

#load configuration
configurationStream = open(AWSCONFIGFILE, 'r')
configurationObject =  yaml.load(configurationStream)

# get a bucket connection
#amiInstanceConnection = S3Connection(configurationObject['keys'][0]['aws_access_key'], configurationObject['keys'][0]['aws_secret_key'])
for region in configurationObject['regions']:
	print str(region['name'])
	#conn = boto.ec2.connection.EC2Connection(configurationObject['keys'][0]['aws_access_key'], configurationObject['keys'][0]['aws_secret_key'],regions['name'])
 	#print boto.ec2.regioninfo.EC2RegionInfo(conn)
	conn = boto.ec2.connect_to_region(region['name'], 
		aws_access_key_id=str(configurationObject['keys'][0]['aws_access_key']),
		aws_secret_access_key=str(configurationObject['keys'][0]['aws_secret_key']))
	reservations = conn.get_all_instances()
	instances = [i for r in reservations for i in r.instances]
	row = 0
	for i in instances:
		row += 1
    		#pprint(i.__dict__)
		#print str(i.state)
		if str(i.state) == "running":
			#pprint(i.id)
			if 'SHUTDOWN' in i.tags:
				pprint(i.tags['SHUTDOWN'])
				if .tags['SHUTDOWN] =='Default':
					pprint(i.id)
					i.stop()
			if 'OWNER_T3' in i.tags:
				pprint(i.tags['OWNER_T3'])
				pprint(i.id)
	print str(row)
