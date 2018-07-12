
# change error prints to a file write, or both.
# re-evaluate whether each exit should actually exit or continue, writing an out error instead that a specific step failed.


# =========================================================
# REQUIRED LIBRARIES
# =========================================================

import datetime
import json
import logging
import requests
import sys
from time import sleep

# =========================================================
# REUSABLE VARIABLE DECLARATION
# =========================================================

config_data_len= 0
config_iteration = 0
config_json_path = []
confirmation_dict = {}
constants_dict = {}
dtTenantURL = 'https://'
name_values = []
parent_file_name = ''
recheck_confirmCreation = {}

# =========================================================
# FUNCTIONS
# =========================================================

def handleException(e):
    "Handles Exceptions. Prints them to console and exits the program"
    errorObject = {}
    if e.args:
        if len(e.args) == 2:
            errorObject[e.args[0]] = e.args[1]
        if len(e.args) == 1:
            errorObject["error"] = e.args[0]
    else:
        errorObject["exception"] = e
    logging.error(errorObject)
    sys.exit(1)


def getAPIToken():
    """ this function gets the api token, validates it's a length of 21, and returns it to the apitoken variable"""
    apitoken = input('Enter your tenant API token for the Config API: ')
    if len(apitoken) == 21:
        return apitoken
    else:
        apitoken = input('Please enter a valid tenant API token for the Config API. You cannot proceed without it: ')
        if len(apitoken) == 21:
            return apitoken
        else:
            print('please obtain a valid tenant API token for the Config API before proceeding')
            logging.error(' API Token Error: Length should be 21')
            sys.exit(1)

def getdtTenantURL():
    """ this function gets the Tenant URL, validates it's not empty, and returns it to the dtTenantURL variable"""
    dtTenantURL = input('Enter your Tenant URL (example: foo.live.dynatrace.com): ')
    if len(dtTenantURL) > 0:
        return dtTenantURL
    else:
        dtTenantURL = input('Please enter your Tenant URL. You cannot proceed without it (example: foo.live.dynatrace.com): ')
        if len(dtTenantURL) < 1:
            print('Please obtain a Tenant URL before proceeding (example: foo.live.dynatrace.com).')
            logging.error(' Tenant URL Error: expecting an input of more than 1 character')
            exit(1)
        return dtTenantURL


def validateGetResponse(apitoken, dtTenantURL, validateGetAPI):
    """ this function validates the respnse code of a specified get. Pass any GET api request, along with tenant and token, so long as the headers match.
        Future todo: make the headers an argument passed in when the function is invoked """
    validateGetURL = dtTenantURL + validateGetAPI
    validatgetresponse = requests.get(validateGetURL,headers=get_headers)
    # For known response codes, send a message. Otherwise send generic response code error in the else.
    if validatgetresponse.status_code == 200:
        logging.info(' Validation Check SUCCESSFUL')
        return
    elif validatgetresponse.status_code == 401:
        print('********************************************\n',
              '******************* FAIL *******************\n',
              '********************************************\n',
              'Status code 401 returned. Most likely cause is an invalid token.\n',
              'Please checked you copied a valid token for the supplied tenant.')
        logging.error(' Validation Check: HTTP 401 returned for %s. This is most likely due to an invalid API token for this tenant',validateGetURL)
        sys.exit(1)
    elif validatgetresponse.status_code == 403:
        print('********************************************\n',
              '******************* FAIL *******************\n',
              '********************************************\n',
              'Status code 403 returned. Most likely cause is incorrect permissions on the API token.\n',
              'Please make sure this token has the following privileges: \n',
              '- Read configuration\n',
              '- Write configuration\n',
              '- Capture request data')
        logging.error(' Validation Check: HTTP 403 returned for %s.\n   This is most likely due to incorrect permissions for the API token.\n      Please make sure this token has the following privileges: \n      - Read configuration\n      - Write configuration\n      - Capture request data', validateGetURL)
        sys.exit(1)
    else:
        print('FAIL - status code {0} returned for GET validation against {1} on Tenant {2} with the supplied API token'.format(validatgetresponse.status_code,validateGetAPI,dtTenantURL))
        logging.error(' Validation Check: HTTP %s returned for %s.', validatgetresponse.status_code, validateGetURL)
        sys.exit(1)

def gatherFileList(ParentFile):
    """ This function reads the list of JSON files in the ParentFile to be used to create the configurations and stores them in the  config_json_path list"""
    config_json_path = []
    try:
        with open(ParentFile) as parent_file_list:
            for line in parent_file_list:
                config_json_path.extend([line.rstrip()])
    except Exception as e:
        print('Function gatherFileList: Cannot open file {}'.format(ParentFile))
        logging.error(' Function gatherFileList: Cannot open file %s', ParentFile)
        handleException(e)
    return config_json_path

