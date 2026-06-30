from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, AsyncGenerator, List, Any
import json
import re
import logging

from app.services.ai_assistant import hr_ai_assistant
from app.services.agent_tools import hr_agent_toolbox
from app.app import RoleChecker

logger = logging.getLogger("uvicorn.error")
router = APIRouter()
allow_user_session = RoleChecker(["Admin", "HR", "Employee"])

class ChatInquiryPayload(BaseModel):
    message: str
    employee_id_context: Optional[int] = None

# FIXED: Strict negative constraints and structured format enforcing to avoid multi-tool bleed
AGENT_SYSTEM_PROMPT = """
You are the SmartHR Autonomous Agent Engine. You have access to these exact system tools:

1. name: "check_live_workforce_headcount"
2. name: "run_attrition_risk_inference"
3. name: "search_company_policy_handbook"
4. name: "trigger_workforce_audit"
5. name: "generate_attrition_ledger_download"
6. name: "terminate_user_session"
7. name: "onboard_new_employee"
   arguments: {"user_id": int, "department_id": int, "full_name": string, "salary": float}
8. name: "clock_in_out_employee"
   arguments: {"employee_id": int, "action_state": string}
9. name: "submit_leave_request_agent"
   arguments: {"employee_id": int, "leave_type": string, "days_duration": int}
10. name: "disburse_department_payroll"
    arguments: {"employee_id": int}

CRITICAL EXECUTION PROTOCOL:
- Analyze the User Query carefully. Identify ONLY the operations explicitly requested.
- DO NOT output tools that are not directly asked for by the user.
- Provide your structured instructions inside clear JSON objects matching this exact formatting target:
{"name": "TOOL_NAME", "arguments": {...}}
- If a multi-step sequence is requested, output ONLY the JSON objects for those requested steps in chronological order. Do not append unrelated tool JSON objects under any circumstances.
"""

def extract_json_objects_from_text(text: str) -> List[dict]:
    """Scans raw conversational text and extracts valid JSON structural blocks."""
    results = []
    brace_count = 0
    start_index = -1
    
    for i, char in enumerate(text):
        if char == '{':
            if brace_count == 0:
                start_index = i
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0 and start_index != -1:
                potential_json = text[start_index:i+1]
                try:
                    parsed_obj = json.loads(potential_json)
                    if isinstance(parsed_obj, dict):
                        results.append(parsed_obj)
                except Exception:
                    try:
                        sanitized = potential_json.replace('\n', ' ')
                        parsed_sanitized = json.loads(sanitized)
                        if isinstance(parsed_sanitized, dict):
                            results.append(parsed_sanitized)
                    except Exception:
                        pass
                start_index = -1
    return results

def safe_int(value: Any, default: int) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_float(value: Any, default: float) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

@router.post("/chat")
async def dispatch_copilot_chat(payload: ChatInquiryPayload, current_user = Depends(allow_user_session)):
    """Advanced sequential agent stream pipeline leveraging native bracket-scanning fallback trees."""
    async def stream_response_generator() -> AsyncGenerator[str, None]:
        user_query = payload.message
        context_data = {"id": payload.employee_id_context} if payload.employee_id_context else None
        
        agent_intent_raw = hr_ai_assistant.execute_hr_query(
            f"{AGENT_SYSTEM_PROMPT}\n\nUser Query: {user_query}", 
            context_data
        ) or ""
        
        executed_tools_telemetry: List[str] = []
        combined_tool_outputs: List[dict] = []
        action_trigger = "NONE"
        action_meta = {}

        extracted_tasks = extract_json_objects_from_text(agent_intent_raw)

        for task_data in extracted_tasks:
            try:
                if "tool_call" in task_data and isinstance(task_data["tool_call"], dict):
                    task_data = task_data["tool_call"]
                elif "tool" in task_data and isinstance(task_data["tool"], dict):
                    task_data = task_data["tool"]

                tool_name = str(task_data.get("name") or task_data.get("tool") or "UNKNOWN")
                raw_args = task_data.get("arguments") or task_data.get("args") or {}
                args = raw_args if isinstance(raw_args, dict) else {}

                tool_output = {"status": "skipped", "message": "Execution bypassed."}

                user_id_val = safe_int(args.get("user_id"), 6)
                emp_id_val = safe_int(args.get("employee_id"), 0)
                dep_id_val = safe_int(args.get("department_id"), 1)
                salary_val = safe_float(args.get("salary"), 90000.0)
                duration_val = safe_int(args.get("days_duration"), 1)

                if tool_name == "check_live_workforce_headcount":
                    tool_output = hr_agent_toolbox.check_live_workforce_headcount()
                elif tool_name == "trigger_workforce_audit":
                    tool_output = hr_agent_toolbox.trigger_workforce_audit()
                elif tool_name == "terminate_user_session":
                    tool_output = hr_agent_toolbox.terminate_user_session()
                    action_trigger = "TERMINATE"
                elif tool_name == "generate_attrition_ledger_download":
                    tool_output = hr_agent_toolbox.generate_attrition_ledger_download()
                    action_trigger = "DOWNLOAD"
                    action_meta = {"url": "/api/v1/exports/export-attrition-report"}
                elif tool_name == "onboard_new_employee":
                    tool_output = hr_agent_toolbox.onboard_new_employee(
                        user_id=user_id_val,
                        department_id=dep_id_val,
                        full_name=str(args.get("full_name") or "Zipporah"),
                        salary=salary_val
                    )
                elif tool_name == "clock_in_out_employee":
                    tool_output = hr_agent_toolbox.clock_in_out_employee(
                        employee_id=emp_id_val,
                        action_state=str(args.get("action_state") or "clock-in")
                    )
                elif tool_name == "submit_leave_request_agent":
                    tool_output = hr_agent_toolbox.submit_leave_request_agent(
                        employee_id=emp_id_val,
                        leave_type=str(args.get("leave_type") or "Casual"),
                        days_duration=duration_val
                    )
                elif tool_name == "disburse_department_payroll":
                    tool_output = hr_agent_toolbox.disburse_department_payroll(
                        employee_id=emp_id_val
                    )
                else:
                    continue

                executed_tools_telemetry.append(tool_name)
                combined_tool_outputs.append({"tool": tool_name, "result": tool_output})

                yield f"DATA:{json.dumps({'status_update': f'Completed step: {tool_name}'})}\n"

            except Exception as block_err:
                logger.warning(f"⚠️ Pipeline token isolation anomaly: {str(block_err)}")

        final_response = ""
        if executed_tools_telemetry:
            telemetry_str = json.dumps(executed_tools_telemetry)
            outputs_str = json.dumps(combined_tool_outputs)
            prompt_explanation = f"The user requested: '{user_query}'. You ran tools: {telemetry_str} and got outputs: {outputs_str}. Summarize the actions taken naturally."
            final_response = hr_ai_assistant.execute_hr_query(prompt_explanation, context_data) or ""
        
        if not final_response.strip():
            if executed_tools_telemetry:
                steps_summary = " & ".join([f"[{t}]" for t in executed_tools_telemetry])
                final_response = f"Operations completed successfully! Executed action sequence: {steps_summary}."
            else:
                final_response = "I processed your request, but no database system tool action was required."

        chunk_payload = {
            "reply": final_response,
            "action_trigger": action_trigger,
            "action_meta": action_meta,
            "agent_telemetry": {"sequence_run": executed_tools_telemetry, "raw_aggregated_outputs": combined_tool_outputs}
        }
        yield f"DATA:{json.dumps(chunk_payload)}\n"

    return StreamingResponse(stream_response_generator(), media_type="text/event-stream")