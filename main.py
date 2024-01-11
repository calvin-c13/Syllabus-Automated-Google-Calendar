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

# Define {the scopes and credentials file
SCOPES =['https://www.googleapis.com/auth/calendar']
credentials_file = input('Enter the path to your credentials.json file: ') #User input to their credentials.json

def main():
    cred = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)
        return service

    except HttpError as error:
        print('An error has occurred: ', error)

service = main()


# Specify the folder name
folder_name = input('Enter the folder name containing your syllabuses: ')


allowed_input = ['E', 'C', 'M', 'P']
while True:
    time_zone_input = input("What is your school's time zone? (ex: EST, CST...): ").upper()
    time_zone_input = time_zone_input[0]
    if time_zone_input in allowed_input:
        # Map the time zone input to the corresponding time zone used for the calendar
        time_zone_mapping = {
            'E': 'America/New_York',
            'C': 'America/Chicago',
            'M': 'America/Denver',
            'P': 'America/Los_Angeles'
        }

        # Set the time_zone_used_for_calendar variable based on the mapping
        time_zone_used_for_calendar = time_zone_mapping.get(time_zone_input)
        break  
    else:
        print("Invalid time zone input. Please enter a valid time zone.")




date_of_last_class = input('Date of last day of classes (format: YYYY-MM-DD): ')
print('\n')

# Split the input string into year, month, and day
year, month, day = date_of_last_class.split('-')
year = int(year)
month = int(month)
day = int(day)

#Used for Google Calendar API function
recurrence_end_date = date_of_last_class.replace('-', '')



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
            return ','.join(day[0:2].upper() for day in input_days)
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
            print('Invalid input. Please enter valid military time (format - HH:MM).')




def number_of_quizzes():
    quantity_of_quizzes = int(input('Number of quizzes: '))
    list_of_quiz_dates = {}

    for quiz_number in range(1, quantity_of_quizzes + 1):
        quiz_date = input(f'Quiz {quiz_number} date (format: MM-DD): ')
        list_of_quiz_dates[f'Quiz {quiz_number}'] = quiz_date

    return list_of_quiz_dates




def number_of_exams():
    quantity_of_exams = int(input('Number of exams (including final exam): '))
    list_of_exam_dates = {}

    for exam_number in range(1, quantity_of_exams):
        exam_date = input(f'Midterm {exam_number} date (format: MM-DD): ')
        list_of_exam_dates[f'Midterm {exam_number}'] = exam_date
    
    # Initialize final_start_time and final_end_time
    final_start_time, final_end_time = None, None

    # If there is only one exam left, treat it as the final exam
    if quantity_of_exams > 0:
        final_exam_date = input('Final exam date (format: MM-DD): ')
        final_start_time, final_end_time = start_and_end_time('Final exam start time (format - HH:MM): ', 'Final exam end time (format - HH:MM): ')

    # Filter out 'final exam start time' and 'final exam end time'
    only_midterm_exam_dates = {key: value for key, value in list_of_exam_dates.items() if key not in ['Final exam start time', 'Final exam end time']}

    return only_midterm_exam_dates, final_exam_date, final_start_time, final_end_time








#Google Calendar Event Functions
def lecture_recurring_event(course_name, start_time, end_time, lecture_location, first_lecture, lecture_days, service):
    event = {
        'summary': f'{course_name} Lecture {start_time} - {end_time} {lecture_location}',
        'start': {
            'dateTime': f'{year}-{first_lecture}T{start_time}:00',
            'timeZone': time_zone_used_for_calendar, 
        },
        'end': {
            'dateTime': f'{year}-{first_lecture}T{end_time}:00',
            'timeZone': time_zone_used_for_calendar,
        },
        'recurrence': [f'RRULE:FREQ=WEEKLY;BYDAY={lecture_days};UNTIL={recurrence_end_date}'],
        'colorId': '5',
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': 60},  # Notification 1 hour before event
            ],
        },
    }

    # Insert the event into the calendar
    calendar_id = 'primary'  # Use 'primary' for the user's primary calendar
    event = service.events().insert(calendarId=calendar_id, body=event).execute()


def online_synch_lecture_recurring_event(course_name, start_time, end_time, first_lecture, lecture_days, service):
    event = {
        'summary': f'{course_name} Online Lecture {start_time} - {end_time}',
        'start': {
            'dateTime': f'{year}-{first_lecture}T{start_time}:00',
            'timeZone': time_zone_used_for_calendar, 
        },
        'end': {
            'dateTime': f'{year}-{first_lecture}T{end_time}:00',
            'timeZone': time_zone_used_for_calendar,
        },
        'recurrence': [f'RRULE:FREQ=WEEKLY;BYDAY={lecture_days};UNTIL={recurrence_end_date}'],
        'colorId': '5',
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': 60},  # Notification 1 hour before event
            ],
        },
    }

    # Insert the event into the calendar
    calendar_id = 'primary'  # Use 'primary' for the user's primary calendar
    event = service.events().insert(calendarId=calendar_id, body=event).execute()









def lab_recurring_event(course_name, start_time, end_time, lab_location, first_lab, lab_days, service):
    event = {
        'summary': f'{course_name} Lab {start_time} - {end_time} {lab_location}',
        'start': {
            'dateTime': f'{year}-{first_lab}T{start_time}:00',
            'timeZone': time_zone_used_for_calendar, 
        },
        'end': {
            'dateTime': f'{year}-{first_lab}T{end_time}:00',
            'timeZone': time_zone_used_for_calendar,
        },
        'recurrence': [f'RRULE:FREQ=WEEKLY;BYDAY={lab_days};UNTIL={recurrence_end_date}'],
        'colorId': '5',
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': 60},  # Notification 1 hour before event
            ],
        },
    }

    # Insert the event into the calendar
    calendar_id = 'primary'  # Use 'primary' for the user's primary calendar
    event = service.events().insert(calendarId=calendar_id, body=event).execute()