def getExistingConfigs(ConfigAPIEndpoint, getConfigType):
    """ This function runs a GET against the supplied API EndPoint, either List Custom Services or List Request Attributes, and retrieves a list
    of existing configuration names, storing them in the name_values list. This list is used in functions postConfigs and confirmCreation.
    The purpose is to be able to check for the existence a configuraion that already has the same name. """
    name_values = []
    get_existing_configs_url = dtTenantURL + ConfigAPIEndpoint
    get_configs = requests.get(get_existing_configs_url,headers=get_headers).json()
    for name_key in get_configs[getConfigType]:
        name_values.append(name_key['name'])
    return name_values

def postConfigs(APIEndPoint, NameValues, ConfigJsonPath):
    """ This Function takes the list of JSON files and iterates posting through them. First, it checks the name against name_values (see  function getExistingConfigs).
    If the config name already exists, the new name gets modified by adding today's date to the end. Additionally, for these duplicates, the enable flag is set to False.
    The user should check these duplicates and determine if they want to replace the exisiting one, delete the new one, or merge the two.
    Next, the custom service or request attribute is posted. If a 201 code (success) is not returned, this config is not tried again. For all posts with a 201 result,
    the name and json file are stored in the confirmation_dict dictonary for use in the confirmCreation function. """
    confirmation_dict = {}
    config_iteration = 0
    config_data_len= len(config_json_path)
    config_url = dtTenantURL + APIEndPoint
    while config_iteration < config_data_len:
        try:
            with open(ConfigJsonPath[config_iteration]) as the_JSON_file:
                loaded_JSON_file = json.load(the_JSON_file)
        except Exception as e:
            print('Function postConfigs: could not open the file {}'.format(ConfigJsonPath[config_iteration]))
            logging.error(' Function postConfigs: could not open the file %s', ConfigJsonPath[config_iteration])
            handleException(e)
        if loaded_JSON_file['name'] in NameValues:
            unique_name = loaded_JSON_file['name'] + '_' + today
            logging.info(' %s found in name_values. Creating alternate name: %s', loaded_JSON_file['name'], unique_name)
            # Since the config already exists with the same name, append today's date to the name to create a new version
            loaded_JSON_file['name'] = unique_name
            # Since this is a duplicate, we'll created it, but disable it. The user should revew the new and original to determine
            #   if they want to merge them, or get rid of one.
            loaded_JSON_file['enabled'] = False
        config_post = requests.post(config_url, data=json.dumps(loaded_JSON_file), headers=post_headers)
        logging.info(' postConfigs status code for %s = %s', loaded_JSON_file['name'], config_post.status_code)
        if config_post.status_code != 201:
            logging.warning(' postConfigs: failed to create configuration for %s. Response code = %s', loaded_JSON_file['name'],config_post.status_code)
        else:
            confirmation_dict.update({loaded_JSON_file['name'] : ConfigJsonPath[config_iteration]})
        sleep(10)
        config_iteration += 1
    return confirmation_dict

def confirmCreation(APIEndPoint, CreatedConfigs, success, getExAPIEndPoint, config_type):
    """ This function confirms the creation for all successful config posts in the function postConfig. First, it runs another GET against either the supplied
    list_customservices_api or list_requestattributes_api to gather the most up-to-date list names_list that exist. For all successful (status 201) postConfig items in confirmation_dict,
    this function checks to see if they exist in names_list. If they do, a success message is written to the log. If not, it tries to post again.  If the post does not receive a 201,
    the config is not tried again. If a 201 is retruned, the name and json file path are stored in the dictionary recheck_confirmCreation so this function can be re-run to confirm their existence."""
    if success == True:
        return success
    else:
        success = True
        created_configs = CreatedConfigs
        recheck_confirmCreation = {}
        sleep(10)
        config_url = dtTenantURL + APIEndPoint
        name_values = getExistingConfigs(getExAPIEndPoint ,config_type)
        for key, value in created_configs.items():
            if key in name_values:
                print('Successfully Confirmed {} was created'.format(key))
                logging.info(' ==================================================================\n||------  %s Creation is successfully confirmed\n========================================================================', key)
            else:
                try:
                    with open(value) as the_JSON_file:
                        loaded_JSON_file = json.load(the_JSON_file)
                except Exception as e:
                    print('Function confirmCreation: could not open file {}'.format(value))
                    logging.error(' Function confirmCreation: could not open file %s', value)
                    handleException(e)

                #The JSON file has the original name. If the name was modified previously in the postConfigs function, the JSON file
                # will not have that change. The modified name is reflected in the key value, as it was added to the confirmation_dict
                # in the postConfigs function, or below in the recheck_confirCreation if this is the second execution of this function.
                loaded_JSON_file['name'] = key

                # If the value of today has been added to the config name, previously in postConfig, it is a duplicate.
                #   For this reason, we want to insert it set to not active. This gives the user the ability th review and decide to
                #   keep the original, keep the new, or otherwise merget the two.
                if today in key:
                    loaded_JSON_file['enabled'] = False
                config_post = requests.post(config_url, data=json.dumps(loaded_JSON_file), headers=post_headers)
                if config_post.status_code != 201:
                    logging.warning(' postConfigs: failed to create configuration for %s. Response code = %s', loaded_JSON_file['name'],config_post.status_code)
                else:
                    recheck_confirmCreation.update({key : value})
                sleep(10)
                success = False
        return success, recheck_confirmCreation

