from anyio import SemaphoreStatistics
import tools.InputProcessor.Helper as Helper
from tools.InputProcessor.ConfigThings import *
from functools import partial, total_ordering
import os
import sys

# We should not be printing verbosely if this is called from an external component (such as the main workflow).
is_main = (__name__ == "__main__")
if not is_main:
    f = open(os.devnull, 'w')
    sys.stdout = f

class DataProcessor():
    """ In charge of Processing Data for Predictor
    """
    def __init__(self):
        self.setup_input_files()
        self.setup_input_dictionaries()
        self.core_course_names = self.create_core_course_names_list(self.core_courses_dict)
        self.core_course_indicies_dict = self.create_core_course_indicies_dict(self.core_course_names)
    
    def setup_input_files(self):
        """ Creates all files necessary for the model's input data
            to be extracted
        """
        #create json file containing core courses from .csv file
        Helper.create_core_json(CORE_COURSES_CSV_PATH, CORE_COURSES_OUTPUT_PATH)
        #create json file containing base features from .csv file
        Helper.create_feature_json(BASE_FEATURES_CSV_PATH, BASE_FEATURES_OUTPUT_PATH)
        #create json file containing final input features for predictive model from .csv file
        Helper.create_feature_json(FINAL_INPUT_FEATURES_CSV_PATH, FINAL_INPUT_FEATURES_OUTPUT_PATH)
        #create json file containing final output features for predictive model from .csv file
        Helper.create_feature_json(FINAL_OUTPUT_FEATURES_CSV_PATH, FINAL_OUTPUT_FEATURES_OUTPUT_PATH)
        #decompress json file containing historical offerings from .bz file
        Helper.decompress_file(COMPRESSED_HISTORICAL_DATA_PATH, HISTORICAL_DATA_OUTPUT_PATH)

    def setup_input_dictionaries(self):
        """" Creates all dictionaries necessary for the model's input
             data to be extracted
        """
        #create list containing names of core SENG courses from .json file
        self.core_courses_dict = get_json(CORE_COURSES_INPUT_PATH)
        #create list containing names of base features from .json file
        self.base_features = get_json(BASE_FEATURES_INPUT_PATH)
        #create list containing names of final input features of prediction model
        self.final_input_features = get_json(FINAL_INPUT_FEATURES_INPUT_PATH)
        #create list containing names of final output features of prediction model
        self.final_output_features = get_json(FINAL_OUTPUT_FEATURES_OUTPUT_PATH)

    def create_core_course_names_list(self, core_courses_dict):
        '''
            This method creates a list of the names of all core_courses
            using a dictionary containing all the core courses
            Input:
                - core_courses_dict: dictionary containing all core courses and 
                    their attributes
            Output:
                - core_courses: list of core course names
        '''
        core_courses = [x for x in core_courses_dict if x is not None]
        return core_courses
    
    def create_core_course_indicies_dict(self, core_courses):
        index = 1
        core_course_indicies_dict = {}
        for core_course in core_courses:
            core_course_indicies_dict[core_course] = index
            index = index + 1
        return core_course_indicies_dict

    def get_historical_clean_core_course_offerings(self):
        """ Retrieves all historical offferings
        """
        historical_offerings = get_json(HISTORICAL_DATA_INPUT_PATH)
        f1_1 = lambda offering: self.remove_useless_offering_features(offering, self.base_features)
        clean_historical_core_course_offerings = self.extract_historical_core_offerings_list(f1_1, historical_offerings, self.core_courses_dict)
        complete_historical_core_course_offerings = self.add_offering_features(clean_historical_core_course_offerings, self.core_courses_dict )
        return complete_historical_core_course_offerings
    
    #calls functions 2
    def get_historical_core_courses(self, historical_core_course_offeirngs):
        """ Retrieves all historical courses
        """
        historical_core_courses = self.extract_all_historical_core_courses(historical_core_course_offeirngs, self.core_course_names)
        f2_1 = lambda core_course_years : self.remove_model_1_unwanted_features(core_course_years)
        f3_1 = lambda core_course_years, semester: self.group_all_courses_by_semester_helper(core_course_years, semester, self.final_input_features)
        yearly_course_offerings, model_1_input = self.group_all_courses_by_year(f2_1, historical_core_courses, self.core_course_names)
        model_2_input = self.group_all_courses_by_semester(f3_1, yearly_course_offerings)
        return model_1_input, model_2_input
    

    #functions 2
    def core_course_offering_check(self, offering, core_course_names):
        '''
        This method checks if a course is a core course
        Input: 
            - offering: a course offering (dictionary)
            - core_course_namess: list of names of core SENG courses
        Output:
            - True: if offering belongs to a core course
            - False: otherwise
    '''
        for row in core_course_names:
            if offering["subjectCourse"] in row:
                return True
        return False

    def add_offering_features(self, historical_core_course_offerings, core_courses):
        complete_offerings = []
        for offering in historical_core_course_offerings:
            offering["term_year"] = offering["term"][0:4]
            offering["semester"] = offering["term"][4:6]
            del offering["term"]
            offering["course_year"] = core_courses[offering["subjectCourse"]]["course_year"]
            offering["course_faculty"] =  core_courses[offering["subjectCourse"]]["course_faculty"]
            offering["course_substitutions"] =  core_courses[offering["subjectCourse"]]["course_substitutions"]
            complete_offerings.append(offering)
        return complete_offerings

    def extract_historical_core_offerings_list(self, f1_1, historical_offerings, core_courses_dict ):
        """
    This method extracts  all core course offerings found in all historical
     offerings
    Input:
        - historical_core_offerings: List of offerings (dictionaries) offered historically
        - core_courses_dict: dictionary containing core SENG courses and their information
    Output:
        - historical_core_offerings: list of dictionaries containing offerings in core SENG
            courses offered historically
    """
        print("Retreiving All Core Courses Offered Historically..")
        historical_core_course_offerings = []
        core_course_names = self.create_core_course_names_list(core_courses_dict)
        for offering in historical_offerings:
            #skip all offerings that are not a lecture
            if not self.offering_is_lecture(offering):
                continue
            if self.core_course_offering_check(offering, core_course_names):
                offering = f1_1(offering)
                historical_core_course_offerings.append(offering)
        print("Total Core Course Offerings: " + str(len(historical_core_course_offerings)) + " out of " + str(len(historical_offerings)) + " Offerings")    
        return historical_core_course_offerings

    def extract_historical_core_course(self, historical_core_offerings, core_course_name):
        '''
        This method extracts one core course's historical offerings from all
        from all historical core SENG course offerings
        Input:
            - historical_core_offerings: List of all core SENG courses' historical
                offerings
            - core_course_name: name of a core SENG course
        '''
        core_course_offers = []
        for hist_core_offering in historical_core_offerings:
            if str(hist_core_offering["subjectCourse"]) == str(core_course_name):
                core_course_offers.append(hist_core_offering)
        return core_course_offers

    def extract_all_historical_core_courses(self, historical_core_offerings, core_course_names):
        '''
        This method extracts a dictionary of core SENG courses, where each course is
            represented by a list of offerings. Each offerings is a dictionary
        Input:
            - historical_core_offerings: List of all core SENG course historical
                offerings
            - core_course_names: List of the names of all core SENG courses
        Output:
            - historical_core_courses: Dictionary of all core SENG courses' 
                historical offerings
        '''
        historical_core_course_offerings = []
        historical_core_courses = {}
        for core_course_name in core_course_names:
            historical_core_course_offerings = self.extract_historical_core_course(historical_core_offerings, core_course_name)
            historical_core_courses[historical_core_course_offerings[0]["subjectCourse"]] = historical_core_course_offerings
        return historical_core_courses

    def group_all_courses_by_year(self, f2_1, historical_core_courses, core_courses_names):
        '''
        This function groups all core SENG course offerings by course name and
        the year the course was offered
        Input:
            - historical_core_courses: Dictionary of all core SENG courses' 
                historical offerings
            - core_courses_dict: dictionary containing core SENG courses and their information
        Output:
            - yearly_core_courses: Dictionary containing all offerings for a core SENG course,
                each core SENG course is further organized by the year an offer was made'''
        print("Grouping Offerings for each Course by Year")
        yearly_core_courses = {}
        model_1_input = {}
        for core_course in core_courses_names:
            yearly_course_offerings = {} #dictionary of all offerings for a course by  year
            model_1_course = {}
            for year in range(2008,2023):
                year_offerings_list = [] # list of all offerings for a course in a year
                model_1_year = {}
                for offering in historical_core_courses[core_course]:
                    if offering['term_year'] == str(year):
                        year_offerings_list.append(offering)
                yearly_course_offerings[year] = year_offerings_list
                model_1_year[year] = f2_1(yearly_course_offerings[year])
                model_1_course[year] = model_1_year
            model_1_input[core_course] = model_1_course
            yearly_core_courses[core_course] = yearly_course_offerings
        return yearly_core_courses, model_1_input

    def group_all_courses_by_semester(self, f3_1, historical_core_courses_yearly):
        print("Grouping Offerings for each year of a course by semester..")
        SEMESTER_VALUES = ["Fall", "Spring", "Summer"]
        model_2_input = {}
        for core_course in self.core_course_names:
            if historical_core_courses_yearly[core_course]:
                model_2_course = {}
                for i_year in range(2008,2023):
                    if historical_core_courses_yearly[core_course][i_year]:
                        model_2_year = {}
                        for semester in SEMESTER_VALUES:
                            model_2_semester = {}
                            model_2_semester = f3_1(historical_core_courses_yearly[core_course][i_year], semester)
                            if model_2_semester:
                                model_2_year[semester] = model_2_semester
                        model_2_course[i_year] = model_2_year
                model_2_input[core_course] = model_2_course
        return model_2_input                    

