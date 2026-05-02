from googleapiclient.discovery import build
from google_integration.auth import get_credentials

def get_calendar_service():
    
    try:
        creds = get_credentials()
        service = build('calendar', version="v3", credentials=creds)

        return service
    
    except Exception as e:
        raise Exception(f'[ERROR]; Credentials are invalid,{e}') 
    

def create_event(summary, start, end, description):

    try:
        service = get_calendar_service()
        g_calendar = service.events()

        event = {
            "summary" : summary,
            "description": description,
            "start": start,
            "end": end
        }
        result = g_calendar.insert(
            calendarId='primary',
            body=event
        ).execute()

        return result
    except Exception as e:
        raise Exception(f'[ERROR]:{e}')

