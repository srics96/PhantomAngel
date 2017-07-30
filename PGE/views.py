from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from PGE.models import Employee, Link, Manager, Priority, Project, Role, Selection, Session, Task
from PGE.serializers import EmployeeSerializer, LinkSerializer, ProjectSerializer  

from datetime import datetime, timedelta


from dateutil import parser

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

import httplib2
import json
import pyrebase
import pytz
import os.path
import sys
import requests


try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai

CLIENT_ACCESS_TOKEN = '75d2f175cd05473fbddba4d6475a49d8'
SESSION_ID = 1001

service_account_email = 'calendar@phantom-gab-engine.iam.gserviceaccount.com'

CLIENT_SECRET_FILE = 'PGE/calendar_service_account.json'

SCOPES = 'https://www.googleapis.com/auth/calendar'
scopes = [SCOPES]
tz = pytz.timezone('Asia/Calcutta')


config = {
  "apiKey": "AIzaSyB4555K4PmN7z5oMFIIfu08HSV_NRReSZQ",
  "authDomain": "phantom-gab-engine.firebaseapp.com",
  "databaseURL": "https://phantom-gab-engine.firebaseio.com",
  "storageBucket": "phantom-gab-engine.appspot.com",
  "serviceAccount": "PGE/phantom-gab-engine-firebase-adminsdk-o9tcv-6faea27d58.json"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
firebase_user = auth.sign_in_with_email_and_password("sriablaze@gmail.com", "1234sri#")
db = firebase.database()

# Utility method to delete unicodes

TASK_ADDITION_KEY_PROJECT_NAME = "project_name"
TASK_ADDITION_KEY_TASKS = "tasks"
TASK_ADDITION_MANAGER_EMAIL = "manager_email"
TASK_ENTITY_NAME = "Task"
TASK_ENTITY_ADDITION_URL = "https://api.api.ai/v1/entities/{0}/entries?v=20150910".format(TASK_ENTITY_NAME)
MESSAGE_SUBMISSION_URL = "https://api.api.ai/v1/query?v=20150910"
SUCCESS_STATUS_CODE = 200
MESSAGE_REQUEST_KEY = "message"
ACTION_INCOMPLETE = "actionIncomplete"
RESULT_KEY = "result"
DATE_DEADLINE_KEY = "date_deadline"
DURATION_DEADLINE_KEY = "duration_deadline"
headers = {'Content-Type': 'application/json; charset=utf-8', 'Authorization': 'Bearer b55df5347afe4002a39e94cd61c121c9'}
WORK_START_INTENT_NAME = "work_start"
SESSION_START_INTENT_NAME = "session_start"
SESSION_END_INTENT_NAME = "session_end"
BREAK_START_INTENT_NAME = "break_start"
BREAK_END_INTENT_NAME = "break_end"
TASK_KEY = "task"
MEETING_INTENT_NAME = "meet_schedular"
ASSIGNMENT_INTENT_NAME = "Assignment"
ASSIGNMENT_CONTINUATION_INTENT_NAME = "assignment_continuation"
LEAVE_ABSENCE_REQUEST_INTENT = "LeaveAbsenceRequest"


def log_user_in(work_type):
    print(work_type)



def build_service():
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        filename=CLIENT_SECRET_FILE,
        scopes=SCOPES
    )

    http = credentials.authorize(httplib2.Http())

    service = build('calendar', 'v3', http=http)

    return service


def create_event(deadline, summary, description):
    service = build_service()
    
    start_datetime = datetime.now(tz=tz)
    event = service.events().insert(calendarId='sricharanprograms@gmail.com', body={
        'summary': summary,
        'description': description,
        'start': {'dateTime': start_datetime.isoformat()},
        'end': {'dateTime': deadline.isoformat()},
    }).execute()

    print(event)



def byteify(input):
    if isinstance(input, dict):
        return {byteify(key): byteify(value)
                for key, value in input.items()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, bytes):
        return input.encode('utf-8')
    else:
        return input


