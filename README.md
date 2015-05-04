SplunkAppforAWSBilling
======================

Splunk App for AWS Billing allows you to collect Detailed Billing data from which in-depth analysis of usage patterns and spending becomes available for Amazon Web Services environment.
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

Install as you normally would by unpacking all the files in the SPLUNK_HOME/etc/apps directory.

You will need to fill in the following pieces of information in the local directory aws.yaml file. (an example is provided)

# Splunk APP for AWS billing

## Overview
Splunk App for AWS Billing allows you to collect Detailed Billing data from which in-depth analysis of usage patterns and spending becomes available for Amazon Web Services environment.

It provides a base for you to extend and articulate your own spending and usage patterns.

Any feedback, including requests for enhancement are most welcome. Email: magic.monkee.magic@gmail.com

Splunk App for AWS Billing is hosted at GitHub
Feel free to submit a pull request:
[https://github.com/monk-ee/SplunkAppforAWSBilling](https://github.com/monk-ee/SplunkAppforAWSBilling)

## Cost Models
The application supports the straight Cost model as well as the Blended/Unblended Cost Model. Dashboards for both are provided; use the one that suits your billing settings.

## Setup Amazon detailed billing
You will need to ensure that you have set your billing preferences correctly.

 If you are not sure go to Billing Preferences:
 ![119814](6803f492-6900-11e3-b4de-005056ad5c72.png)

 You will then need to make sure that you have subscribed to Programmtic Access and have setup an S3 bucket for your bills:
 ![119815](6802b53c-6900-11e3-b4de-005056ad5c72.png)

 In this case the S3 bucket is called fct-billing. Now make sureyou have also subscribed to Detailed Billing Report (with resources and tags):
 ![119816](6801857c-6900-11e3-b4de-005056ad5c72.png)

 It's also a great idea to setup a user account that only has readonly rights to your file bucket. I use an account called service.splunk.

## Setup Splunk App
The app is provided as an spl an can be installed using the GUI - feel free to unpack it if you want:

It's file system location is [SPLUNK_HOME]/etc/apps/SplunkAppforAWSBilling.

You will need to take the aws.yaml.example and put in your own configuration details then save it as aws.yaml in the [SPLUNK_HOME]/etc/apps/SplunkAppforAWSBilling/local directory.
![119817](68005a76-6900-11e3-b4de-005056ad5c72.png)

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
![119818](67ff275a-6900-11e3-b4de-005056ad5c72.png)

Splunk translates them to the following values:
![119819](67fe026c-6900-11e3-b4de-005056ad5c72.png)

So to use them in a search you will need to refer to them like this:
![119820](67fccfdc-6900-11e3-b4de-005056ad5c72.png)

So to recap, your custom tag looks like this in the report:
> user:Name

And is translated to
> user_Name

All strange characters are changed on the way past to the underscore character (_)

## Logs
The error log file system location is [SPLUNK_HOME]/etc/apps/SplunkAppforAWSBilling/log/detailed_bill_errors.txt.

## Additional Command Line Tools

Located in the bin directory of the application are two new tools for fetching and processing older reports. If you do not change to the splunk user (recommended) you will need to set the SPLUNK_HOME for these to work:

    export SPLUNK_HOME=/opt/splunk

+ fetch_older_reports.py: will fetch the reports for you
+ process_older_report.py will process them for you

### Fetching
#### usage: fetch_older_report.py [-h] [-d] year month

A utility for fetching/downloading older report files into SplunkAppforAWSBilling.

Be very careful, do not fetch the current months data - you will cause a double up of records in the splunk index.
`
To be used in conjunction with process_older_report.py

    positional arguments:
        year          The year in this format: 2014 (YYYY)
        month         The month in this format: 05 (MM)

    optional arguments:
        -h, --help    show this help message and exit
        -d, --dryrun  Fake runs for testing purposes.

### Processing
#### usage: process_older_report.py [-h] [-d] year month

A utility for processing older report files into splunk for processing. Be very careful, do not process this months data - you will cause a double up of records in the splunk index.

    positional arguments:
        year          The year in this format: 2014 (YYYY)
        month         The month in this format: 05 (MM)

    optional arguments:
        -h, --help    show this help message and exit
        -d, --dryrun  Fake runs for testing purposes.

Restart splunk and you should be away.


### Configuration

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

Special thanks to Nilesh Khetia who's module I borrowed to make this one http://answers.splunk.com/users/114849/nkhetia



@todo set the input to be scripted not csv reader