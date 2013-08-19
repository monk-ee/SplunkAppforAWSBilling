#!/usr/bin/python
#ap-southeast-2
#AKIAIQDZ4YGX6ZCWLTMA
#WJ3hcMrWvedNNBx+e6bu9p+CBe5fdtkN4WxIV2os
#aws_access_key_id='AKIAIQDZ4YGX6ZCWLTMA',
#aws_secret_access_key='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')

import boto.rds

conn = boto.rds.connect_to_region(
	"ap-southeast-2",
	aws_access_key_id='AKIAJJG6NBIMIJSAXO3A',
	aws_secret_access_key='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')
print conn