def call_api(session_id, query):
    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)

    request = ai.text_request()

    request.session_id = session_id

    request.query = query

    response = request.getresponse()

    return response.read()


@csrf_exempt
def add_tasks(request):
    if request.method == 'POST':
        selection_dict = {}
        task_names = []
        recieved_json = json.loads(request.body)
        print(recieved_json)
        recieved_dict = byteify(recieved_json)
        channel_name = recieved_dict['channel_name']
        manager_email = recieved_json['manager_email']
        user = User.objects.get(email=manager_email)
        employee_obj = user.employee
        manager_obj, created = Manager.objects.get_or_create(employee_instance=employee_obj)
        print(created)
        print(Manager.objects.all())
        manager_obj.project_set.create(project_name=channel_name)
        print(manager_obj.project_set.all())
        project_obj = Project.objects.get(project_name=channel_name)
        print(recieved_dict)
        for task_obj in recieved_dict['tasks']:
            task_name = task_obj['task_name']
            task_names.append(task_name)
            project_obj.task_set.create(task_name=task_name)

        print(project_obj.task_set.all())
        for role_emp_object in recieved_dict["employees"]:
            role_name = role_emp_object['role_name']
            employee_email = role_emp_object['employee']['email']
            print(employee_email)
            role_obj = Role.objects.get(role_name=role_name)
            user = User.objects.get(email=employee_email)
            employee_obj = user.employee
            project_obj.employees.add(employee_obj)
            selection_obj, created = project_obj.selections.get_or_create(role=role_obj)
            selection_obj.employees.add(employee_obj)
            selection_dict[role_name] = selection_obj
        print(selection_obj.employees.count())
        print(selection_dict)
        for role, selection_obj in selection_dict.items():
            project_obj.selections.add(selection_obj)
        entity_entries = [] 
        entity_name = TASK_ENTITY_NAME
        request_list = []
        for task_name in task_names:
            request_dict = {"value" : task_name, "synonyms" : [task_name]}
            request_list.append(request_dict)

        print(request_list)       
        request_list = json.dumps(request_list)
        entity_request = requests.post(TASK_ENTITY_ADDITION_URL, data=request_list, headers=headers)
        print(entity_request.json())
        if entity_request.status_code == SUCCESS_STATUS_CODE:
            print("Entity added successfully")
            
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=403)
        

def _close_session(user):
    session = Session.objects.get(end_date_time=None, user=user)
    session.end_date_time = datetime.now()
    session.save()
    return session

def _days_hours_minutes(td):
    return td.days, td.seconds//3600, (td.seconds//60)%60


def _format_end_session_response(days, hours, minutes, task_name):
    response = "You've worked on {0} for {1} minutes".format(task_name, minutes)
    response = {
        "speech_response" : response
    }
    return response

def send_response(results_dict):
    print("Im at the send reponse")
    fulfillment = results_dict['fulfillment']   
    speech_response = fulfillment['speech']
    response = {
        "speech_response" : speech_response
    }
    return response


def create_session(request, user, task, if_end_break=False):
    user_last_session = Session.objects.filter(user=user).last()
    if user_last_session is not None:
        if user_last_session.end_date_time is None:
            print("I shouldnt be here at all")
            user_last_session.end_date_time = datetime.now(tz=tz)
            logout(request)
    
    session = Session(user=user, task=task)
    session.save()
    session_id = session.id
    if if_end_break is False:
        print("Im here during start session")
        login(request, user)
    return session_id


def end_session(request, user):
    session = _close_session(user)
    cumulative_start_session_id = request.session['session_id']
    all_sessions = Session.objects.filter(id__gte=cumulative_start_session_id)
    session_timedelta = timedelta(0, 0, 0)
    for session in all_sessions:
        session_timedelta = session_timedelta + (session.end_date_time - session.start_date_time)

    days, hours, minutes = _days_hours_minutes(session_timedelta)
    task_name = request.session['task_name']
    response = _format_end_session_response(days, hours, minutes, task_name)
    logout(request)
    return response


def start_break(request, user, return_time):
    session = _close_session(user)
    task_name = session.task.task_name
    request.session['task_name'] = task_name


