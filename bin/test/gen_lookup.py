#!/usr/bin/python


import os, sys, calendar, datetime,time, ConfigParser
from ConfigParser import SafeConfigParser

path = os.environ["SPLUNK_HOME"]

LKUPFL = os.path.join(path,'etc','apps','SplunkAppforAWS','local','lookup1.txt')
CFGFL = os.path.join(path,'etc','apps','SplunkAppforAWS','local','aws.conf')
parser = SafeConfigParser()
parser.read(CFGFL)

parser = SafeConfigParser()
parser.read(CFGFL)

fLKUPFL = open(LKUPFL,'w')
for key,dept in parser.items("keys"):
        dept = dept.rstrip()
        cols = dept.split()
        if len(cols) > 0:
	        fLKUPFL.write(cols[0].rstrip()+'\n')
fLKUPFL.close()