# =========================================================
# LOGGER
# =========================================================
logfile = 'log/hybris_config_' + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + '.log'
logging.basicConfig(filename=logfile,format='%(levelname)s:%(message)s',level=logging.INFO)

# =========================================================
# LOAD CONSTANTS file
# =========================================================
"""
The file Constants.txt contains:
    - the variable names and endpoints for the API calls used in this script
    - two URIs for the tenant settings pages where the user is instructed to look to see their handiwork
    - key valuse for reading modifying the name of a config in the config json file
    This file should only be modified if any of these constants have changed.
    The format for an entry is:
        variablename : value
    These will be split, whitespace will removed, and the values will be written to the dictionary constants_dict
"""


with open('Constants.txt') as constants_file:
    for line in constants_file:
        constant_key, constant_value = line.strip('\n').split(':', 1)
        constants_dict[constant_key.strip()] = constant_value.lstrip()

# =========================================================
# GET TENANT URL AND API TOKEN
# =========================================================
#  Testing data, do not leave in
#apitoken = 'uIbCVh2cRdWcnpN0hY_nN'
#dtTenantURL = 'https://aby71138.dev.dynatracelabs.com'


# get user data for making API calls
# Uncomment these when ready to run for real
apitoken = getAPIToken()
dtTenantURL += getdtTenantURL()

# =========================================================
# CONSTANTS
# =========================================================

get_headers = {'Accept':'application/json; charset=utf-8', 'Authorization':'Api-Token {}'.format(apitoken)}
post_headers = {'Content-Type':'application/json; charset=utf-8', 'Authorization':'Api-Token {}'.format(apitoken)}
today = datetime.date.today().strftime("%Y%m%d")

# =========================================================
# WRITE INSTRUCTIONS TO LOG FILE
# =========================================================

with open(logfile, 'a') as the_log_file:
    the_log_file.write('**********************************************************************\n')
    the_log_file.write(' \n')
    the_log_file.write('This is the log file for the Dynatrace Hybris eCommerce Configuration.\n')
    the_log_file.write('In this file you will find several important things. \n')
    the_log_file.write('** The HTTP Status Code of every Post\n')
    the_log_file.write('***** Any POST that does not result in a 201 status code failed and will not be retried.\n')
    the_log_file.write('***** You will have to debug why these failed. To try them again, remove the successful POSTs\n')
    the_log_file.write('***** from the parent file (CustomServiceList.txt or RequsetAttributes.txt) and re-run this script.\n')
    the_log_file.write('\n')
    the_log_file.write('** Other errors or exceptions will be listed.\n')
    the_log_file.write('\n')
    the_log_file.write('IMPORTANT!\n')
    the_log_file.write('** You want to look for the lines containing text like:\n')
    the_log_file.write('***** ---yBusiness Process Task1 Creation is successfully confirmed\n')
    the_log_file.write('***** This indicates all of the succussful posts. Check these against the\n')
    the_log_file.write('***** lists in your parent file to determine if all were created. \n')
    the_log_file.write('\n')
    the_log_file.write('** Any time the name used in the custom service or request attribute already exists in your Dynatrace Tenant,\n')
    the_log_file.write('***** this script will append the date (like "_20180711") to the end of name in the JSON config file. \n')
    the_log_file.write('***** Further, when creating this possible duplicate, the script will set this new configuration to be inactive.\n')
    the_log_file.write('***** Make sure to go to the custom service settings page: {}\n'.format(dtTenantURL + constants_dict['custom_service_path']))
    the_log_file.write('***** or the request attribute settings page: {}\n'.format(dtTenantURL + constants_dict['request_attribute_path']))
    the_log_file.write('***** Determine if you want delete the new config, replace your pre-existing one, or merge the two.\n')
    the_log_file.write('\n')
    the_log_file.write('**********************************************************************\n')
    the_log_file.write('**********************************************************************\n')


# =========================================================
# RUN A GET AGAINST THE API TO CHECK IF THE TENANT AND API TOKEN ARE VAILD
# =========================================================

print('Validating API access on the tenant')
validateGetResponse(apitoken, dtTenantURL, constants_dict['list_customservices_api'])
print('---Validation successful')

