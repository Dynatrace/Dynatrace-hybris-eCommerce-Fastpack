
# change error prints to a file write, or both.
# re-evaluate whether each exit should actually exit or continue, writing an out error instead that a specific step failed.


# =========================================================
# REQUIRED LIBRARIES
# =========================================================

import datetime
import getpass
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
config_file_path = []
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
    apitoken = getpass.getpass(prompt='Enter your tenant API token for the Config API: ', stream = None)
    if len(apitoken) == 21:
        return apitoken
    else:
        apitoken = getpass.getpass(prompt='Please enter a valid tenant API token for the Config API. You cannot proceed without it: ', stream = None)
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

def getPLUGINAPIToken():
    """ this function gets the PLUGIN api token, validates it's a length of 21, and returns it to the PLUGINapitoken variable"""
    PLUGINapitoken = getpass.getpass(prompt='Enter your tenant API token for the PLUGIN API: ', stream = None)
    if len(PLUGINapitoken) == 21:
        return PLUGINapitoken
    else:
        PLUGINapitoken = getpass.getpass(prompt='Please enter a valid tenant API token for the PLUGIN API. You cannot proceed without it: ', stream = None)
        if len(PLUGINapitoken) == 21:
            return PLUGINapitoken
        else:
            print('please obtain a valid tenant API token for the PLUGIN API before proceeding')
            logging.error(' PLUGIN API Token Error: Length should be 21')
            sys.exit(1)

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
    """ This function reads the list of files in the ParentFile to be used to create the configurations and stores them in the  config_file_path list"""
    config_file_path = []
    try:
        with open(ParentFile) as parent_file_list:
            for line in parent_file_list:
                config_file_path.extend([line.rstrip()])
    except Exception as e:
        print('Function gatherFileList: Cannot open file {}'.format(ParentFile))
        logging.error(' Function gatherFileList: Cannot open file %s', ParentFile)
        handleException(e)
    return config_file_path

def getExistingConfigs(ConfigAPIEndpoint, getConfigType, NameKey):
    """ This function runs a GET against the supplied API EndPoint, either List Custom Services or List Request Attributes, and retrieves a list
    of existing configuration names, storing them in the name_values list. This list is used in functions postConfigs and confirmCreation.
    The purpose is to be able to check for the existence a configuraion that already has the same name. """
    name_values = []
    get_existing_configs_url = dtTenantURL + ConfigAPIEndpoint
    get_configs = requests.get(get_existing_configs_url,headers=get_headers).json()
    for name_key in get_configs[getConfigType]:
        name_values.append(name_key[NameKey])
    return name_values

def postConfigs(APIEndPoint, NameValues, ConfigJsonPath, NameKey):
    """ This Function takes the list of JSON files and iterates posting through them. First, it checks the name against name_values (see  function getExistingConfigs).
    If the config name already exists, the new name gets modified by adding today's date to the end. Additionally, for these duplicates, the enable flag is set to False.
    The user should check these duplicates and determine if they want to replace the exisiting one, delete the new one, or merge the two.
    Next, the custom service or request attribute is posted. If a 201 code (success) is not returned, this config is not tried again. For all posts with a 201 result,
    the name and json file are stored in the confirmation_dict dictonary for use in the confirmCreation function. """
    confirmation_dict = {}
    config_iteration = 0
    config_data_len= len(ConfigJsonPath)
    config_url = dtTenantURL + APIEndPoint
    while config_iteration < config_data_len:
        try:
            with open(ConfigJsonPath[config_iteration]) as the_JSON_file:
                loaded_JSON_file = json.load(the_JSON_file)
        except Exception as e:
            print('Function postConfigs: could not open the file {}'.format(ConfigJsonPath[config_iteration]))
            logging.error(' Function postConfigs: could not open the file %s', ConfigJsonPath[config_iteration])
            handleException(e)
        if loaded_JSON_file[NameKey] in NameValues:
            unique_name = loaded_JSON_file[NameKey] + '_' + today
            logging.info(' %s found in name_values. Creating alternate name: %s', loaded_JSON_file[NameKey], unique_name)
            # Since the config already exists with the same name, append today's date to the name to create a new version
            loaded_JSON_file[NameKey] = unique_name
            # Since this is a duplicate, we'll created it, but disable it. The user should revew the new and original to determine
            #   if they want to merge them, or get rid of one.
            loaded_JSON_file['enabled'] = False
        config_post = requests.post(config_url, data=json.dumps(loaded_JSON_file), headers=post_headers)
        logging.info(' postConfigs status code for %s = %s', loaded_JSON_file[NameKey], config_post.status_code)
        if config_post.status_code != 201:
            logging.warning(' postConfigs: failed to create configuration for %s. Response code = %s', loaded_JSON_file[NameKey],config_post.status_code)
            print('ERROR: postConfigs: failed to create configuration for {0}. Response code = {1}'.format( loaded_JSON_file[NameKey],config_post.status_code))
        else:
            print('SUCCESS postConfigs status code for {0} = {1}'.format(loaded_JSON_file[NameKey], config_post.status_code))
            confirmation_dict.update({loaded_JSON_file[NameKey] : ConfigJsonPath[config_iteration]})
        config_iteration += 1
    return confirmation_dict

