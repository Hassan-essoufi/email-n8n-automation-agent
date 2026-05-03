from fastapi import FastAPI
from openclaw_agent.app.agent import run_agent
from openclaw_agent.app.tools import fetch_and_parse_emails
from openclaw_agent.app.memory import is_processed, mark_processed

app = FastAPI(title="Openclaw-n8n-email-automation", version="1.0.0", )

@app.get('/')
def check_health():
    return {"status": "OK"}

@app.get('/fetch')
async def fetch_emails(max_results: int = 10):
    
    emails = fetch_and_parse_emails(max_results=max_results)
    count = 0
    for email in emails:
        if is_processed(email.email_id) == True:
            continue

        else:
            await run_agent(email)
            mark_processed(email.email_id)
            count += 1
    
    return {"processed": count}

