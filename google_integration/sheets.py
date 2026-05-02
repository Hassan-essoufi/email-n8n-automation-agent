from googleapiclient.discovery import build
from google_integration.auth import get_credentials

def get_sheets_service():

    try:
        creds = get_credentials()
        service = build('sheets', version="v4", credentials=creds)
        return service
    
    except Exception as e:
        raise Exception(f'[ERROR]; Credentials are invalid,{e}')
    

def write_row(spreadsheet_id, cell_range, values):

    try:
        service = get_sheets_service()
        sheet = service.spreadsheets()
        sheet.values().append(
            spreadsheetId=spreadsheet_id,
            range=cell_range,
            valueInputOption="RAW",
            body={'values': values}
            ).execute()
    
    except Exception as e:
        raise Exception(f'[ERROR]:{e}')
    

def read_row(spreadsheet_id, cell_range):

    try:
        service = get_sheets_service()
        sheet = service.spreadsheets()
        
        data = sheet.values().get(
            spreadsheetId=spreadsheet_id,
            range=cell_range
            ).execute()
        
        return data.get('values', [])
    except Exception as e:
        raise Exception(f'[ERROR]:{e}')
    



    