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



""" #initializing lab, quiz, and exam existence
lab_existence_bool = False
quiz_existence_bool = False
exam_existence_bool = False """

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
    #initializing instruction mode
    in_person = False
    online_synch = False
    online_asynch = False

    if 'asynchronous' in lower_text:
        online_asynch = True
    elif 'synchronous' in lower_text:
        online_synch = True
    else:
        in_person = True

    # Return the variable that is True
    if online_asynch:
        return 'online_asynch'
    elif online_synch:
        return 'online_synch'
    else:
        return 'in_person'



#Obtain existence of lab
def lab_existence(lower_text):
    lab_words = ['lab ', 'labs ']

    # searching for lab in text
    for word in lab_words:
        if word in lower_text:
            return True

    return False

#Obtain existence of quizzes
def quiz_existence(lower_text):
    quiz_words = ['quiz ', 'quizzes ']

    #searching for quiz in text
    for word in quiz_words:
        if word in lower_text:
            return  True

    return False


#Obtain existence of exams
def exam_existence(lower_text):
    exam_words = ['midterm', 'exam', 'final exam ', 'final ', 'final project', 'final draft']

    #searching for exam in text
    for word in exam_words:
        if word in lower_text:
            return True

    return False


#run if instruction_mode is in person or online synch
def get_days(prompt):
    valid_days = ['SU', 'MO', 'TU', 'WE', 'TH', 'FR', 'SA']

    while True:
        input_days = input(prompt).lower().split()

        # Check if all input days are valid
        if all(day[0:2].upper() in valid_days for day in input_days):
            return [day[0:2].upper() for day in input_days]
        else:
            print("Invalid input. Please enter valid days.")


def start_and_end_time(start_prompt, end_prompt):
    while True:
        try:
            start_time = input(start_prompt)
            end_time = input(end_prompt)

            # Validate the format of start and end time
            datetime.strptime(start_time, "%H:%M")
            datetime.strptime(end_time, "%H:%M")

            return start_time, end_time
        except ValueError:
            print("Invalid input. Please enter valid military time (HH:MM).")

#Iterating over each pdf file in the folder
def iterate_over_pdf(folder_name):
    pdf_pattern = os.path.join(folder_name, '*.pdf')
    pdf_files = glob.glob(pdf_pattern)

    for pdf_file in pdf_files:
        print(end = '\n')

        lower_text = extract_text(pdf_file).lower()

        print(find_first_course_code(pdf_file))
        course_instruction_mode = instruction_mode(lower_text)
        print(course_instruction_mode)

        # Lecture prompt
        if course_instruction_mode == 'in_person' or course_instruction_mode == 'online_synch':
            lecture_days = get_days('Enter lecture meeting day(s) (separated by spaces, ex: "sun tues thurs"): ')
            start_and_end_time("Enter lecture start time (HH:MM): ", "Enter lecture end time (HH:MM): ")


        print(lab_existence(lower_text))
        # Lab prompt if applicable
        if lab_existence(lower_text):
            lab_days = get_days('Enter lab meeting day(s) (separated by spaces, ex: "sun tues thurs"): ')
            start_and_end_time("Enter lab start time (HH:MM): ", "Enter lab end time (HH:MM): ")

        print(quiz_existence(lower_text))
        

        print(exam_existence(lower_text))
        




# Specify the folder name
folder_name = 'syllabus examples'
iterate_over_pdf(folder_name)





