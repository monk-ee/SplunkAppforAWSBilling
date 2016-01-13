VERSION = 12.0.5
ZIPNAME= splunk-app-for-aws-billing.zip

all:
        /usr/bin/zip -r $(ZIPNAME) SplunkAppforAWSBilling --exclude=*.gitignore* --exclude=*Makefile* --exclude*.git*