def quiz_calendar_event(course_name, quiz_number, lecture_start_time, lecture_end_time, lecture_location, quiz_date):
    event = {
        'summary': f'{course_name} {quiz_number} {lecture_location}',
        'start': {
            'dateTime': f'{year}-{quiz_date}T{lecture_start_time}:00',
            'timeZone': 'EST',
        },
        'end': {
            'dateTime': f'{year}-{quiz_date}T{lecture_end_time}:00',
            'timeZone': 'EST',
        },
        'colorId': '11',
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': 7 * 24 * 60},  # Notification 1 week before event
            ],
        },
    }

    # Insert the event into the calendar
    calendar_id = 'primary'  # Use 'primary' for the user's primary calendar
    event = service.events().insert(calendarId=calendar_id, body=event).execute()



def midterm_calendar_event(course_name, exam_number, lecture_start_time, lecture_end_time, lecture_location, exam_date):
    event = {
        'summary': f'{course_name} {exam_number} {lecture_start_time} - {lecture_end_time} {lecture_location}',
        'start': {
            'dateTime': f'{year}-{exam_date}T{lecture_start_time}:00',
            'timeZone': 'EST',
        },
        'end': {
            'dateTime': f'{year}-{exam_date}T{lecture_end_time}:00',
            'timeZone': 'EST',
        },
        'colorId': '11',
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': 14 * 24 * 60},  # Notification 2 week before event
            ],
        },
    }

    # Insert the event into the calendar
    calendar_id = 'primary'  # Use 'primary' for the user's primary calendar
    event = service.events().insert(calendarId=calendar_id, body=event).execute()


def final_exam_calendar_event(course_name, final_start_time, final_end_time, lecture_location, final_exam_date):
    event = {
        'summary': f'{course_name} Final Exam {final_start_time} - {final_end_time} {lecture_location}',
        'start': {
            'dateTime': f'{year}-{final_exam_date}T{final_start_time}:00',
            'timeZone': 'EST',
        },
        'end': {
            'dateTime': f'{year}-{final_exam_date}T{final_end_time}:00',
            'timeZone': 'EST',
        },
        'colorId': '11',
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': 14 * 24 * 60},  # Notification 2 week before event
            ],
        },
    }

    # Insert the event into the calendar
    calendar_id = 'primary'  # Use 'primary' for the user's primary calendar
    event = service.events().insert(calendarId=calendar_id, body=event).execute()




#Iterating over each pdf file in the folder
def iterate_over_pdf(folder_name, service):
    pdf_pattern = os.path.join(folder_name, '*.pdf')
    pdf_files = glob.glob(pdf_pattern)

    for pdf_file in pdf_files:

        lower_text = extract_text(pdf_file).lower()

        course_name = find_first_course_code(pdf_file)
        print('\n' + course_name)
        course_instruction_mode = instruction_mode(lower_text)

        # Lecture prompt
        if course_instruction_mode == 'in_person' or course_instruction_mode == 'online_synch':
            first_lecture = input('Date of first lecture (format: MM-DD): ')
            lecture_days = get_days('Lecture meeting day(s) (separated by spaces, ex: "sun tues thurs"): ')
            lecture_start_time, lecture_end_time = start_and_end_time('Lecture start time (format - HH:MM): ', 'Lecture end time (format - HH:MM): ')

        if course_instruction_mode == 'in_person':
            lecture_location = input('Lecture location: ')
            lecture_recurring_event(course_name, lecture_start_time, lecture_end_time, lecture_location, first_lecture, lecture_days, service)

        if course_instruction_mode == 'online_synch':
            online_synch_lecture_recurring_event(course_name, lecture_start_time, lecture_end_time, first_lecture, lecture_days, service)

        lab_existence(lower_text)
        # Lab prompts if applicable
        if lab_existence(lower_text):
            print('\n')
            first_lab = input('Date of first lab (format: MM-DD): ')
            lab_days = get_days('Lab meeting day(s) (separated by spaces, ex: "sun tues thurs"): ')
            lab_start_time, lab_end_time = start_and_end_time('Lab start time (format - HH:MM): ', 'Lab end time (format - HH:MM): ')
            lab_location = input('Lab location: ')
            lab_recurring_event(course_name, lab_start_time, lab_end_time, lab_location, first_lab, lab_days, service)





        quiz_existence(lower_text)
        #Quiz prompts if applicable
        if quiz_existence(lower_text):
            print('\n')
            quizzes = number_of_quizzes()
            for quiz_number, quiz_date in quizzes.items():
                    quiz_calendar_event(course_name, quiz_number, lecture_start_time, lecture_end_time, lecture_location, quiz_date)

        exam_existence(lower_text)
        #Exam prompts if applicable
        if exam_existence(lower_text):
            print('\n')
            # Call the function and unpack the returned values
            only_midterm_exam_dates, final_exam_date, final_start_time, final_end_time = number_of_exams()
            for exam_number, exam_date in only_midterm_exam_dates.items():
                midterm_calendar_event(course_name, exam_number, lecture_start_time, lecture_end_time, lecture_location, exam_date)
        final_exam_calendar_event(course_name, final_start_time, final_end_time, lecture_location, final_exam_date)
        
        print(end = '\n')



iterate_over_pdf(folder_name, service)

print('ALL DONE!')




