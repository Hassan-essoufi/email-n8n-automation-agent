from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from open_agent.app.agent import run_agent
from open_agent.app.tools import fetch_and_parse_emails
from open_agent.app.memory import is_processed, mark_processed, get_history, cache
from google_integration.gcalendar import get_events
from datetime import datetime, timezone
import calendar as cal
import asyncio

app = FastAPI(title="Open Agent - Email Automation", version="1.0.0")

app.mount("/ui", StaticFiles(directory="frontend", html=True), name="frontend")

@app.get('/')
def check_health():
    return {"status": "OK"}

@app.get('/stats')
def get_stats():
    return {"total_processed": len(cache)}

@app.get('/history')
def get_email_history():
    return {"emails": get_history()}

@app.get('/events')
def get_calendar_events():
    now = datetime.now(timezone.utc)
    time_min = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
    last_day = cal.monthrange(now.year, now.month)[1]
    time_max = now.replace(day=last_day, hour=23, minute=59, second=59, microsecond=0).isoformat()
    events = get_events(time_min, time_max)
    simplified = [
        {
            "summary": e.get("summary", "No title"),
            "date": e["start"].get("dateTime", e["start"].get("date", ""))[:10],
            "description": e.get("description", "")
        }
        for e in events
    ]
    return {"events": simplified}

@app.get('/fetch')
async def fetch_emails(max_results: int = 10):
    
    emails = fetch_and_parse_emails(max_results=max_results)
    results = []
    for email in emails:
        if is_processed(email.email_id):
            continue
        response = await run_agent(email)
        detail = {"id": email.email_id, "subject": email.subject, "action": response.action, "status": response.status, "message": response.message}
        if response.status == "success":
            mark_processed(email.email_id, detail)
        results.append(detail)
        await asyncio.sleep(0)

    return {"processed": len([r for r in results if r["status"] == "success"]), "details": results}