def end_break(request, user, channel_name):
    task_name = request.session['task_name']
    task = Task.objects.get(task_name=task_name, project__project_name=channel_name)
    session_id = create_session(request, user, task, if_end_break=True)


def create_meeting_event(meet_time, summary, description, attendees=None):
    service = build_service()
    end_time = meet_time + timedelta(hours=1)
    event = service.events().insert(calendarId='sricharanprograms@gmail.com', body={
        'summary': summary,
        'description': description,
        'start': {'dateTime': meet_time.isoformat()},
        'end': {'dateTime': end_time.isoformat()},
        'attendees': attendees
    }).execute()

    print(event)


def schedule_meeting(meet_time, meet_venue, attendees_email_list, organizer_email):
    attendees = []
    meet_time = parser.parse(meet_time)
    meet_time = meet_time - timedelta(hours=5, minutes=30)
    meet_time = meet_time.astimezone(tz)
    print("The meet time is {0}".format(meet_time))
    for attendee_email in attendees_email_list:
        each_mail_dict  = {'email' : attendee_email}
    attendees.append(each_mail_dict)
    username = User.objects.get(email=organizer_email).username
    summary = "Meeting organized by {0}".format(username)
    description = "Weekly meetup"
    create_meeting_event(meet_time, summary, description, attendees)


def create_attendence_tracker():
    managers = Manager.objects.all()
    for manager in managers:
        manager_email = manager.employee_instance.user.email
        at_stripped_email = manager_email.replace("@", "")
        dot_stripped_email = at_stripped_email.replace(".", "")
        input_dict = {"name" : "Phantom Attendence Tracker"}
        unique_key = "PAT{0}".format(dot_stripped_email) 
        db.child("master").child("channels").child(unique_key).set(input_dict, firebase_user['idToken'])
        channel_dict = {"channel_id" : unique_key}
        db.child("master").child(dot_stripped_email).child("associated_rooms").push(channel_dict, firebase_user['idToken'])
        

def leave_request(request, start_date, end_date, manager_email, user):
    at_stripped_email = manager_email.replace("@", "")
    dot_stripped_email = at_stripped_email.replace(".", "")
    unique_key = "PAT{0}".format(dot_stripped_email)
    username = user.username
    days, minutes, hours = _days_hours_minutes(end_date - start_date)
    message_text = "Hey, {0} has requested leave of absence for {1} days from {2} to {3}".format(username, days + 1, str(start_date), str(end_date))
    message_dict = {"senderId" : "phantom", "senderName" : "phantom", "text": message_text}
    channel_dict = db.child("master").child("channels").child(unique_key).child("messages").push(message_dict, firebase_user['idToken'])
    

