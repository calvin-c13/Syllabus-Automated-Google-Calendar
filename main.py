import os
import glob
import re
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pdfminer.high_level import extract_text



#LOOK AT THIS
#LOOK AT THIS
#LOOK AT THIS
#LOOK AT THIS
#LOOK AT THIS
#LOOK AT THIS
#LOOK AT THIS
#LOOK AT THIS
#LOOK AT THIS
#LOOK AT THIS
#google calendar time zone input COME BACK TO THIS
""" time_zone_input = input("What is your school's time zone? (ex: EST, CST...): ").lower()
time_zone_for_calendar = time_zone_input[0] """

date_of_last_class = input('Date of last day of classes (format: YYYY-MM-DD): ')

# Split the input string into year, month, and day
year, month, day = date_of_last_class.split('-')
year = int(year)
month = int(month)
day = int(day)



#Obtain course name from the first page
def find_first_course_code(pdf_file):
    first_pg_text = extract_text(pdf_file, page_numbers=[0])

    # Regex to find 2 - 4 uppercase letters followed by a space and 3 - 4 digits
    pattern = r'\b[A-Z]{2,4} \d{3,4}\b'
    match = re.search(pattern, first_pg_text)

    if match:
        course_name = match.group()
    
    while True:
        real_course_name = input(f'Course name: {course_name} \nCorrect name? (yes/no): ').lower()

        if real_course_name.startswith('y'):
            break
        elif real_course_name.startswith('n'):
            course_name = input('Correct course name: ')
            break
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")
    return course_name




def instruction_mode(lower_text):
    if 'asynchronous' in lower_text:
        return 'online_asynch'
    elif 'synchronous' in lower_text:
        return 'online_synch'
    else:
        return 'in_person'




def lab_existence(lower_text):
    return any(word in lower_text for word in ['lab ', 'labs '])

def quiz_existence(lower_text):
    return any(word in lower_text for word in ['quiz ', 'quizzes '])

def exam_existence(lower_text):
    exam_words = ['midterm', 'exam', 'final exam ', 'final ', 'final project', 'final draft']
    return any(word in lower_text for word in exam_words)



#run if instruction_mode is in person or online synch
def get_days(prompt):
    valid_days = ['SU', 'MO', 'TU', 'WE', 'TH', 'FR', 'SA']

    while True:
        input_days = input(prompt).lower().split()

        # Check if all input days are valid
        if all(day[0:2].upper() in valid_days for day in input_days):
            return [day[0:2].upper() for day in input_days]
        else:
            print('Invalid input. Please enter valid days.')


def start_and_end_time(start_prompt, end_prompt):
    while True:
        try:
            start_time = input(start_prompt)
            end_time = input(end_prompt)

            # Validate the format of start and end time
            datetime.strptime(start_time, '%H:%M')
            datetime.strptime(end_time, '%H:%M')

            return start_time, end_time
        except ValueError:
            print('Invalid input. Please enter valid military time (HH:MM).')




def number_of_quizzes():
    quantity_of_quizzes = int(input('Number of quizzes: '))
    list_of_quiz_dates = {}

    for quiz_number in range(1, quantity_of_quizzes + 1):
        quiz_date = input(f'Quiz {quiz_number} date (format: MM-DD): ')
        list_of_quiz_dates[f'Quiz {quiz_number} date'] = quiz_date

    return list_of_quiz_dates




def number_of_exams():
    quantity_of_exams = int(input('Number of exams (including final exam): '))
    list_of_exam_dates = {}

    for exam_number in range(1, quantity_of_exams):
        exam_date = input(f'Midterm {exam_number} date (format: MM-DD): ')
        list_of_exam_dates[f'Midterm {exam_number} date'] = exam_date

    # If there is only one exam left, treat it as the final exam
    if quantity_of_exams > 0:
        final_exam_date = input('Final exam date (format: MM-DD): ')
        final_start_time, final_end_time = start_and_end_time('Final exam start time (HH:MM): ', 'Final exam end time (HH:MM): ')

        list_of_exam_dates['Final exam date'] = final_exam_date
        list_of_exam_dates['Final exam start time'] = final_start_time
        list_of_exam_dates['Final exam end time'] = final_end_time

    return list_of_exam_dates







#Iterating over each pdf file in the folder
def iterate_over_pdf(folder_name):
    pdf_pattern = os.path.join(folder_name, '*.pdf')
    pdf_files = glob.glob(pdf_pattern)

    for pdf_file in pdf_files:
        #delete later
        print(end = '\n')

        lower_text = extract_text(pdf_file).lower()

        print(find_first_course_code(pdf_file))
        course_instruction_mode = instruction_mode(lower_text)

        # Lecture prompt
        if course_instruction_mode == 'in_person' or course_instruction_mode == 'online_synch':
            lecture_days = get_days('Lecture meeting day(s) (separated by spaces, ex: "sun tues thurs"): ')
            start_and_end_time('Lecture start time (HH:MM): ', 'Lecture end time (HH:MM): ')

        if course_instruction_mode == 'in-person':
            lecture_location = input('Lecture location: ')



        print(lab_existence(lower_text))
        # Lab prompts if applicable
        if lab_existence(lower_text):
            lab_days = get_days('Lab meeting day(s) (separated by spaces, ex: "sun tues thurs"): ')
            start_and_end_time('Lab start time (HH:MM): ', 'Lab end time (HH:MM): ')
            lab_location = input('Lab location: ')


        print(quiz_existence(lower_text))
        #Quiz prompts if applicable
        if quiz_existence(lower_text):
            number_of_quizzes()

        print(exam_existence(lower_text))
        #Exam prompts if applicable
        if exam_existence(lower_text):
            number_of_exams()
        




# Specify the folder name
#make it input('Enter the folder name that contains your course syllabuses: ')
folder_name = 'syllabus examples'
iterate_over_pdf(folder_name)





