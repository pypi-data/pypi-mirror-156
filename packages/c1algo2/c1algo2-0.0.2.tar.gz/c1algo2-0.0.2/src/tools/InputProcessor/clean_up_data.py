import json
import bz2

#decompress json file containing historical offerings from .bz file
with open('./Input/Given_Input/banner.json', 'wb') as new_file, bz2.BZ2File('./Input/Given_Input/banner.json.bz2', 'rb') as file:
    decompressor = bz2.BZ2Decompressor()
    for data in iter(lambda: file.read(100*1024), b''):
        new_file.write(data)

data_file = open('./Input/Given_Input/banner.json', 'r')
semester_json = json.load(data_file)

filtered = []
filtered_by_course = {}

# CENG 412 maps to ECE 440
# CENG 420 to ECE 470
# CENG 421 to ECE 471
# CENG 450 to ECE 449
# CENG 453 to ECE 457
# CENG 460 to ECE 458
# CENG 461 to ECE 463
# CENG 496?
# ECE 498 is merged CENG 498 and ELEC 498
# ECE 499 is merged CENG 499 and ELEC 499

for datum in semester_json:
    if datum is not None:
        if (datum['subject'] == 'SENG' or datum['subject'] == 'CSC' or datum['subject'] == 'ECE') and datum['scheduleTypeDescription'] == 'Lecture':
            filtered_datum = {
                'term': datum['term'],
                'subject': datum['subject'],
                'courseNumber': datum['courseNumber'],
                'sequenceNumber': datum['sequenceNumber'],
                'scheduleTypeDescription': datum['scheduleTypeDescription'],
                'courseTitle': datum['courseTitle'],
                'maximumEnrollment': datum['maximumEnrollment'],
                'enrollment': datum['enrollment'],
                'seatsAvailable': datum['seatsAvailable'],
                'subjectCourse': datum['subjectCourse']
            }
                
            filtered.append(filtered_datum)

        if (datum['subject'] == 'CENG' or datum['subject'] == 'ELEC') and datum['scheduleTypeDescription'] == 'Lecture':
            if datum['subjectCourse'] == 'CENG412':
                datum['courseNumber'] == '440'
            elif datum['subjectCourse'] == 'CENG420':
                datum['courseNumber'] == '470'
            elif datum['subjectCourse'] == 'CENG421':
                datum['courseNumber'] == '471'
            elif datum['subjectCourse'] == 'CENG450':
                datum['courseNumber'] == '449'
            elif datum['subjectCourse'] == 'CENG453':
                datum['courseNumber'] == '457'
            elif datum['subjectCourse'] == 'CENG460':
                datum['courseNumber'] == '458'
            elif datum['subjectCourse'] == 'CENG461':
                datum['courseNumber'] == '463'

            filtered_datum = {
                'term': datum['term'],
                'subject': 'ECE',
                'courseNumber': datum['courseNumber'],
                'sequenceNumber': datum['sequenceNumber'],
                'scheduleTypeDescription': datum['scheduleTypeDescription'],
                'courseTitle': datum['courseTitle'],
                'maximumEnrollment': datum['maximumEnrollment'],
                'enrollment': datum['enrollment'],
                'seatsAvailable': datum['seatsAvailable'],
                'subjectCourse': 'ECE' + datum['courseNumber']
            }
                
            filtered.append(filtered_datum)

filtered_file = open('./Input/Given_Input/banner_clean.json', 'w')

filtered_file.write(json.dumps(filtered, indent=4))

filtered_file.close()
data_file.close()
