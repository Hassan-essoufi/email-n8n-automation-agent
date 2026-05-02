import httpx
from openclaw_agent.config import settings
from openclaw_agent.app.schemas import EmailData, SheetRow, CalendarEvent, AgentResponse
from openclaw_agent.app.tools import log_to_sheet, create_calendar_event
from openclaw_agent.app.prompts import EMAIL_PROMPT, SYSTEM_PROMPT

async def run_agent(email: EmailData):

    try:
        formatted_prompt = EMAIL_PROMPT.format(
                    sender=email.sender,
                    subject=email.subject,
                    body=email.body
                    )
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.openclaw_url,
                json={"system": SYSTEM_PROMPT,
                      "message": formatted_prompt},
                headers={"Authorization": f"Bearer {settings.openclaw_secret}"}
                )
            result = response.json()
            action = result.get("action")

            if action == "log_to_sheets":
                sheet_row = SheetRow(spreadsheet_id=settings.spreadsheet_id,
                                    cell_range="Sheet1!A:D",
                                    values=[[email.sender, email.subject, email.body]])
                
                log_to_sheet(sheet_row=sheet_row)

            elif action == "create_event":
                event = CalendarEvent(summary=result.get("summary"),
                                    description=result.get("description"),
                                    start_time=result.get("start_time"),
                                    end_time=result.get("end_time"),

                                    )

                create_calendar_event(event)

            
            return AgentResponse(action=action,
                                status="success",
                                message="Done")
        
    except Exception as e:
        return AgentResponse(action="error",
                            status="error",
                            message=str(e))