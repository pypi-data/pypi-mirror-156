# !RP/!JC - Fill in these methods. We made need to adjust the parameters/output
#           format.

import json
import string
from tools.InputProcessor import DataProcessor

def parse_input_for_sizer(backend_input_data) -> dict:
    # Dictionary, where keys are courses e.g. "CSC111" and values are dicts.
    # Each dict within a course contains the following structure:
    # {
    #   "1": 10,
    #   "2": 10,
    #   "2T": 10,
    #   "3": 10,
    #   "4": 10,
    #   "5": 10,
    #   "6": 10,
    #   "7": 10,
    #   "Enrolment": 50,
    #   "Maximum Enrolment": 60,
    #   "Year": 2008
    pass

# ENUM: 0, 1, 2 for Fall Spring Summer

def parse_input_for_sequencer(input_data) -> dict:
    # Outermost: Dictionary, where keys are courses e.g. "CSC111" and values are dicts.
    # Each dict within a course contains the following structure:
    # {
    #   "1": 10,
    #   "2": 10,
    #   "2T": 10,
    #   "3": 10,
    #   "4": 10,
    #   "5": 10,
    #   "6": 10,
    #   "7": 10,
    #   "Fall Enrolment": 50,
    #   "Fall Maximum Enrolment": 60,
    #   "Spring Enrolment": 50,
    #   "Spring Maximum Enrolment": 60,
    #   "Summer Enrolment": 50,
    #   "Summer Maximum Enrolment": 60,
    #   "Year Enrolment": 50,
    #   "Year Maximum Enrolment": 60,
    #   "Year": 2008
    pass

def parse_output_for_backend(predictor_output: dict, prev_year: int, dummy: bool) -> dict:
    # predictor_output:
    #
    # Outermost: Dictionary, where keys are courses e.g. "CSC111" and values are lists of numpy arrays.
    # Each list contains 3 numpy arrays with values(capacities for all sections): Fall Maximum Enrolment, Spring Maximum Enrolment, Summer Maximum Enrolment.
    # Example: {"CSC111": [[150], [100], [80]], "CSC115": [[250], [200], [150]], "MATH100": [[250, 250, 250], [80, 80], [70]]....}
    #
    # Return Value:
    # Refer to Data Model.
    
    fall_offerings = []
    spring_offerings = []
    summer_offerings = []

    if dummy: return(build_dummy_schedule())

    first_year_copy = get_prev_year_course_data(prev_year)
    predictor_output.update(first_year_copy)

    for key in predictor_output:
        value = predictor_output[key]
        
        # if value[0] is non-empty then the course sections contained there should be scheduled in the FALL semester.
        if value[0] != []: 
            fall_offerings.append(build_offering_dict(key, value[0]))
        # if value[1] is non-empty then the course sections contained at there should be scheduled in the SPRING semester.
        if value[1] != []:
            spring_offerings.append(build_offering_dict(key, value[1]))
        # if value[2] is non-empty then the course sections contained at there should be scheduled in the SUMMER semester.
        if value[2] != []:
            summer_offerings.append(build_offering_dict(key, value[2]))

    return {"fall": fall_offerings,
            "spring": spring_offerings,
            "summer": summer_offerings}

def build_offering_dict(course_code: string, sections: list) -> dict:
    offering_dict = {
        "course": {
            "code": course_code,
            #TODO: !RP can we add the course title to the core courses csv?
            "title": "",
            "pengRequired": False
        },
        "sections": []
    }
    for capacity in sections:
        offering_dict['sections'].append({
            "professor": None,
            "capacity": capacity,
            "timeSlots": None
        })
    
    return(offering_dict)

#TODO: !RP Don't know if we still need this? passing dummy data to parse_output_for_backend() instead of a 'dummy' flag will do the same thing.
def build_dummy_schedule(prev_first_year_data: dict) -> dict:
    print("you are a dummy!")
    return({})

def get_prev_year_course_data(current_year):
    data_processor = DataProcessor.DataProcessor()
    complete_core_courses = data_processor.get_historical_clean_core_course_offerings()

    combined_dict = {}
    #TODO: get timeslots for these first year courses/sections.

    for course in complete_core_courses:
        if(course['courseNumber'][0] == '1' and course['subject'] != 'CSC' and course['subject'] != 'SENG'):
            if course['subjectCourse'] in combined_dict:
                if(course['term_year'] == str(current_year) and course['semester'] == '09'): # fall
                    combined_dict[course['subjectCourse']][0].append(course['maximumEnrollment'])
                if(course['term_year'] == str(current_year) and course['semester'] == '01'): # spring
                    combined_dict[course['subjectCourse']][1].append(course['maximumEnrollment'])
                if(course['term_year'] == str(current_year) and course['semester'] == '05'): # summer
                    combined_dict[course['subjectCourse']][2].append(course['maximumEnrollment'])
            else:
                if(course['term_year'] == str(current_year) and course['semester'] == '09'): # fall
                    combined_dict[course['subjectCourse']] = [[course['maximumEnrollment']],[],[]]
                if(course['term_year'] == str(current_year) and course['semester'] == '01'): # spring
                    combined_dict[course['subjectCourse']] = [[],[course['maximumEnrollment']],[]]
                if(course['term_year'] == str(current_year) and course['semester'] == '05'): # summer
                    combined_dict[course['subjectCourse']] = [[],[],[course['maximumEnrollment']]]

    # out_file1 = open("combined.json", "w")
    # json.dump(combined_dict, out_file1, indent = 4)

    return(combined_dict)

# def main():
#     result = parse_output_for_backend({"CSC111": [[100], [150], []], "CSC115": [[100], [150], []], "SENG370": [[100], [150], [20]], "ECE260": [[100], [150], [60]]}, 2022, False)
#     out_file = open("dummy_out.json", "w")
#     json.dump(result, out_file, indent=6)

#     if result != None:
#         print(result)

# if __name__ == '__main__':
#     main()