@csrf_exempt
def handle_message(request):
    if request.method == 'GET':
        return HttpResponse("Reached server")
    if request.method == 'POST':
        print(Task.objects.all())
        recieved_json = json.loads(request.body)
        input_dict = byteify(recieved_json)
        message = input_dict[MESSAGE_REQUEST_KEY]
        channel_name = input_dict['channel_name']
        user_email = input_dict.get('email', None)
        message = message.lstrip()
        message = message[8:]
        message = message.replace("@", "")
        print(message)
        headers['Authorization'] = 'Bearer {0}'.format(CLIENT_ACCESS_TOKEN)
        request_dict = {"query" : [message], "sessionId" : SESSION_ID, "lang" : "en" } 
        request_dict = json.dumps(request_dict)
        response = requests.post(MESSAGE_SUBMISSION_URL, data=request_dict, headers=headers)
        response_dict = byteify(response.json())
        results_dict = response_dict[RESULT_KEY]
        print(results_dict)
        intent_name = results_dict['metadata']['intentName']
        result_parameters = results_dict["parameters"]
        action_incomplete = results_dict[ACTION_INCOMPLETE]
        user = User.objects.get(email=user_email)
        if intent_name == WORK_START_INTENT_NAME:
            method_call = eval(results_dict['action'])
            work_type = result_parameters['work_types']
            method_call(work_type)
            response = send_response(results_dict)
            
        elif intent_name == SESSION_START_INTENT_NAME:
            if action_incomplete is False:
                task_name = result_parameters[TASK_KEY]
                task = Task.objects.get(project__project_name=channel_name, task_name=task_name)
                session_id = create_session(request, user, task)
                request.session['session_id'] = session_id

        elif intent_name == BREAK_START_INTENT_NAME:
            method_call = eval(results_dict['action'])
            return_time = result_parameters['return_time']
            method_call(request, user, return_time)

        elif intent_name == BREAK_END_INTENT_NAME:
            method_call = eval(results_dict['action'])(request, user, channel_name)

        elif intent_name == SESSION_END_INTENT_NAME:
            response = eval(results_dict['action'])(request, user)
            return HttpResponse(json.dumps(response), content_type="application/json")

        elif intent_name == LEAVE_ABSENCE_REQUEST_INTENT:
            start_date = result_parameters['start_date']
            if start_date:
                start_date = parser.parse(start_date)
            else:
                start_date = datetime.now(tz=tz).date()
            absence_end_dict = result_parameters['end_of_leave']
            end_duration_dict = absence_end_dict.get("end_duration", None)
            if end_duration_dict is not None:
                magnitude = int(end_duration_dict["amount"])
                end_date = start_date + timedelta(days=magnitude - 1)
            else:
                end_date = parser.parse(absence_end_dict["end_date"])

            employee = user.employee
            project_obj = Project.objects.get(project_name=channel_name)
            manager = project_obj.manager
            manager_name = manager.employee_instance.user.username
            manager_email = manager.employee_instance.user.email 
            days, hours, minutes = _days_hours_minutes(end_date - start_date)
            leave_request(request, start_date.date(), end_date.date(), manager_email, user)
            response = "Your leave request for {0} days from {1} to {2} has been forwarded to your manager {3}".format(days + 1, str(start_date.date()), str(end_date.date()), manager_name)
            response = {
                "speech_response" : response
            }

            return HttpResponse(json.dumps(response), content_type="application/json")

                


        elif intent_name == MEETING_INTENT_NAME:
            if action_incomplete is False:
                attendees_email_list = []
                meet_time = result_parameters['date-time']
                meet_venue = result_parameters['meet-locations']
                meet_entities = result_parameters['meetEntity']
                all_roles = Role.objects.all()
                role_names = []
                for role in all_roles:
                    role_names.append(role.role_name)
                project_obj = Project.objects.get(project_name=channel_name)
                for meet_entity in meet_entities:
                    # Belongs to a role group
                    if meet_entity in role_names:
                        selection_obj = project_obj.selections.get(role__role_name=meet_entity)
                        employees = selection_obj.employees.all()
                        for employee in employees:
                            email = employee.user.email
                            attendees_email_list.append(email)
                    # An individual meet entity
                    else:
                        email = Employee.objects.get(user__username=meet_entity).user.email
                        attendees_email_list.append(email)
                print(attendees_email_list)
                eval(results_dict['action'])(meet_time, meet_venue, attendees_email_list, user_email)

        elif intent_name == ASSIGNMENT_INTENT_NAME or intent_name == ASSIGNMENT_CONTINUATION_INTENT_NAME:
            if action_incomplete is False:
                employees = result_parameters["employee"]
                print(employees)
                task_name = result_parameters["task"]
                print(task_name)
                task_obj = Task.objects.get(task_name=task_name, project__project_name=channel_name)
                project_obj = Project.objects.get(project_name=channel_name)
                for employee_name in employees:
                    if project_obj.selections.filter(employees__user__username=employee_name).exists():
                        employee_obj = Employee.objects.get(user__username=employee_name)
                        task_obj.employees.add(employee_obj)
                    else:
                        response = "The employee {0} is not a valid candidate for task assignment".format(employee_name)
                        response = {
                            "speech_response": response
                        }
                        return HttpResponse(json.dumps(response), content_type="application/json")
                
                deadline_dict = result_parameters.get("deadline", None)
                if deadline_dict is not None:
                    date_duration = deadline_dict.get(DATE_DEADLINE_KEY, None)
                    duration_deadline = deadline_dict.get(DURATION_DEADLINE_KEY, None)
                    if duration_deadline is not None:
                        amount = duration_deadline["amount"]
                        unit = duration_deadline["unit"]
                        if unit == "day":
                            deadline = datetime.now(tz=tz).date() + timedelta(days=int(amount))
                    else:
                        deadline = parser.parse(date_duration)
                else:
                    deadline = task_obj.deadline
                
                summary = task_name
                description = "Task Deadline set by channel - {0}".format(channel_name)
                default_time = datetime.now(tz=tz).time()
                datetime_obj = datetime.combine(deadline, default_time)
                datetime_obj = tz.localize(datetime_obj)
                create_event(datetime_obj, summary, description)
                task_obj.deadline = deadline
                task_obj.save()
            else:
                pass
        
        response = send_response(results_dict)
        return HttpResponse(json.dumps(response), content_type="application/json")
        

