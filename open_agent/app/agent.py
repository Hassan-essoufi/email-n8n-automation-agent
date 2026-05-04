import json
from groq import Groq
from open_agent.config import settings
from open_agent.app.schemas import EmailData, SheetRow, CalendarEvent, AgentResponse
from open_agent.app.tools import log_to_sheet, create_calendar_event
from open_agent.app.prompts import EMAIL_PROMPT, SYSTEM_PROMPT

client = Groq(api_key=settings.groq_api_key)

async def run_agent(email: EmailData):

    try:
        formatted_prompt = EMAIL_PROMPT.format(
            sender=email.sender,
            subject=email.subject,
            body=email.body[:3000]
        )

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": formatted_prompt}
            ]
        )
        text = response.choices[0].message.content.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        result = json.loads(text)
        action = result.get("action")

        if action == "log_to_sheets":
            sheet_row = SheetRow(
                spreadsheet_id=settings.spreadsheet_id,
                cell_range="Feuille 1!A:D",
                values=[[email.sender, email.subject, result.get("summary", "")]]
            )
            log_to_sheet(sheet_row=sheet_row)

        elif action == "create_event":
            event = CalendarEvent(
                summary=result.get("summary"),
                description=result.get("description"),
                start_time=result.get("start_time"),
                end_time=result.get("end_time")
            )
            create_calendar_event(event)

        return AgentResponse(action=action, status="success", message="Done")

    except Exception as e:
        return AgentResponse(action="error", status="error", message=str(e))
