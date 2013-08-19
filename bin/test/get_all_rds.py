#!/usr/bin/python

# new ci1.txt -->  time=1341961850 instancetype=m2.2xlarge region=us-west-1a subaccount=production instanceid=i-040ea842

# new ri1.txt -->  time=1341952630 instancetype=m1.large region=us-east-1e subaccount=staging instancecount=8



import os, sys, boto.rds, datetime, time, calendar, ConfigParser
from pprint import pprint
from datetime import datetime
from ConfigParser import SafeConfigParser
import datetime, time

path = os.environ["SPLUNK_HOME"]

CIALL = os.path.join(path,'etc','apps','SplunkAppforAWS','log','rds_ci11.txt')
RIALL = os.path.join(path,'etc','apps','SplunkAppforAWS','log','rds_ri11.txt')
CICUR = os.path.join(path,'etc','apps','SplunkAppforAWS','log','rds_ci1.txt')
RICUR = os.path.join(path,'etc','apps','SplunkAppforAWS','log','rds_ri1.txt')
FINTMP = os.path.join(path,'etc','apps','SplunkAppforAWS','log','rds_final22.txt')
RITMP = os.path.join(path,'etc','apps','SplunkAppforAWS','log','rds_ri2.txt')
FINAL = os.path.join(path,'etc','apps','SplunkAppforAWS','log','rds_instances.txt')
CFGFL = os.path.join(path,'etc','apps','SplunkAppforAWS','local','aws.conf')
ERRFL = os.path.join(path,'etc','apps','SplunkAppforAWS','log','errors.txt')

if not os.path.isfile(ERRFL):
        fERRFL = open(ERRFL,'w')
else:
        fERRFL = open(ERRFL,'ab')

fFITMP = open(FINTMP,'w')
fRITMP = open(RITMP,'w')
fCICUR = open(CICUR,'w')
fRICUR = open(RICUR,'w')

now=time.strftime("%m-%d-%Y %H:%M:%S", time.localtime())+" "+time.strftime("%z")

print now

parser = SafeConfigParser()
parser.read(CFGFL)
#print parser.items("keys")
for key,dept in parser.items("keys"):
        dept = dept.rstrip()
        cols = dept.split()
        if len(cols) > 2:
            for rgn,rline in parser.items("regions"):
                rline = rline.rstrip()
                try:
                        rds_conn = boto.rds.connect_to_region(str(rline),aws_access_key_id=cols[1],aws_secret_access_key=cols[2])
                except boto.exception.RDSResponseError, emsg:
                        fERRFL.write(now+' '+str(key)+' '+dept+' '+rline+'\n')
                        continue
                running_all = rds_conn.get_all_dbinstances()
                for db_instance in running_all:
                        #for db_instance in running_instance.instances:
                        print (db_instance.__dict__)
      #                          if instance.state == "running":
       #                                 rn = instance.placement
        #                                citype = instance.instance_type
        #                                iid = instance.id
        #                                if instance.tags:
                                                #tgs = instance.tags["Name"]
                                                #tgs = ','.join(instance.tags)
        #                                        tgs = ""
        #                                        for keys in instance.tags:
         #                                               tgs+=str("["+keys + "=" +  instance.tags[keys]+ "]")
          #                              else:
           #                                     tgs = 'None'
            #                            fCICUR.write(now+' instancetype='+citype+' region='+rn+' subaccount='+cols[0]+' instanceid='+iid+' tags=['+tgs+']\n')



###################################
fCICUR.close()
fRICUR.close()
fERRFL.close()

fCIALL = open(CIALL,'ab')
for line in open(CICUR):
        fCIALL.write(line)
fCIALL.close()

fRIALL = open(RIALL,'ab')
for line in open(RICUR):
        fRIALL.write(line)
        fRITMP.write(line)
fRIALL.close()
fRITMP.close()

for ciline in open(CICUR):
        cols = ciline.split()
        run_state = "Y"
        rilines1 = []
        totsum = 0
        ciline = ciline.rstrip()
        search = cols[0]+' '+cols[1]+' '+cols[2]+' '+cols[3]+' '+cols[4]
        for riline in open(RICUR).readlines():
                if riline.find(search) >= 0:
                        riline = riline.rstrip()
                        rilines1.append(riline)
                        cols = riline.split()
                        count1 = cols[6].split('=')
                        totsum = totsum + int(count1[1])
        if len(rilines1) == 0:
                fFINTMP = open(FINTMP,'ab')
                fFINTMP.write(ciline.rstrip()+' running=Y reserved=N\n')
                fFINTMP.close()
        else:
                filines1=[]
                fFINTMP = open(FINTMP)
                for filine in fFINTMP.readlines():
                        if filine.find(search) >=0:
                                filines1.append(filine)
                fFINTMP.close()
                if totsum > len(filines1):
                        res_state="Y"
                else:
                        res_state="N"
                fFINTMP = open(FINTMP,'ab')
                fFINTMP.write(ciline.rstrip()+' running='+run_state+' reserved='+res_state+'\n')
                fFINTMP.close()

for riline in open(RICUR):
        riline = riline.rstrip()
        cols = riline.split()
        rilines1=[]
        subac=cols[5]
        totsum=0
        search = cols[0]+' '+cols[1]+' '+cols[2]+' '+cols[3]+' '+cols[4]
        for riline1 in open(RITMP).readlines():
                if riline1.find(search) >= 0:
                        riline1 = riline1.rstrip()
                        rilines1.append(riline1)
                        cols = riline1.split()
                        count1 = cols[6].split('=')
                        totsum = totsum + int(count1[1])
        filines1=[]
        fFINTMP = open(FINTMP)
        for filine in fFINTMP.readlines():
                if filine.find(search) >=0:
                                filines1.append(filine)
        fFINTMP.close()
        fFINTMP = open(FINTMP,'ab')
        yy=len(filines1)
        while (totsum > yy):
                fFINTMP.write(search+' '+subac+' instanceid=reserved running=N reserved=Y\n')
                yy = yy+1
        fFINTMP.close()


#fFINAL = open(FINAL,'ab')
#for line in open(FINTMP):
#        fFINAL.write(line)
#         print line
#fFINAL.close()


