from fastapi import FastAPI
from open_agent.app.agent import run_agent
from open_agent.app.tools import fetch_and_parse_emails
from open_agent.app.memory import is_processed, mark_processed

app = FastAPI(title="Open Agent - Email Automation", version="1.0.0", )

@app.get('/')
def check_health():
    return {"status": "OK"}

@app.get('/fetch')
async def fetch_emails(max_results: int = 10):
    
    emails = fetch_and_parse_emails(max_results=max_results)
    results = []
    for email in emails:
        if is_processed(email.email_id):
            continue
        response = await run_agent(email)
        if response.status == "success":
            mark_processed(email.email_id)
        results.append({"id": email.email_id,
                        "subject": email.subject,
                        "action": response.action, 
                        "status": response.status, 
                        "message": response.message})

    return {"processed": len([r for r in results if r["status"] == "success"]), "details": results}