@csrf_exempt
def get_employees(request, role='WFD'):
    if request.method == 'GET':
        print(role)
        queryset = Employee.objects.filter(priority__role__role_name=role).order_by('priority__magnitude', 'user__username')
        employee_serializer = EmployeeSerializer(queryset, many=True)
        print(employee_serializer.data)
        return JsonResponse(employee_serializer.data, status=201, safe=False)


@csrf_exempt
def get_project_employees(request, channel_name):
    if request.method == 'GET':
        list_of_employees_serialized = []
        project_obj = Project.objects.get(project_name=channel_name)
        selections = project_obj.selections.all()
        for selection in selections:
            queryset = selection.employees.all()
            employee_serializer = EmployeeSerializer(queryset, many=True)
            list_of_employees_serialized.append(employee_serializer.data)
        return JsonResponse(list_of_employees_serialized, status=201, safe=False)

@csrf_exempt
def get_channels(request, email):
    if request.method == 'GET':
        print("Im at the getChannels API")
        employee = Employee.objects.get(user__email=email)
        projects = employee.project_set.all()
        project_serializer = ProjectSerializer(projects, many=True)
        return JsonResponse(project_serializer.data, status=200, safe=False)


@csrf_exempt
def list_links(request, channel_name):
    if request.method == 'GET':
        project = Project.objects.get(project_name=channel_name)
        queryset = project.link_set.all()
        link_serializer = LinkSerializer(queryset, many=True)
        return JsonResponse(link_serializer.data, status=200, safe=False)


@csrf_exempt
def add_employee(request):
    if request.method == 'POST':
        roles = []
        role_keys = ["1", "2", "3"]
        recieved_json = json.loads(request.body)
        recieved_dict = byteify(recieved_json)
        name = recieved_dict["name"]
        email = recieved_dict["email"]
        at_stripped_email = email.replace("@", "")
        dot_stripped_email = at_stripped_email.replace(".", "")
        input_dict = {"name": name}
        db.child("master").child(dot_stripped_email).set(input_dict, firebase_user['idToken'])
        for priorities in role_keys:
            roles.append(recieved_dict.get(priorities, None))
        print(roles)
        for (index, role) in enumerate(roles):
            if role is not None:
                role_obj = Role.objects.get(role_name=role)
                priority_obj = Priority.objects.get(role=role_obj, magnitude=index + 1)
                user = User.objects.create(username=name, email=email)
                employee_obj = Employee(user=user)
                employee_obj.save()
                employee_obj.priority.add(priority_obj)
        return HttpResponse(status=200)

@csrf_exempt
def submit_link_data(request):
    if request.method == 'POST':
        link_name = request.POST['linkName']
        selected_project = request.POST['projectList']
        url = request.POST['url']
        project = Project.objects.get(project_name=selected_project)
        link = Link(project=project, link_name=link_name, url=url)
        link.save()
        print(link)
        return HttpResponse(status=200)








                



    

    
        



        



