#!/usr/bin/python
#ap-southeast-2
#AKIAIQDZ4YGX6ZCWLTMA
#WJ3hcMrWvedNNBx+e6bu9p+CBe5fdtkN4WxIV2os

import boto.ec2

conn = boto.ec2.connect_to_region(
	"ap-southeast-2",
	aws_access_key_id='AKIAIQDZ4YGX6ZCWLTMA',
	aws_secret_access_key='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')
print conn
