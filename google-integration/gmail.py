from googleapiclient.discovery import build
from auth import get_credentials
import base64



def get_gmail_service():
     
    try:
        creds = get_credentials()
        service = build('gmail', version="v1", credentials=creds)
        return service
    
    except Exception as e:
        raise Exception(f'[ERROR]: Credentials are invalid{e}')
    

def get_emails(max_results):
    
    try:
        service = get_gmail_service()
        results = service.users().messages().list(
                userId="me",
                labelIds=["INBOX"],
                maxResults=max_results
                ).execute()
        messages = results.get("messages", [])
        
        emails = []

        for m in messages:
            msg = service.users().messages().get(
                userId="me",
                id=m["id"],
                format="full"
            ).execute()
            emails.append(msg)
        return emails
    
    except Exception as e:
        raise Exception(f'[ERROR]:{e}')
    

def parse_email(message):
    
    parsed_email = {}
    payload = message["payload"]
    headers = payload["headers"]
    
    for h in headers:
        if h["name"] == "From":
            parsed_email["sender"] = h["value"]
        if h["name"] == "Subject":
            parsed_email["subject"] = h["value"]

    body = ""

    if "data" in payload.get("body", {}):
        body = base64.urlsafe_b64decode(
            payload["body"]["data"]
        ).decode("utf-8", errors="ignore")
        parsed_email['body'] = body

    return parsed_email


