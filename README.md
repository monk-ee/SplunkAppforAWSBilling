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

Install as you normally would by unpacking all the files in the SPLUNK_HOME/etc/apps directory or uploading using the app manager.

You will need to fill in the following pieces of information in the local directory aws.yaml file. (an example is provided)

# Splunk APP for AWS billing

## Overview
Splunk App for AWS Billing allows you to collect Detailed Billing data from which in-depth analysis of usage patterns and spending becomes available for Amazon Web Services environment.

It provides a base for you to extend and articulate your own spending and usage patterns. It converts your billing line items into JSON which is imported and can be processed in SPlunk.

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


## Logs
The error log file system location is [SPLUNK_HOME]/var/log/splunk/SplunkAppforAWSBilling.log.

## Additional Tools

Located in the bin directory of the application are two new tools for fetching and processing older reports. 

They are designed to be run as splunk cli scripts:
eg.
    
    $SPLUNK_HOME/bin/splunk cmd python fetch_older_report.py 2015 04
    

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
        
You don't need to stop splunk for this script to run.


### Processing
#### usage: process_older_report.py [-h] [-d] year month

A utility for processing older report files into splunk for processing. You will need to run the fetch script first with the appropriate date.

    positional arguments:
        year          The year in this format: 2014 (YYYY)
        month         The month in this format: 05 (MM)
        user          The username for a splunk user.
        password      The password for a splunk user

    optional arguments:
        -h, --help          show this help message and exit
        -d, --dryrun        Fake runs for testing purposes
        -p, --port          The port to post events to.
        -s, --serverport    The server to post events to.

You don't need to stop splunk for this script to run.


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


### Contributors

Special thanks to Nilesh Khetia who's module I borrowed to make this one http://answers.splunk.com/users/114849/nkhetia


### Release Notes

2.0.0 

    - Supports multiple accounts
    - events are streamed in json
    - file positions are tracked using yaml files
    - all functions have been moved to classes
    - boto has been updated to 2.38.0
    - proxy support is introduced but not implemented - coming soon!
    
    
### Examples

index=aws-bill | timechart sum(BlendedCost) as $ by ItemDescription