# =========================================================
# CREATE CUSTOM SERVICES
# =========================================================
# If you have no custom services to create, comment out this section.

# This file contains the path to the json files of the custom services you want to create.

parent_file_name = 'CustomServiceList.txt'

#Process the parent file - generate config_json_path list which is used to load JSON payloads later.

config_json_path = gatherFileList(parent_file_name)

#Run a GET against the list custom services API to get a name list of existing custom services
# that already exist on the Dynatrace tenant. These will be used to check for pre-existing
# configurations of the same name.

print('Get existing Custom Services')
name_values = getExistingConfigs(constants_dict['list_customservices_api'],constants_dict['custom_srvc_type'])
print('---Get existing Custom Services was successful')


#Iterate through the JSON files in 'CustomServiceList.txt' and do the following:
# Check if service name to be created already exists
#   If name already exists, change name by appending todays date in YYYYMMDD format.
# Create custom service and confirm a 201 response code.
# Returns a list of services created with a 201 response for valdiation in a later step

print('Attempting to create Custom Services')
confirmation_dict = postConfigs(constants_dict['post_customservices_api'], name_values, config_json_path)
print('---Create Custom Services complete')

created_custom_services = confirmation_dict

#After the services are created, this function is called in order to confirm the that the custom services were actually created.
# this step is required for now as there is an issue with stickiness which causes a write not to stick, from time to time.
# if all are present, this step is over. If not, the list of items that had to be submitted again are returned in recheck_confirmCreation

print('Verifying creation of Custom Services')
success = False
success, recheck_confirmCreation = confirmCreation(constants_dict['post_customservices_api'], created_custom_services, success, constants_dict['list_customservices_api'], constants_dict['custom_srvc_type'])

#For all customm services that had to be re-posted in the confirmation step just above, this next function call goes back and checks
# for their successful creation again. It repeats the check and re-submit until it's successful. If there is some other problem,
# this has the potential to create a serious loop.

while success == False:
    success, recheck_confirmCreation = confirmCreation(constants_dict['post_customservices_api'], recheck_confirmCreation, success, constants_dict['list_customservices_api'], constants_dict['custom_srvc_type'])
print('---Custom Services Creation Verification Complete')




# =========================================================
# CREATE REQUEST ATTRIBUTES
# =========================================================
# If you have no request attributes to create, comment out this section.

# This file contains the path to the json files of the custom services you want to create.

parent_file_name = 'RequestAttributeList.txt'

#Process the parent file - generate config_json_path list which is used to load JSON payloads later.

config_json_path = gatherFileList(parent_file_name)


#Run a GET against the list custom services API to get a name list of existing custom services
# that already exist on the Dynatrace tenant. These will be used to check for pre-existing
# configurations of the same name.

print('Get existing Request Attributes')
name_values = getExistingConfigs(constants_dict['list_requestattributes_api'], constants_dict['request_attr_type'])
print('---Get existing Request Attributes was successful')

#Iterate through the JSON files in 'RequestAttributeList.json' and do the following:
# Check if attribute name to be created already exists
#   If name already exists, change name by appending todays date in YYYYMMDD format.
# Create custom service and confirm a 201 response code.
# Returns a list of services created with a 201 response for valdiation in a later step

print('Attempting to create Request Attributes')
confirmation_dict = postConfigs(constants_dict['post_requestattributes_api'], name_values, config_json_path)
print('---Create Request Attributes Services complete')

created_request_attributes = confirmation_dict

#After the attributes are created, this function is called in order to confirm the that the request attributes were actually created.
# this step is required for now as there is an issue with stickiness which causes a write not to stick, from time to time.
# if all are present, this step is over. If not, the list of items that had to be submitted again are returned in recheck_confirmCreation

print('Verifying creation of Request Attributes')
success = False
success, recheck_confirmCreation = confirmCreation(constants_dict['post_requestattributes_api'], created_request_attributes, success, constants_dict['list_requestattributes_api'], constants_dict['request_attr_type'])

#For all request attributes that had to be re-posted in the confirmation step just above, this next function goes back and checks
# for their successful creation again. It repeats the check and re-submit until it's successful.

while success == False:
    success, recheck_confirmCreation = confirmCreation(constants_dict['post_requestattributes_api'], recheck_confirmCreation, success, constants_dict['list_requestattributes_api'], constants_dict['request_attr_type'])
print('---Request Attributes Creation Verification Complete')

# =========================================================
# FINISH
# =========================================================

print(' =========================================================================================================================================\n',
      '|| ................................................................................................................................... ||\n',
      '||  PLEASE CHECK THE LOG FILE {} LOCATED IN THE LOG FOLDER IN THIS DIRECTORY FOR IMPORTANT INFORMATION. ||\n'.format(logfile[4:]),
      '|| ................................................................................................................................... ||\n',
      '=========================================================================================================================================')
