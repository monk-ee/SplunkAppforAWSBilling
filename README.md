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
* Boto 2.10.0
* PyYaml 3.10

#Installation Instructions

Install as you normally would by unpacking all the files in the SPLUNK_HOME/etc/apps directory.

You will need to fill in the following pieces of information in the local directory aws.yaml file. (an example is provided)

Restart splunk and you should be away.

> s3:
>  account_number: 123456
>  billing_bucket: name-of-bucket
>  time_zone: Australia/Brisbane
> regions:
>  - name: ap-southeast-2
> keys:
>  - account_number    : 123456
>    name              : service.splunk
>    aws_access_key    : AAAAAAAAAAAA
>    aws_secret_key    : AAAAAAAAAAAABBBBBBBBBBBBBBCC
>    spend_limit       : 10000
>    corporate_key     : true

Special thanks to Nilesh Khetia who's module I borrowed to make this one http://answers.splunk.com/users/114849/nkhetia
