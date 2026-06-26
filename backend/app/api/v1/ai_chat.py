from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
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

# --- 🤖 EXPANDED SYSTEM PROMPT WITH RAG TOOL ---
AGENT_SYSTEM_PROMPT = """
You are the SmartHR Autonomous Agent Engine. You have access to the following tools:

1. name: "check_live_workforce_headcount"
   description: "Use this tool to find out the total number of employees currently hired in the organization."
   arguments: {}

2. name: "run_attrition_risk_inference"
   description: "Use this tool to compute turnover and retention risk probability metrics for an individual."
   arguments: {"years_at_company": float, "monthly_salary": float, "weekly_overtime": float, "satisfaction": float}

3. name: "search_company_policy_handbook"
   description: "Use this tool to search internal corporate rules, parental leaves, codes of conduct, or employee handbook policies."
   arguments: {"search_query": string}

If the user's query requires a tool, you MUST respond ONLY with a raw JSON object matching this structure:
{"tool_call": {"name": "TOOL_NAME", "arguments": { ... }}}

If no tool is required to fulfill the request, respond naturally in plain prose text. Do not invent arguments.
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
            try:
                tool_data = json.loads(agent_intent_raw)
                call_details = tool_data.get("tool_call", {})
                tool_name = call_details.get("name")
                args = call_details.get("arguments", {})
                
                tool_output = {}
                
                # --- TOOL ROUTING DIRECT PATHS ---
                if tool_name == "check_live_workforce_headcount":
                    tool_output = hr_agent_toolbox.check_live_workforce_headcount()
                    
                elif tool_name == "run_attrition_risk_inference":
                    tool_output = hr_agent_toolbox.run_attrition_risk_inference(
                        years_at_company=float(args.get("years_at_company", 0)),
                        monthly_salary=float(args.get("monthly_salary", 0)),
                        weekly_overtime=float(args.get("weekly_overtime", 0)),
                        satisfaction=float(args.get("satisfaction", 3))
                    )
                
                # 🌟 ADDED RAG TOOL EXECUTION ROUTE 
                elif tool_name == "search_company_policy_handbook":
                    tool_output = hr_agent_toolbox.search_company_policy_handbook(
                        search_query=str(args.get("search_query", ""))
                    )
                
                final_response = hr_ai_assistant.execute_hr_query(
                    f"The user asked: '{user_query}'. You ran the tool '{tool_name}' and got this raw data output back: {json.dumps(tool_output)}. Explain this data summary naturally to the user.",
                    context_data
                )
                
                return {
                    "reply": final_response,
                    "agent_telemetry": {
                        "tool_executed": tool_name,
                        "arguments_passed": args,
                        "raw_output": tool_output
                    }
                }
                
            except Exception as parse_err:
                logger.warning(f"⚠️ Agent output was not valid JSON, falling back to direct chat response: {str(parse_err)}")
        
        return {"reply": agent_intent_raw}
        
    except Exception as e:
        logger.error(f"❌ Agent execution framework exception: {str(e)}")
        raise HTTPException(status_code=500, detail="Agent loop processing fault encountered.")