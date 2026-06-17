from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from app.services.ai_assistant import hr_ai_assistant
from app.app import RoleChecker

router = APIRouter()
allow_user_session = RoleChecker(["Admin", "HR", "Employee"])

class ChatInquiryPayload(BaseModel):
    message: str
    employee_id_context: Optional[int] = None

@router.post("/chat")
def dispatch_copilot_chat(payload: ChatInquiryPayload, current_user = Depends(allow_user_session)):
    context_data = {"id": payload.employee_id_context} if payload.employee_id_context else None
    response_string = hr_ai_assistant.execute_hr_query(payload.message, context_data)
    return {"reply": response_string}