# Dynatrace-hybris-eCommerce-Fastpack
This is a Python 3 based script designed to import Custom Service and Request Attribute definitions and deploy them to your Dynatrace Tenant through the Configuration API. Specifically, the Custom Services and Request Attributes in this repo are for monitoring the Hybris eCommerce environment. 

This script was designed to be re-usable for deploying any Custom Services and Request Attributes, not just Hybris. At a high level: you provide the inputs and the script posts them to the target tenant. 

## Pre-requisits 
* [Python3](https://www.python.org/downloads/)
* A local copy of this repository
* The following standard python modules:
  * datetime
  * json
  * logging 
  * requests
  * datetime
  * time
  * sys
* A Dynatrace Tenant
* An API Token from the Dynatrace Tenant with the following permissions:
  * 
  * 
  * 


## How to use the fastpack
There are 3 parent files in the same directory as the python script and 3 subdirectories that you may interact with. However, if you are using this repository to deploy the Hybris configurations, all you have to do is run the python script
### Parent Files:
* CustomServiceList.txt
* RequestAttributesList.txt
* Constants.txt
### Subfolders
* custom_services
* request_attributes
* log

A custom service/request attribute (CS/RA) is created by a data set in JSON format. Each CS/RA requires its own json document. These are stored in the subfolders 'custom_services' and 'request_attributes'. For every CS/RA you want to create, store it in a new json document in the appropriate subfolder. 

The files CustomServiceList.txt & RequestAttributesList.txt are simply text files containing a line for the path/name of each json file for the CS/RA to be created. For whatever CS/RA json files you create, put the relative path to their location on a new line in the respective file. 

The log folder is simply the location where the log file will be written. Every time you run the script, a log file will be created with outputs and instructions. 

The Constants.txt file has a list of constants that get read into the script. Though these are considered constants, I've placed them outside of the script becaus overtime, the values may change. It is not expected that they do, but as you can see in the list of the constants below, if anything changes in the Configuration API, you can modify the data in the file instead of modifying the script itself. 

The Constants are:
* API GET endpoints for retrieving the existing Custom Services and Request Attributes
* API POST endpoints for creating Custom Services and Request Attributes
* URIs in the dynatrace tenant for the settings pages for Custom Services and Request Attributes
* the JSON keys for identifying the names of existing Custom Services and Request Attributes
