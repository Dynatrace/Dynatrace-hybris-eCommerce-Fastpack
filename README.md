# Dynatrace-hybris-eCommerce-Fastpack
This is a Python 3 based script designed to import Custom Service and Request Attribute definitions and deploy them to your Dynatrace Tenant through the Configuration API. Specifically, the Custom Services and Request Attributes in this repo are for monitoring the Hybris eCommerce environment. 

This script was designed to be re-usable for deploying any Custom Services and Request Attributes, not just Hybris. At a high level: you provide the inputs and the script posts them to the target tenant. 

__It is not yet possible to create the following items with the Configuration API. Please refer to the videos on Dynatrace APMU for instructions on how to create them:__
* Hybris JMX Metrics
* Request Naming Rules based on Request Attributes

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
  * Read Configuration
  * Write Configuration
  * Capture request data

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

## Running the Script
Once all of your files are in order, it's as simple as navigating to repository directory and running:
```
python dynatrace_hybris_ecommerce_fastpack.py
```

Please take into account that your python command may vary. Some may have to us python3, others py. Basically, use whatever python command will invoke your python 3 CLI.

## How the script operates
This section describes how the script operates. 

* The log file is initialized
* The Constants file gets read and processed
* The user is required to input their API Token. The token is checked to make sure it's 21 characters long. If not, and the user does not correct it, the script exits.
* The user is required to input their tenant name. Since tenant names, especially if managed, can be almost anything, all we're doing here is verifying that the input is not null. 
* Headers are created
* A GET is run against custom services, checking for the status code. This is to determine if the API Token and Tenant are Valid.  If an HTTP 200 is not returned, the script exits with a specific message both in the terminal as well as in the log file
* Custom Services are created:
  * The CustomServicesList.txt file is parsed and sent to the gatherFilesList function. 
  * The gatherFilesList function creates a library containing the path/filename of all of the custom services to be created
  * The getExistingConfigs function is invoked and gathers a list of existing custom services.
  * The postConfigs function is called to create the custom services, looping through all of the loaded JSON files.
     * First, we check the name of the new custom service against the list of existing services. a duplicate cannot be created, so if a duplicate is found, we append today's date to the end of the name to make it unique. We do this because even though the names may be the same, the configuration may be different. We want to give the user the option as to whether or not they want to stay with their original config, use the new one, or, if there are difference, merge the differences.
     * Once the name is checked and possibly modified, the custom service is created. If the name has not been modified, the custom service is created as 'active'. If it's a duplicate and the name was modified, it is created but set to 'inactive' in order to avoid any conflicts.  
     * With the POST of the config, the status code is checked. If it's a 201 status code - success, the name of the config and the file are written to a library so they can be verified in the next step. If the status is not 201, the creation of that custom service is aborted and the function loops to the next.
  * Once all of the custom services are created, the confirmCreation function is invoked. This takes the list of custom service names (the modified ones if they had to get modified) and the JSON file for all custom services that returned a 201 success during creation. The function runs another GET against the list custom services endpoint, capturing the names of the existing custom services which should now contain the new services. The names returned in by postConfigs are checked against the names from the new GET. If the name exists, the function writes a success message to the console and the log. If the name does not exist, the custom service is posted and if there's a 201 result, the name and JSON file get written to another confirmation dictionary for use in the next step. If the result is not a 201, that custom service is aborted.
  * In the final step, we loop through the confimation step until all created services exist. There is a small chance for an endless loop here if something very strange is wrong, but remember, only services that get a 201 status are re-checked. We will not be in a situation where a 4xx or 5xx result will result in an endless loop, as those ones are not retried.
     * these confirmation steps were created becuase of a known issue where in certain circumstances, a 201 result will be returned, but the configuration will not persist. Once this issue is resolved, we can decided to either keep the confirmation steps or get rid of them. I'm leaning towards keeping them.  
* The entire process above is repeated for the Request Atttrubutes. All of the same functions are used.
  * When the script is complete, the terminal prompts the user to check the log file for results as well as instructions to verify the results in the tenant and make choices for identified, renamed duplicated. 

