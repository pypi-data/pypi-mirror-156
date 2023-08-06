import csv
import tools.InputProcessor.ConfigThings as ConfigThings
import bz2


def create_core_json(csv_input_path, json_output_path):
    '''
    This method creates a json file containing all the SENG core courses
    Input:
        - csv_input_path: csv file containing the names of all the SENG core courses
    Output: 
        - json_output_path: json file containing the names of all the SENG core courses
    '''
    data = {}
    total_courses = 0
    print("Reading from csv file: " + str(csv_input_path) + " ..")
    with open(csv_input_path, 'r', encoding='utf-8-sig') as csv_f:
        csv_data = csv.DictReader(csv_f)
        for rows in csv_data:
            key = rows['course_name']
            data[key] = rows
            total_courses = total_courses + 1
    print("Total Core Courses Found: " + str(total_courses))
    ConfigThings.create_json(data, json_output_path)

def create_feature_json(csv_input_path, json_output_path):
    '''
    This method creates a json file containing all 
      the features of a course that will be tracked
    Input:
        - csv_input_path: csv file containing the names of all 
          the features of a course that will be tracked
    Output: 
        - json_output_path: json file containing the names of all 
          the features of a course that will be tracked
    '''
    data = []
    total_features = 0
    print("Reading from csv file: " + str(csv_input_path) + " ..")
    with open(csv_input_path, 'r', encoding='utf-8-sig') as csv_f:
        csv_data = csv.reader(csv_f)
        for row in csv_data:
            for cell in row:
                if cell != '':
                    data.append(cell)
                    total_features = total_features + 1
    print("Total Features Found: " + str(total_features))
    ConfigThings.create_json(data,json_output_path)
            
def decompress_file(compressed_input_file_path, output_file_path):
    '''This function decompresses a bz file'''
    with open(output_file_path, 'wb') as new_file, bz2.BZ2File(compressed_input_file_path, 'rb') as file:
        decompressor = bz2.BZ2Decompressor()
        for data in iter(lambda: file.read(100*1024), b''):
            new_file.write(data)


if __name__ == '__main__':
    create_core_json(ConfigThings.CORE_COURSES_CSV_PATH, ConfigThings.CORE_COURSES_OUTPUT_PATH)
    create_feature_json(ConfigThings.BASE_FEATURES_CSV_PATH, ConfigThings.BASE_FEATURES_OUTPUT_PATH)
    decompress_file(ConfigThings.COMPRESSED_HISTORICAL_DATA_PATH, ConfigThings.HISTORICAL_DATA_OUTPUT_PATH)