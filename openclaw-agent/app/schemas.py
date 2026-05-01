from pydantic import BaseModel
from typing import Literal, List, Dict


class EmailData(BaseModel):

    sender: str
    subject: str
    body: str

class AgentRequest(BaseModel):

    email: EmailData

class AgentResponse(BaseModel):

    action: str 
    status: Literal['success', 'error']
    message: str

class SheetRow(BaseModel):
    
    spreadsheet_id: str
    cell_range: str
    values: List[list]

class CalendarEvent(BaseModel):

    summary: str
    description: str
    start_time: Dict[str, str]
    end_time: Dict[str, str]