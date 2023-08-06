import sys
import os
import json

TOOLS_FOLDER_NAME = 'tools'
INPUT_PROCESSOR_FOLDER_NAME = os.path.join(TOOLS_FOLDER_NAME, "InputProcessor")
INPUT_FOLDER_NAME = os.path.join(INPUT_PROCESSOR_FOLDER_NAME, "Input")
GIVEN_INPUT_FOLDER_NAME = 'Given_Input'

SENG_PROGRAM_URL = 'https://www.uvic.ca/calendar/undergrad/index.php#/programs/SJKVp7AME?bc=true&bcCurrent=Softw'
HISTORICAL_DATA_INPUT_PATH = os.path.join( sys.path[0], INPUT_FOLDER_NAME, GIVEN_INPUT_FOLDER_NAME,'banner.json')
CORE_COURSES_CSV_PATH = os.path.join(sys.path[0], INPUT_FOLDER_NAME, GIVEN_INPUT_FOLDER_NAME, 'core_courses.csv')
CORE_COURSES_INPUT_PATH = os.path.join(sys.path[0], INPUT_FOLDER_NAME,'core_courses.json')
MODEL_1_INPUT_PATH = os.path.join(sys.path[0], INPUT_FOLDER_NAME, "model_1_input.json")
MODEL_2_INPUT_PATH = os.path.join(sys.path[0], INPUT_FOLDER_NAME, "model_2_input.json")


COMPRESSED_HISTORICAL_DATA_PATH =  os.path.join( sys.path[0], INPUT_FOLDER_NAME, GIVEN_INPUT_FOLDER_NAME,'banner.json.bz2')
HISTORICAL_DATA_OUTPUT_PATH =  os.path.join( sys.path[0], INPUT_FOLDER_NAME, GIVEN_INPUT_FOLDER_NAME,'banner.json')

BASE_FEATURES_CSV_PATH = os.path.join(sys.path[0], INPUT_FOLDER_NAME, GIVEN_INPUT_FOLDER_NAME,'base_features.csv')
BASE_FEATURES_INPUT_PATH = os.path.join(sys.path[0], INPUT_FOLDER_NAME, 'base_features.json')

FINAL_INPUT_FEATURES_CSV_PATH = os.path.join(sys.path[0], INPUT_FOLDER_NAME, GIVEN_INPUT_FOLDER_NAME,'final_model_input_features.csv')
FINAL_INPUT_FEATURES_INPUT_PATH = os.path.join(sys.path[0], INPUT_FOLDER_NAME, 'final_model_input_features.json')

FINAL_OUTPUT_FEATURES_CSV_PATH = os.path.join(sys.path[0], INPUT_FOLDER_NAME, GIVEN_INPUT_FOLDER_NAME,'final_model_output_features.csv')
FINAL_OUTPUT_FEATURES_INPUT_PATH = os.path.join(sys.path[0], INPUT_FOLDER_NAME, 'final_model_output_features.json')

CORE_COURSES_OUTPUT_PATH = CORE_COURSES_INPUT_PATH
BASE_FEATURES_OUTPUT_PATH = BASE_FEATURES_INPUT_PATH
FINAL_INPUT_FEATURES_OUTPUT_PATH = FINAL_INPUT_FEATURES_INPUT_PATH
FINAL_OUTPUT_FEATURES_OUTPUT_PATH = FINAL_OUTPUT_FEATURES_INPUT_PATH

ALL_CORE_COURSES_OUTPUT_PATH = os.path.join(sys.path[0], INPUT_FOLDER_NAME, 'all_core_courses.json')
CLEAN_CORE_COURSE_OUTPUT_PATH = os.path.join(sys.path[0], INPUT_FOLDER_NAME, 'cleaned_core_courses.json')
#get data from json file
#returns: list of dictionaries or 1 dictionary

def get_json(input_file_name):
    '''
    This method creates a dictionary containing the
      contents of a json file
    Input:
        - input_file_name: the json file being read from
    Output:
        -  None
    '''
    print("Reading from json file: " + str(input_file_name) + " ..")
    with open(input_file_name, encoding="utf8") as json_file:
        json_data = json.load(json_file)
    print("Data Loaded Succesfully!")
    #print(len(json_data))
    #makes sure historical data does not have enteries that are missing information
    if input_file_name == HISTORICAL_DATA_INPUT_PATH:
        clean_json = [x for x in json_data if x is not None]
        #print(len(clean_json))
        #print(type(json_data))
        return clean_json
    #print(type(json_data))
    return json_data

def create_json(data, output_file_name):
    '''
    This method creates a json file containing the
      contents of a python dictionary
    Input:
        - data: the dictionary which will be written
        - ouput_file_name: the json file being written to
    Output:
        -  None
    '''
    print("Saving to json file: " + str(output_file_name) + " ..")
    with open(output_file_name, 'w', encoding='utf-8') as json_f:
        json_f.write(json.dumps(data, indent=4))