def confirmCreation(APIEndPoint, CreatedConfigs, getAPIEndPoint, config_type, NameKey):
    """ This function confirms the creation for all successful config posts in the function postConfig. First, it runs another GET against either the supplied
     list_customservices_api or list_requestattributes_api to gather the most up-to-date list names_list that exist. For all successful (status 201) postConfig items in confirmation_dict,
     this function checks to see if they exist in names_list. If they do, a success message is written to the log and terminal. If not, an error is written to the log and terminal."""
    if len(CreatedConfigs)==0:
        logging.warning('==================================================================\nERROR: NO configureations created against %s \n========================================================================', getAPIEndPoint)
        print('==================================================================\nERROR: NO configureations created against {} \n========================================================================'.format(getAPIEndPoint))
    else:
        config_url = dtTenantURL + APIEndPoint
        name_values = getExistingConfigs(getAPIEndPoint ,config_type, NameKey)
        for key, value in CreatedConfigs.items():
            if key in name_values:
                print('Successfully Confirmed {} was created'.format(key))
                logging.info(' ==================================================================\n||------  %s Creation is successfully confirmed\n========================================================================', key)
            else:
                logging.warning(' ==================================================================\nERROR: %s NOT CREATED in tenant %s\n========================================================================', key,dtTenantURL)
                print('ERROR {0} NOT CREATED in tenant {1}'.format(key,dtTenantURL))
        return

def postPLUGIN(APIEndPoint, ConfigPLUGINPath):
    """ This Function takes the list of PLUGIN Plugin ZIP files and iterates posting through them. If the PLUGIN Plugin already exist, the post will fail. In order to fix this,
    open the .zip file and change the version number in the pl;ugin.json file. Then rezip the plugin.json file, using the original name of the zip file.
    NOTE - the actual json files in the zip file have to be called plugin.json - hence we name the zip file something more specific. """
    config_iteration = 0
    #config_data_len= len(config_file_path)
    config_data_len= len(ConfigPLUGINPath)
    config_url = dtTenantURL + APIEndPoint
    while config_iteration < config_data_len:
        try:
            loaded_PLUGIN_file = {'file': open(ConfigPLUGINPath[config_iteration], 'rb')}
        except Exception as e:
            print('Function postPLUGIN: could not open the file {}'.format(ConfigPLUGINPath[config_iteration]))
            logging.error('Function postPLUGIN: could not open the file %s', ConfigPLUGINPath[config_iteration])
            handleException(e)
        PLUGIN_post = requests.post(config_url, files=loaded_PLUGIN_file, headers=PLUGIN_post_headers)
        logging.info(' postPLUGIN status code for %s = %s', loaded_PLUGIN_file, PLUGIN_post.status_code)
        print(' postPLUGIN status code for {} = {}'.format(loaded_PLUGIN_file, PLUGIN_post.status_code))
        if PLUGIN_post.status_code != 200:
            logging.warning(' postPLUGIN: failed to create PLUGIN Plugin for %s. Response code = %s', loaded_PLUGIN_file, PLUGIN_post.status_code)
            print('postPLUGIN: failed to create PLUGIN Plugin for {}. Response code = {}'.format(loaded_PLUGIN_file, PLUGIN_post.status_code))
        else:
            print('Succesfully created PLUGIN Plugin for {}'.format(loaded_PLUGIN_file))
            logging.info(' ==================================================================\n||------  %s Creation is successfully confirmed\n========================================================================', loaded_PLUGIN_file)
        config_iteration += 1
    return

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
    the_log_file.write('** Global Request Naming rules can be seen in the Request Naming Rules section of any service ,\n')
    the_log_file.write('***** because they are global. Click the edit ellipsis on any service to access this section \n')
    the_log_file.write('\n')
    the_log_file.write('** JMX Metrics plugins can be seen on the custom plugins page: {}\n'.format(dtTenantURL + constants_dict['plugin_path']))
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
# CREATE PLUGIN
# =========================================================
# If you have no Plugins to create, comment out this section.

