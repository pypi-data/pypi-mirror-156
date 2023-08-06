import numpy as np
from sklearn import semi_supervised
from sklearn.linear_model import LinearRegression
from tools.InputProcessor import ConfigThings
from tools.InputProcessor import DataProcessor

# !OA - Do we really want to use tools in our main workflow? Can we duplicate
#       this functionality into src so we can have tools as a top-level folder
#       (along with src and test).

def create_model_inputs():
    """creates DataProcessor Object which initializes model input data
    """
    data_processor = DataProcessor.DataProcessor()
    complete_historical_core_courses = data_processor.get_historical_clean_core_course_offerings()
    model_1_input, model_2_input = data_processor.get_historical_core_courses(complete_historical_core_courses)
    data_processor.print_model_1_input_to_json(model_1_input)
    data_processor.print_model_2_input_to_json(model_2_input)
    return model_1_input, model_2_input, data_processor.core_course_names

def process_model_1_input(model_1_input):
    """Creates Model_1_input (ALl Courses) Object which initializes formats model 1 input data
    """
    x_years = {}
    y_enrollments = {}
    for course in model_1_input:
        x_years[course], y_enrollments[course] = create_model_1_input(model_1_input[course])
    return x_years ,y_enrollments

def create_model_1_input(course):
    """Creates Model_1_input (1 course) 
    """
    x_year = [] # x_year[i] = course[year].key()[ij] (year i, semester j)
    y_enrollment = [] # y_enrollment[i] = course[year][semester]["maximumEnrollment"]
    for i_year in course:
        for semester in course[i_year].values():
            if semester:
                x_year.append(int(i_year))
                y_enrollment.append(int(semester["maximumEnrollment"]))
    x_year = np.array(x_year, dtype=np.int32).reshape(-1,1)
    y_enrollment = np.array(y_enrollment, dtype=np.int32)
    return x_year, y_enrollment
    
def round_floats_to_ints(float_list):
    int_list = []
    for float_value in float_list:
        int_value = round(float_value)
        int_list.append(int_value)
    return int_list

def main(verbose=False):
    model_1_inputs, model_2_inputs, core_course_names =  create_model_inputs()
    x_years, y_enrollments = process_model_1_input(model_1_inputs)
    model = LinearRegression()
    for course in core_course_names:
        model.fit(x_years[course], y_enrollments[course])
        r_sq = model.score(x_years[course],y_enrollments[course])
        y_pred_floats = model.predict(x_years[course])
        y_pred = round_floats_to_ints(y_pred_floats)
        if verbose:
            print("    **** "+ str(course) + " Predicted Sizes ****")
            for input, pred in zip(x_years[course],y_pred):
                print("Year: " + str(int(input)) + "    Prediction:" + str(pred))
    # !OA/!JS - We should return a dict of output here.
    return {"Real": "Data"}

if __name__ == '__main__':
    main()