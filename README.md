SplunkAppforAWSBilling v2.0.11
=============================

Splunk App for AWS Billing allows you to collect Detailed Billing data from which in-depth analysis of usage patterns 
and spending becomes available for Amazon Web Services environment.
It provides a base for you to extend and articulate your own spending and usage patterns.

# Features

## Billing Analysis for:

* AWS Direct Connect
* AWS Support (Business)
* Amazon DynamoDB
* Amazon Elastic Compute Cloud
* Amazon RDS Service
* Amazon Simple Email Service
* Amazon Simple Notification Service
* Amazon Simple Queue Service
* Amazon Virtual Private Cloud

## Supports:

* Custom Tags
* Billing Projections
* Month-over-Month Billing Comparision
* Day/Night Billing Comparison
* Usage Analysis
* Simple YAML configuration

## Graphs

* Costs by AWS Product
* Current Spend
* Billing items
* Monthly Raw Costs
* Costs by Availability Zone

## Includes:

* Boto 2.38.0
* PyYaml 3.10

#Installation Instructions

Install as you normally would by unpacking all the files in the SPLUNK_HOME/etc/apps directory or uploading using the 
app manager.

You will need to fill in the following pieces of information in the local directory aws.yaml file. 
(an example is provided)

## Upgrading from older versions (especially pre 2.0.9)

The scripts have changed to go back at least 12 months to fecth older reports, this means the old method for getting 
reports and processing has been deprecated. DO NOT under any circumstances run the fetch older or process older reports 
scripts. At best they will not work at worst they will cause data duplicates.

Currently on upgrade these files will be in your bin directory, delete them for your own safety and sanity. 

Versions moving forward will not have these files.

It would be better if you have the time, to flush all your indexes and install the application 
"as if for the first time", these will avoid any of the nasty import duplication bugs that were present in the 
2.0.5 - 2.0.8 releases.

If you would like older reports than just a year (it defaults to 12), you can change the history value in aws.yaml file:

    history: 12

If the history stanza is missing from your aws.yaml - the code will not break (since 2.0.11) - it just means you wont be
able to change the history value.


# Splunk APP for AWS billing

## Overview
Splunk App for AWS Billing allows you to collect Detailed Billing data from which in-depth analysis of usage patterns 
and spending becomes available for Amazon Web Services environment.

It provides a base for you to extend and articulate your own spending and usage patterns. It converts your billing line 
items into JSON which is imported and can be processed in Splunk.

Any feedback, including requests for enhancement are most welcome. Email: magic.monkee.magic@gmail.com

Splunk App for AWS Billing is hosted at GitHub:

