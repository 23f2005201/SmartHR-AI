from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
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

AGENT_SYSTEM_PROMPT = """
You are the SmartHR Autonomous Agent Engine. You have access to these exact system tools:

1. name: "check_live_workforce_headcount"
   description: "Use this tool to find out the total number of employees currently hired."
   arguments: {}

2. name: "run_attrition_risk_inference"
   description: "Use this tool to compute turnover and retention risk probability metrics."
   arguments: {"years_at_company": float, "monthly_salary": float, "weekly_overtime": float, "satisfaction": float}

3. name: "search_company_policy_handbook"
   description: "Use this tool to search internal corporate rules, codes of conduct, or handbook policies."
   arguments: {"search_query": string}

4. name: "trigger_workforce_audit"
   description: "Use this tool when the user asks to 'audit', check metrics health, perform compliance reviews, or run structural HR routine checks."
   arguments: {}

5. name: "generate_attrition_ledger_download"
   description: "Use this tool explicitly when the user requests to download, export, generate, or fetch an 'Executive Attrition CSV audit' report or spreadsheet."
   arguments: {}

6. name: "terminate_user_session"
   description: "Use this tool explicitly when the user asks to log out, exit, sign out, terminate session, or clear their local session state."
   arguments: {}

CRITICAL RULES FOR APPLICATION COMPLIANCE:
- If the user query requires an action or tool, respond ONLY with a single JSON block matching the schema below.
- DO NOT wrap the JSON block in markdown backticks.
- DO NOT output introductory text, logging metadata, debug status or descriptive paragraphs.
- If no tool is required, answer in normal human text.

Exact JSON schema format to return:
{"tool_call": {"name": "TOOL_NAME", "arguments": { ... }}}
"""

@router.post("/chat")
async def dispatch_copilot_chat(payload: ChatInquiryPayload, current_user = Depends(allow_user_session)):
    try:
        user_query = payload.message
        logger.info(f"📨 Agent receiving incoming user interaction query: '{user_query}'")
        
        context_data = {"id": payload.employee_id_context} if payload.employee_id_context else None
        
        agent_intent_raw = hr_ai_assistant.execute_hr_query(
            f"{AGENT_SYSTEM_PROMPT}\n\nUser Query: {user_query}", 
            context_data
        )
        
        if agent_intent_raw and "tool_call" in agent_intent_raw:
            json_match = re.search(r"\{.*\}", agent_intent_raw, re.DOTALL)
            if json_match:
                try:
                    clean_json_str = json_match.group(0)
                    tool_data = json.loads(clean_json_str)
                    
                    if isinstance(tool_data, dict):
                        call_details = tool_data.get("tool_call", {})
                        
                        # 🛡️ FIX: Safely parse whether the model returned an object or a plain string name
                        if isinstance(call_details, dict):
                            tool_name = call_details.get("name")
                            args = call_details.get("arguments", {}) or {}
                        else:
                            tool_name = str(call_details)
                            args = {}
                        
                        tool_output = {}
                        action_trigger = "NONE"
                        action_meta = {}
                        
                        # --- DYNAMIC TOOL ROUTING MATRIX ---
                        if tool_name == "check_live_workforce_headcount":
                            tool_output = hr_agent_toolbox.check_live_workforce_headcount()
                            
                        elif tool_name == "run_attrition_risk_inference":
                            tool_output = hr_agent_toolbox.run_attrition_risk_inference(
                                years_at_company=float(args.get("years_at_company", 0)) if isinstance(args, dict) else 0.0,
                                monthly_salary=float(args.get("monthly_salary", 0)) if isinstance(args, dict) else 0.0,
                                weekly_overtime=float(args.get("weekly_overtime", 0)) if isinstance(args, dict) else 0.0,
                                satisfaction=float(args.get("satisfaction", 3)) if isinstance(args, dict) else 3.0
                            )
                        
                        elif tool_name == "search_company_policy_handbook":
                            search_val = args.get("search_query", user_query) if isinstance(args, dict) else user_query
                            tool_output = hr_agent_toolbox.search_company_policy_handbook(search_query=str(search_val))
                            
                        elif tool_name == "trigger_workforce_audit":
                            tool_output = hr_agent_toolbox.trigger_workforce_audit()
                                
                        elif tool_name == "terminate_user_session":
                            tool_output = hr_agent_toolbox.terminate_user_session()
                            action_trigger = "TERMINATE"
                        
                        
                        elif tool_name == "generate_attrition_ledger_download":
                            tool_output = hr_agent_toolbox.generate_attrition_ledger_download()
                            action_trigger = "DOWNLOAD"
                            action_meta = {"url": tool_output.get("download_url", "/api/v1/exports/export-attrition-report")}

                        # Generate the organic conversational response using tool outputs
                        final_response = hr_ai_assistant.execute_hr_query(
                            f"The user asked: '{user_query}'. You ran the tool '{tool_name}' and got this raw data output back: {json.dumps(tool_output)}. Explain this data summary naturally to the user.",
                            context_data
                        )
                        # Around line 124 of backend/app/api/v1/ai_chat.py
                        
                        return {
                            "reply": final_response,
                            "action_trigger": action_trigger,
                            "action_meta": action_meta,
                            "agent_telemetry": {
                                "tool_executed": tool_name,
                                "arguments_passed": args,
                                "raw_output": tool_output
                            }
                        }
                except Exception as parse_err:
                    logger.warning(f"⚠️ Agent parser internal error: {str(parse_err)}")
        
        return {"reply": agent_intent_raw, "action_trigger": "NONE", "action_meta": {}}
        
    except Exception as e:
        logger.error(f"❌ Agent execution framework exception: {str(e)}")
        raise HTTPException(status_code=500, detail="Agent loop processing fault encountered.")