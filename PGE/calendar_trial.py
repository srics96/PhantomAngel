import os
from datetime import timedelta
import datetime
import pytz

import httplib2
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

service_account_email = 'calendar@phantom-gab-engine.iam.gserviceaccount.com'

CLIENT_SECRET_FILE = 'calendar_service_account.json'

SCOPES = 'https://www.googleapis.com/auth/calendar'
scopes = [SCOPES]

def build_service():
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        filename=CLIENT_SECRET_FILE,
        scopes=SCOPES
    )

    http = credentials.authorize(httplib2.Http())

    service = build('calendar', 'v3', http=http)

    return service


def create_event():
    service = build_service()

    start_datetime = datetime.datetime.now(tz=pytz.utc)
    event = service.events().insert(calendarId='sricharanprograms@gmail.com', body={
        'summary': 'Foo',
        'description': 'Bar',
        'start': {'dateTime': start_datetime.isoformat()},
        'end': {'dateTime': (start_datetime + timedelta(minutes=15)).isoformat()},
    }).execute()

    print(event)

create_event()