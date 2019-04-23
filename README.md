# Dynatrace-hybris-eCommerce-Fastpack

Current Version supports Dynatrace v1.67+

This is a Python 3 based script designed to import Custom Service, Request Attribute, and Global Request Naming definitions as well as JMX Plugin Metrics and deploy them to your Dynatrace Tenant through the Configuration API and JMX API. Specifically, the Custom Services, Request Attributes, Global Request Naming Rules and JMX metrics in this repo are for monitoring the Hybris eCommerce environment.

This script was designed to be re-usable for deploying any Custom Services, Request Attributes, Request Naming Rules and JMX Metrics Plugins, not just Hybris. At a high level: you provide the inputs and the script posts them to the target tenant.


## Pre-requisites
* [Python3](https://www.python.org/downloads/)
* A local copy of this repository
* The following standard python modules:
  * datetime
  * getpass
  * json
  * logging
  * requests
  * time
  * sys
* A [Dynatrace Tenant](https://www.dynatrace.com/trial/)
* An API Token from the Dynatrace Tenant with the following permissions:
  * Read Configuration
  * Write Configuration
  * Capture request data
    * Located at Settings -> Integration -> Dynatrace API
* A PLUGIN API token from the Dynatrace Tenant
  * Located at Settings -> Monitoring -> Monitored technologies -> Custom plugins

## How to use the fastpack
There are 5 parent files in the same directory as the python script and 5 subdirectories that you may interact with. However, if you are using this repository to deploy the Hybris configurations, all you have to do is run the python script
### Parent Files:
* CustomServiceList.txt
* RequestAttributesList.txt
* RequestNamingList.txt
* jmx_metrics.txt
* Constants.txt
### Subfolders
* custom_services
* request_attributes
* request_naming
* JMX_metrics
* log

## Custom Services, Request Attributes, and Global Request Naming Rules
A custom service/request attribute/request naming rule (CS/RA/RN) is created by a data set in JSON format. Each CS/RA/RN requires its own JSON document. These are stored in the subfolders 'custom_services', 'request_attributes', and 'request_naming'. For every CS/RA/RN you want to create, store it in a new JSON document in the appropriate subfolder.

The files CustomServiceList.txt, RequestAttributesList.txt, and RequestNamingList.txt are simply text files containing a line for the path/name of each JSON file for the CS/RA/RN to be created. For whatever CS/RA/RN JSON files you create, put the relative path to their location on a new line in the respective file.

## JMX Metrics Plugins
JMX metrics are imported via the plugin API and operate a little differently than the other configurations.

For each group of metrics, for instance, yQueryRegionCache, a separate plugin file is used. This is so that the metrics will naturally be grouped together in Dynatrace. If you do not care about such grouping, you can create one large plugin file and bundle all JMX metrics together.

Each plugin JSON file **MUST** be named
>plugin.json

The plugin API imports ZIP files, not JSON files, so this is ok. each unique 'plugin.json' file gets put in a uniquely named ZIP file, like JMX_yQueryRegionCache.zip. These zip files are located in the JMX_metrics sub folder.

For each JMX Plugin you want to import, place it's zip file in the JMX_metrics subfolder and add a reference to the jmx_metrics.txt file in the following format:
> JMX_metrics/\<metricgroup\>.zip

## Log Folder
The log folder is simply the location where the log file will be written. Every time you run the script, a log file will be created with outputs and instructions.

## Constants File
The Constants.txt file has a list of constants that get read into the script. Though these are considered constants, I've placed them outside of the script because over time, the values may change. It is not expected that they do, but as you can see in the list of the constants below, if anything changes in the Configuration API, you can modify the data in the file instead of modifying the script itself.

The Constants are:
* API GET endpoints for retrieving the existing Custom Services, Request Attributes, and Request Naming Rules
* API POST endpoints for creating Custom Services, Request Attributes, Request Naming Rules, and Plugins
* URIs in the dynatrace tenant for the settings pages for Custom Services, Request Attributes, and Plugins
* the JSON keys for identifying the names of existing Custom Services, Request Attributes, and Request Naming Rules
* the JSON key value for identifying the names of existing Custom Services, Request Attributes, and Request Naming Rules

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


* JMX plugins are imported
  * The jmx_metrics.txt file is parsed and sent to the gatherFilesList function.
  * The gatherFilesList function creates a library containing the path/filename of all of the custom services to be created.
  * If there are plugins to be imported, the user is required to input their Plugin API Token. The token is checked to make sure it's 21 characters long. If not, and the user does not correct it, the script exits.
  * The postPLUGIN function is called to create the JMX Metric Plugins, looping through all of the loaded ZIP files.
  * With the POST of the plugin, the status code is checked. If it's a 200 status code - success, the name of the plugin zip file and status code are to the log and console. If the return code is not 200, the name of the script and status code are written to the log and the console.
  * The plugin API does not currently allow for any confirmation by reading the plugin list.
* When the script is complete, the terminal prompts the user to check the log file for results as well as instructions to verify the results in the tenant and make choices for identified, renamed duplicated.


* Custom Services are created:
  * The CustomServicesList.txt file is parsed and sent to the gatherFilesList function.
  * The gatherFilesList function creates a library containing the path/filename of all of the custom services to be created
  * If there are custom services to be imported, the getExistingConfigs function is invoked and gathers a list of existing custom services.
  * The postConfigs function is called to create the custom services, looping through all of the loaded JSON files.
     * First, we check the name of the new custom service against the list of existing services. Duplicates cannot be created. If a duplicate is found, the entry is skipped and a warning message is issued.
     * If the entry is not a duplicate, the custom service is created.  
     * With the POST of the config, the status code is checked. If it's a 201 status code - success, the name of the config and the file are written to a library so they can be verified in the next step. If the status is not 201, the creation of that custom service is aborted and the function loops to the next.
  * Once all of the custom services are created, the confirmCreation function is invoked. This takes the list of custom service names and the JSON file for all custom services that returned a 201 success during creation. The function runs another GET against the list custom services endpoint, capturing the names of the existing custom services which should now contain the new services. The names returned in by postConfigs are checked against the names from the new GET. If the name exists, the function writes a success message to the console and the log. If the name does not exist, the function writes an error message to the console and log file. .

* The entire process above is repeated for the Request Attributes and Request Naming Rules. All of the same functions are used.
