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

![Billing Management Console](/screenshots/Billing_Management_Console.png)

 You will then need to make sure that you have subscribed to "Recieve Billing Reports" and have setup a valid S3 bucket for your bills.

 Now make sure you have also ticked the Detailed Billing Report (with resources and tags):

 It's also a great idea to setup an IAM user account that only has readonly rights to your file bucket. 
 

## Setup and Configuration of the Splunk App
The app is provided as an spl an can be installed using the GUI - feel free to unpack it if you want:

It's file system location is [SPLUNK_HOME]/etc/apps/SplunkAppforAWSBilling.

You will need to take the aws.yaml.example and put in your own configuration details then save it as aws.yaml in the [SPLUNK_HOME]/etc/apps/SplunkAppforAWSBilling/local directory.

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

You can enable it by navigating to Settings > Data Inputs > Scripts and clicking on enable for the the command
"$SPLUNK_HOME/etc/apps/SplunkAppforAWSBilling/bin/maintain_detailed_reports.py".

## Logs
The error log file system location is [SPLUNK_HOME]/var/log/splunk/SplunkAppforAWSBilling.log.

## Additional Tools

Located in the bin directory of the application are two tools for fetching and processing older reports. 

They are designed to be run as Splunk CLI scripts:
eg.
    
    $SPLUNK_HOME/bin/splunk cmd python $SPLUNK_HOME/etc/apps/SplunkAppforAWSBilling/bin/fetch_older_report.py 2015 04
    
They are CLI only, so you will need to be able to navigate to the bin directory of the application in a shell or command
session. They live in the $SPLUNK_HOME/etc/apps/SplunkAppforAWSBilling/bin directory.

It is best to disable the fetch_detailed_report while you import the older months because they use the same temporary
file to download to.

You can disable it by navigating to Settings > Data Inputs > Scripts and clicking on disable for the the command
"$SPLUNK_HOME/etc/apps/SplunkAppforAWSBilling/bin/fetch_detailed_report.py".

You run the fetch_older_report command with the year and month report you want (you can do this for multiple months, but not in parallel)
You then run the process_older_report command with the same year and month with user credentials for a suitably privileged user.

The older events should have appeared in the index, be aware for big files this can take a long time. Don't forget to 
re-enable the fetch_detailed_report script when you are done.

### Fetching
#### usage: fetch_older_report.py [-h] [-d] year month

A utility for fetching/downloading older report files into SplunkAppforAWSBilling.

To be used in conjunction with process_older_report.py

    positional arguments:
        year          The year in this format: 2014 (YYYY)
        month         The month in this format: 05 (MM)

    optional arguments:
        -h, --help    show this help message and exit
        -d, --dryrun  Fake runs for testing purposes.
        
You don't need to stop Splunk for this script to run.


### Processing
#### usage: process_older_report.py [-h] [-d] year month

A utility for processing older report files into Splunk for processing. You will need to run the fetch script first with the appropriate date.

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

### Contributors

Special thanks to Nilesh Khetia who's module I borrowed to make this one http://answers.splunk.com/users/114849/nkhetia


### Release Notes

2.0.0 

    - Supports multiple accounts
    - events are streamed in json
    - file positions are tracked using yaml files, to reduce the likelihood of double ups
    - all functions have been moved to classes
    - boto has been updated to 2.38.0
    - proxy support is introduced but not implemented - coming soon!
    
    
### Examples
Here are some example searches, I hope you find them useful:

    index=aws-bill | timechart sum(BlendedCost) as $ by ItemDescription