Feel free to submit a pull request:
[https://github.com/monk-ee/SplunkAppforAWSBilling](https://github.com/monk-ee/SplunkAppforAWSBilling)

Also feel fre to raise any issues here:
[https://github.com/monk-ee/SplunkAppforAWSBilling/issues](https://github.com/monk-ee/SplunkAppforAWSBilling/issues)

## Cost Models
The application supports the straight Cost model as well as the Blended/Unblended Cost Model. Dashboards for both are 
provided; use the one that suits your billing settings.

From Amazon's own documentation:

    Keep in mind that blended rates apply only to Consolidated Billing customers.

http://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/con-bill-blended-rates.html

### Blended and Unblended Rates:

The detailed billing report enables customers to perform detailed cost analyses on their usage. 
AWS meters usage in hourly increments; for each product resource in use, a rate is applied for operations performed by 
usage type in that hour, with each operation comprising a 
line item. The detailed billing report shows both blended and unblended rates for each line item. An unblended rate is 
the cost per hour for a product, usage type, and the 
operation performed. A blended rate is an average rate calculated for identical instance usage in an Availability Zone 
for members of a Consolidated Billing family.

### A Quiet Word about the detailed Billing Reports eg Why no Cost field?
If you have a single AWS account and you don't use Consolidated billing your report only contains the Rate and Cost 
Fields.

eg NON-CONSOLIDATED: Your search should look like this:

    index=aws-bill | timechart sum(Cost) as $ by ItemDescription

If you have have multiple AWS accounts and use Consolidated billing  your report contains BlendedRate, BlendedCost, 
UnBlendedRate and UnBlendedCost fields BUT not the Cost and Rate fields.

eg CONSOLIDATED: Your search should look like this:
    
    index=aws-bill | timechart sum(BlendedCost) as $ by ItemDescription

This means you need different searches and dashboards for the different billing reports eg a Consolidated OR a Single 
billing account report.

## Setup Amazon detailed billing

v2.0 Indexes are not compatible with earlier versions of the app, you will have to rerun all your log data and flush the
 older indexes - the data has changed from csv items to JSON.

You will need to ensure that you have set your billing preferences correctly.

 If you are not sure go to Billing Preferences:

![Billing Management Console](/screenshots/Billing_Management_Console.png)

 You will then need to make sure that you have subscribed to "Recieve Billing Reports" and have setup a valid S3 bucket 
 for your bills.

 Now make sure you have also ticked the Detailed Billing Report (with resources and tags):

 It's also a great idea to setup an IAM user account that only has readonly rights to your file bucket. 
 

## Setup and Configuration of the Splunk App
The app is provided as an spl an can be installed using the GUI - feel free to unpack it if you want:

It's file system location is $SPLUNK_HOME/etc/apps/SplunkAppforAWSBilling.

You will need to take the aws.yaml.example and put in your own configuration details then save it as aws.yaml in the 
$SPLUNK_HOME/etc/apps/SplunkAppforAWSBilling/local directory.

For a single account use the following style of aws.yaml:

    accounts:
        - account_number    : 123456
          billing_bucket    : company-billing
          aws_access_key    : AAAAAAAAAAAA
          aws_secret_key    : AAAAAAAAAAAABBBBBBBBBBBBBBCC


For multiple accounts use the following style of aws.yaml:

    accounts:
        - account_number    : 123456
          billing_bucket    : company-one-billing
          aws_access_key    : AAAAAAAAAAAA
          aws_secret_key    : AAAAAAAAAAAABBBBBBBBBBBBBBCC
        - account_number    : 654321
          billing_bucket    : company-two-billing
          aws_access_key    : AAAAAAAAAAAA
          aws_secret_key    : AAAAAAAAAAAABBBBBBBBBBBBBBCC


## S3 Bucket Policy

Your bucket policy for the programmatic user (the user that accesses the bucket) should look something like this; as a minimum:

    {
    
     "Version": "2012-10-17",
    
     "Statement": [{
    
         "Effect": "Allow",
    
         "Action": ["s3:ListBucket", "s3:GetObject", "s3:GetObjectVersion"],
    
         "Resource": [
    
             "arn:aws:s3:::billing-bucket",
    
             "arn:aws:s3:::billing-bucket/*"
    
         ]
    
       }]
    
    }
    
The best practice for this is to create a new policy and user for this, NEVER EVER EVER EVER use your root credentials for this.

## The index
The index is called aws-bill

## The views
There are three main views:

+ AWS billing
+ Resources Breakdown
+ Example Tag charts

## Customizing your Tag Graphs
When the app imports your billing report it adds all of the custom fields from your report.
They appear like this in your report:

![Billing Management Console](/screenshots/Custom_Tags.png)

You can then use them in a search or to customize a dashboard like so:

    index=aws-bill | timechart sum(BlendedCost) as $ by user:Customer

## Maintenance
A script is provided to allow the system to clean up old csv files, it is disabled by default.

You can enable it by navigating to Settings > Data Inputs > Scripts and clicking on enable for the command
"$SPLUNK_HOME/etc/apps/SplunkAppforAWSBilling/bin/MaintainDetailedReports.py".

It will delete all zips and csvs older than a year.

## Logs
The error log file system location is $SPLUNK_HOME/var/log/splunk/SplunkAppforAWSBilling.log.

### Contributors

Special thanks to Nilesh Khetia who's module I borrowed to make this one http://answers.splunk.com/users/114849/nkhetia


### Release Notes

2.0.5

    - Supports multiple accounts
    - set driven duplicate protection for line items
    - events are streamed in json
    - file positions are tracked using pickle binary files, to reduce the likelihood of double ups
    - all functions have been moved to classes
    - boto has been updated to 2.38.0
    - old reports are posted to splunk using splunklib index post
    - proxy support is introduced - a must for corporate network fun
    - pivot tables on LinkedAccountId
    
2.0.6

    - automated history fetching - last 12 months
    - automated report processing - last 12 months
    - no date fudging
    - checksums of s3 billing reports are checked so only changed files are downloaded
    - all original zip files are downloaded locally
    - the raw data files are unzipped on the system
    - fix for UsageStartDate 'fudge' misfiring Issue #5 https://github.com/monk-ee/SplunkAppforAWSBilling/issues/5
    - fix for Double Indexed Items - Remove KVMODE  Issue #6 https://github.com/monk-ee/SplunkAppforAWSBilling/issues/6
    - be aware the application needs more space as it gets a years worth of data and unzips it
    - maintenance script will clean up files older than a year (but it is still disabled by default)
 
2.0.7

    - fix recurring position bug

2.0.8

    - clear duplicates from positional set - this a cracker - sorry about that folks

2.0.9

    - changed the import to KV_MODE json - this is more flexible than commiting to an index at import time

2.0.10

    - remove deprecated files
    - add doco abput upgrading
    
2.0.11

    - harden up history file fetching
    - talk about the fetching of aws reports
        
### Examples
Here are some consolidated billing example searches, I hope you find them useful:

    index=aws-bill | timechart sum(BlendedCost) as $ by ItemDescription
    index=aws-bill BlendedCost !="" | timechart span=1day sum(BlendedCost) as $ by ProductName useother=f
    
Search for Duplicate Record Id - to see if the import has gone crazy.

    index=aws-bill | stats count by RecordId | where count > 1
    
### Reports

- Monthly Blended Raw Costs (Bar)
- Monthly UnBlended Raw Costs (Bar)
- Last Month Daytime Blended Costs (Bar)
- Last Month Nighttime Blended Costs (Bar)
- Blended Costs by AWS Product (Bar)
- Current $ Spend  (Gauge)
- Billing Items
- Usage Quantity


- Account
- Daily Cost
- Tag Report
- This Month vs. Last Month Detail
- This Week vs. Last Week by Account
- Total Invoiced Cost
- Usage Type.

### Billing and Cost Management

dashboard

- spend summary - include subscriptions
- month-to-date spend by service
- consolidated bill charges by service charges
- bill details by account ****

cost explorer

- monthly spend by service view
- monthly spend by linked account view
- daily spend view

Pivot

- API Operation
- Availability Zone
- Linked Account
- Purchase Option
- Service
- Tag


### Warning: Danger Will Robinson!!!

- v2.0 Indexes are not compatible with earlier versions of the app, you will have to rerun all your log data and flush 
the older indexes - the data has changed from csv items to JSON.
- GST Items are thrown away - because of the currency conversion complexity. (I am considering adding these but with 
exclusion flags on the reports)
- Any LineItem that does not have a RecordId is thrown away - because it is not charged to your bill

### Troubleshooting

In the $SPLUNK_HOME/etc/apps/SplunkAppforAWSBilling/local directory are the *.p files that keep track of processed 
records. If you find that you have got twisted or need to 
reimport a file you may need to clear the aws-bill index or delete these files. 

They are basically sets of imported RecordIds - to avoid duplicates.

#### Collection of report files from AWS

If you feel you need to rush the collection of the files from AWS you can run the following command in the CLI:

    {SPLUNK_HOME}/bin/splunk cmd python FetchDetailedReport.py 

This will also troubleshoot whether you have filled the aws.yaml file in correctly. If all is good you should see some
CSV files in the csv directory.