#helper functions
    def find_total_offerings_for_course(self, course):
        total_offerings = 0
        for offering in course:
            total_offerings = self.add_to_total_offerings(total_offerings)
        return total_offerings

    def add_to_total_offerings(self, total_offerings):
        return total_offerings + 1
    
    def add_to_total_offerings_size(self, offering_size, total_enrollment):
        return total_enrollment + offering_size

    def add_to_total_seats(self, seats, total_seats):
        return total_seats + seats

    def offering_is_lecture(self, offering):
        if offering["scheduleTypeDescription"] == "Lecture":
            return True
        else:
            return False

    def rename_semester_feature(self, offering):
        if offering["semester"] == "01":
            offering["semester"] = "Spring"
        if offering["semester"] == "05":
            offering["semester"] = "Summer"
        if offering["semester"]  == "09":
            offering["semester"] = "Fall"
        return offering

    def create_model_1_input(self, core_course_year):
        total_seats = 0
        total_offerings_size = 0
        total_offerings = 0
        for offering in core_course_year:
            total_seats = self.add_to_total_seats(offering["enrollment"], total_seats)
            total_offerings_size = self.add_to_total_offerings_size(offering["maximumEnrollment"], total_offerings_size)
            total_offerings = self.add_to_total_offerings(total_offerings)
        return total_seats, total_offerings_size, total_offerings