# This file contains the path to the ZIP files that contain the plugin.json files you want to import.

parent_file_name = 'jmx_metrics.txt'

#Process the parent file - generate config_file_path list which is used to load ZIP files later.

config_file_path = gatherFileList(parent_file_name)

#Check is there are plugins to be loaded in the jmx_metrics.txt file.
if len(config_file_path) > 0:

#Get the user to input the Plugin API token and create the header
    PLUGINapitoken = getPLUGINAPIToken()
    PLUGIN_post_headers = {'Authorization':'Api-Token {}'.format(PLUGINapitoken)}

# Iterate through the ZIP files in 'jmx_metrics.txt' and import the plugin.json file contained within.
#  If the plugin already exists, this will fail. In that case, extract the plugin.json file from the specific zip file,
#   change the version number, save the plugin.json file and re-zip it as the original zip file name.
#  Aside from a http 200 response the only way to confirm success is by checking in the dynatace gui under
#   Settings -> Monitoring -> Monitored technologied -> Custom Plugins

    print('Attempting to create Plugins')
    postPLUGIN(constants_dict['post_plugin_api'], config_file_path)
    print('---Create Plugins complete')

#If there are no plugins to be imported, output this message
else:
    print('There are no plugins in jmx_metrics.txt to be imported')
    logging.info(' ==================================================================\n||------  There are no plugins in jmx_metrics.txt to be imported\n========================================================================')


# =========================================================
# CREATE CUSTOM SERVICES
# =========================================================
# If you have no custom services to create, comment out this section.

# This file contains the path to the json files of the custom services you want to create.

parent_file_name = 'CustomServiceList.txt'

#Process the parent file - generate config_file_path list which is used to load JSON payloads later.

config_file_path = gatherFileList(parent_file_name)

#Check is there are custom services to be loaded in the CustomServicesList.txt file.
if len(config_file_path) > 0:

#Run a GET against the list custom services API to get a name list of existing custom services
# that already exist on the Dynatrace tenant. These will be used to check for pre-existing
# configurations of the same name.

    print('Get existing Custom Services')
    name_values = getExistingConfigs(constants_dict['list_customservices_api'],constants_dict['custom_srvc_type'],constants_dict['nameKey_custom_svc'])
    print('---Get existing Custom Services was successful')


#Iterate through the JSON files in 'CustomServiceList.txt' and do the following:
# Check if service name to be created already exists
#   If name already exists, change name by appending todays date in YYYYMMDD format.
# Create custom service and confirm a 201 response code.
# Returns a list of services created with a 201 response for valdiation in a later step

    print('Attempting to create Custom Services')
    confirmation_dict = postConfigs(constants_dict['post_customservices_api'], name_values, config_file_path,constants_dict['nameKey_custom_svc'])
    print('---Create Custom Services complete')

    created_custom_services = confirmation_dict

#After the services are created, this function is called in order to confirm the that the custom services were actually created.

    print('Verifying creation of Custom Services')
    confirmCreation(constants_dict['post_customservices_api'], created_custom_services, constants_dict['list_customservices_api'], constants_dict['custom_srvc_type'],constants_dict['nameKey_custom_svc'])
    print('---Custom Services Creation Verification Complete')

#If there are no custom services to be imported, output this message
else:
    print('There are no custom services in CustomServiceList.txt to be imported')
    logging.info(' ==================================================================\n||------  There are no custom services in CustomServiceList.txt to be imported\n========================================================================')



# =========================================================
# CREATE REQUEST ATTRIBUTES
# =========================================================
# If you have no request attributes to create, comment out this section.

# This file contains the path to the json files of the request attributes you want to create.

parent_file_name = 'RequestAttributeList.txt'

#Process the parent file - generate config_file_path list which is used to load JSON payloads later.

config_file_path = gatherFileList(parent_file_name)

#Check is there are request attributes to be loaded in the RequestAttributesList.txt file.
if len(config_file_path) > 0:

