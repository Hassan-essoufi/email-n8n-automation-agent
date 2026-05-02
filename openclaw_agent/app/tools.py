from google_integration.gmail import  get_emails, parse_email
from google_integration.sheets import write_row
from google_integration.gcalendar import create_event
from openclaw_agent.app.schemas import EmailData, SheetRow, CalendarEvent

def fetch_and_parse_emails(max_results):

    messages = get_emails(max_results=max_results)
    emails = []
    for msg in messages:
        parsed = parse_email(msg)
        email_data = EmailData(**parsed)
        emails.append(email_data)
    return emails
    
    
def log_to_sheet(sheet_row: SheetRow):

    result = write_row(sheet_row.spreadsheet_id,
                        sheet_row.cell_range,
                        sheet_row.values)
    return result

def create_calendar_event(event: CalendarEvent):

    result = create_event(summary=event.summary,
                        start=event.start_time,
                        end=event.end_time,
                        description=event.description)
    return result