#lambda functions
    #f1_1
    def remove_useless_offering_features(self, offering, base_features):
        clean_offering = {feature: offering[feature] for feature in base_features}
        return clean_offering
    #f2_1
    def group_all_courses_by_year_helper(self, core_course_dicts, year,final_input_features):
        """
        """
        for offering in core_course_dicts:
            offering = self.rename_semester_feature(offering)

    #f2_1
    def remove_model_1_unwanted_features(self, core_course_year):
        new_core_course_semester = {}
        total_seats = 0
        total_offerings_size = 0
        total_offerings = 0
        total_seats, total_offerings_size, total_offerings = self.create_model_1_input(core_course_year)
        if total_seats != 0:
            new_core_course_semester["maximumEnrollment"] = total_offerings_size
            new_core_course_semester["totalEnrollment"] = total_seats
        return new_core_course_semester
        
    #f3_1
    def group_all_courses_by_semester_helper(self, core_course_years, semester, final_input_features):
        semester_offerings_list = []
        for offering in core_course_years:
            offering = self.rename_semester_feature(offering)
            if offering["semester"] == semester:
                clean_offering = {feature: offering[feature] for feature in final_input_features}
                semester_offerings_list.append(clean_offering)

        return semester_offerings_list

    def print_model_1_input_to_json(self, model_input):
        create_json(model_input, MODEL_1_INPUT_PATH)
    
    def print_model_2_input_to_json(self, model_output):
        create_json(model_output, MODEL_2_INPUT_PATH)