#Run a GET against the list request attributes API to get a name list of existing request attributes
# that already exist on the Dynatrace tenant. These will be used to check for pre-existing
# configurations of the same name.

    print('Get existing Request Attributes')
    name_values = getExistingConfigs(constants_dict['list_requestattributes_api'], constants_dict['request_attr_type'],constants_dict['nameKey_request_attr'])
    print('---Get existing Request Attributes was successful')

#Iterate through the JSON files in 'RequestAttributeList.txt' and do the following:
# Check if attribute name to be created already exists
#   If name already exists, change name by appending todays date in YYYYMMDD format.
# Create request attribute and confirm a 201 response code.
# Returns a list of attributes created with a 201 response for valdiation in a later step

    print('Attempting to create Request Attributes')
    confirmation_dict = postConfigs(constants_dict['post_requestattributes_api'], name_values, config_file_path,constants_dict['nameKey_request_attr'])
    print('---Create Request Attributes complete')

    created_request_attributes = confirmation_dict

#After the attributes are created, this function is called in order to confirm the that the request attributes were actually created.

    print('Verifying creation of Request Attributes')
    confirmCreation(constants_dict['post_requestattributes_api'], created_request_attributes, constants_dict['list_requestattributes_api'], constants_dict['request_attr_type'],constants_dict['nameKey_request_attr'])
    print('---Request Attributes Creation Verification Complete')

#If there are no request attributes to be imported, output this message
else:
    print('There are no request attributes in RequestAttributeList.txt to be imported')
    logging.info(' ==================================================================\n||------  There are no request attributes in RequestAttributeList.txt to be imported\n========================================================================')

# # =========================================================
# # CREATE REQUEST NAMING RULES
# # =========================================================
# # If you have no request naming rules to create, comment out this section.

# # This file contains the path to the json files of the request naming rules you want to create.

# parent_file_name = 'RequestNamingList.txt'

# #Process the parent file - generate config_file_path list which is used to load JSON payloads later.

# config_file_path = gatherFileList(parent_file_name)

# #Check is there are request naming rules to be loaded in the RequestNamingList.txt file.
# if len(config_file_path) > 0:

# #Run a GET against the list request naming rules API to get a name list of existing request naming rules
# # that already exist on the Dynatrace tenant. These will be used to check for pre-existing
# # configurations of the same name.

#     print('Get existing Request Naming Rules')
#     name_values = getExistingConfigs(constants_dict['list_requestnamingrules_api'], constants_dict['request_name_type'], constants_dict['nameKey_request_name'])
#     print('---Get existing Request Naming Rules was successful')

# #Iterate through the JSON files in 'RequestNamingList.txt' and do the following:
# # Check if naming rule name to be created already exists
# #   If name already exists, change name by appending todays date in YYYYMMDD format.
# # Create Request Naming Rule and confirm a 201 response code.
# # Returns a list of naming rules created with a 201 response for valdiation in a later step

#     print('Attempting to create Request Naming Rules')
#     confirmation_dict = postConfigs(constants_dict['post_requestnamingrules_api'], name_values, config_file_path, constants_dict['nameKey_request_name'])
#     print('---Create Request Naming Rules complete')

#     created_request_naming_rules = confirmation_dict

# #After the naming rules are created, this function is called in order to confirm the that the request naming rules were actually created.
# # this step is required for now as there is an issue with stickiness which causes a write not to stick, from time to time.
# # if all are present, this step is over. If not, the list of items that had to be submitted again are returned in recheck_confirmCreation

#     print('Verifying creation of Request Naming Rules')
#     confirmCreation(constants_dict['post_requestnamingrules_api'], created_request_naming_rules, constants_dict['list_requestnamingrules_api'], constants_dict['request_name_type'],constants_dict['nameKey_request_name'])
#     print('---Request Naming Rules Creation Verification Complete')

# #If there are no request naming rules to be imported, output this message
# else:
#     print('There are no request attributes in RequestAttributeList.txt to be imported')
#     logging.info(' ==================================================================\n||------  There are no request attributes in RequestAttributeList.txt to be imported\n========================================================================')


# =========================================================
# FINISH
# =========================================================

print(' =========================================================================================================================================\n',
      '|| ................................................................................................................................... ||\n',
      '||  PLEASE CHECK THE LOG FILE {} LOCATED IN THE LOG FOLDER IN THIS DIRECTORY FOR IMPORTANT INFORMATION. ||\n'.format(logfile[4:]),
      '|| ................................................................................................................................... ||\n',
      '=========================================================================================================================================')
