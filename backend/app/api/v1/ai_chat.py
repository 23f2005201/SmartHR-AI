from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, AsyncGenerator, List, Any, Dict
import json
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.services.ai_assistant import hr_ai_assistant
from app.services.agent_tools import hr_agent_toolbox
from app.app import RoleChecker

logger = logging.getLogger("uvicorn.error")
router = APIRouter()
allow_user_session = RoleChecker(["Admin", "HR", "Employee"])

# Thread pool for running blocking LLM calls
_executor = ThreadPoolExecutor(max_workers=4)

class ChatInquiryPayload(BaseModel):
    message: str
    employee_id_context: Optional[int] = None

# ============================================================
# AGENT SYSTEM PROMPT
# ============================================================
AGENT_SYSTEM_PROMPT = """
You are the SmartHR Autonomous Agent Engine. You have access to these exact tools:

AVAILABLE TOOLS:
1. {"name": "check_live_workforce_headcount"}
2. {"name": "run_attrition_risk_inference", "arguments": {"years_at_company": float, "monthly_salary": float, "weekly_overtime": float, "satisfaction": float}}
3. {"name": "search_company_policy_handbook", "arguments": {"search_query": string}}
4. {"name": "trigger_workforce_audit"}
5. {"name": "generate_attrition_ledger_download"}
6. {"name": "terminate_user_session"}
7. {"name": "onboard_new_employee", "arguments": {"user_id": int, "department_id": int, "full_name": string, "salary": float}}
8. {"name": "clock_in_out_employee", "arguments": {"employee_id": int, "action_state": "clock-in" or "clock-out"}}
9. {"name": "submit_leave_request_agent", "arguments": {"employee_id": int, "leave_type": string, "days_duration": int}}
10. {"name": "disburse_department_payroll", "arguments": {"employee_id": int}}

STRICT EXECUTION RULES:
- Output ONLY valid JSON objects for tools that are EXPLICITLY requested
- Each tool call must be a separate JSON object: {"name": "TOOL_NAME", "arguments": {...}}
- For tools with no arguments, output: {"name": "TOOL_NAME"}
- Do NOT add commentary, explanation, or extra text
- Do NOT call tools that were not requested
- Output tool calls in the exact order they should execute

EXAMPLE:
User: "Check headcount and run workforce audit"
Output:
{"name": "check_live_workforce_headcount"}
{"name": "trigger_workforce_audit"}
"""

# ============================================================
# TOOL REGISTRY - Maps tool names to executor functions
# ============================================================
def build_tool_registry(args: dict, context: Optional[dict]) -> dict:
    """Build a clean tool registry with argument injection."""

    def safe_int(val: Any, default: int) -> int:
        try:
            return int(val)
        except (ValueError, TypeError):
            return default

    def safe_float(val: Any, default: float) -> float:
        try:
            return float(val)
        except (ValueError, TypeError):
            return default

    # Extract common args with smart fallbacks
    employee_id = safe_int(
        args.get("employee_id") or (context.get("id") if context else None), 0
    )
    user_id = safe_int(args.get("user_id"), 6)
    department_id = safe_int(args.get("department_id"), 1)
    salary = safe_float(args.get("salary"), 90000.0)
    days_duration = safe_int(args.get("days_duration"), 1)
    years_at_company = safe_float(args.get("years_at_company"), 2.0)
    monthly_salary = safe_float(args.get("monthly_salary"), salary / 12)
    weekly_overtime = safe_float(args.get("weekly_overtime"), 0.0)
    satisfaction = safe_float(args.get("satisfaction"), 0.7)
    search_query = str(args.get("search_query") or "company policy")
    full_name = str(args.get("full_name") or "New Employee")
    action_state = str(args.get("action_state") or "clock-in")
    leave_type = str(args.get("leave_type") or "Casual")

    return {
        "check_live_workforce_headcount": lambda: hr_agent_toolbox.check_live_workforce_headcount(),
        "run_attrition_risk_inference": lambda: hr_agent_toolbox.run_attrition_risk_inference(
            years_at_company=years_at_company,
            monthly_salary=monthly_salary,
            weekly_overtime=weekly_overtime,
            satisfaction=satisfaction
        ),
        "search_company_policy_handbook": lambda: hr_agent_toolbox.search_company_policy_handbook(
            search_query=search_query
        ),
        "trigger_workforce_audit": lambda: hr_agent_toolbox.trigger_workforce_audit(),
        "generate_attrition_ledger_download": lambda: hr_agent_toolbox.generate_attrition_ledger_download(),
        "terminate_user_session": lambda: hr_agent_toolbox.terminate_user_session(),
        "onboard_new_employee": lambda: hr_agent_toolbox.onboard_new_employee(
            user_id=user_id,
            department_id=department_id,
            full_name=full_name,
            salary=salary
        ),
        "clock_in_out_employee": lambda: hr_agent_toolbox.clock_in_out_employee(
            employee_id=employee_id,
            action_state=action_state
        ),
        "submit_leave_request_agent": lambda: hr_agent_toolbox.submit_leave_request_agent(
            employee_id=employee_id,
            leave_type=leave_type,
            days_duration=days_duration
        ),
        "disburse_department_payroll": lambda: hr_agent_toolbox.disburse_department_payroll(
            employee_id=employee_id
        ),
    }

# ============================================================
# ACTION TRIGGERS - Special post-tool UI signals
# ============================================================
ACTION_TRIGGER_MAP: Dict[str, Dict] = {
    "terminate_user_session": {
        "trigger": "TERMINATE",
        "meta": {}
    },
    "generate_attrition_ledger_download": {
        "trigger": "DOWNLOAD",
        "meta": {"url": "/api/v1/exports/export-attrition-report"}
    },
}

# ============================================================
# JSON EXTRACTION ENGINE
# ============================================================
def extract_json_objects_from_text(text: str) -> List[dict]:
    """
    Robust brace-balanced JSON scanner with multi-pass fallback.
    Handles nested objects, newlines, and partial corruptions.
    """
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
                candidate = text[start_index:i + 1]
                parsed = _try_parse_json(candidate)
                if parsed and isinstance(parsed, dict):
                    results.append(parsed)
                start_index = -1

    if not results:
        # Fallback: try line-by-line parsing
        for line in text.splitlines():
            line = line.strip()
            if line.startswith('{') and line.endswith('}'):
                parsed = _try_parse_json(line)
                if parsed and isinstance(parsed, dict):
                    results.append(parsed)

    logger.info(f"🔍 Extracted {len(results)} tool call(s) from agent response")
    return results


def _try_parse_json(raw: str) -> Optional[dict]:
    """Attempt JSON parsing with sanitization fallbacks."""
    for candidate in [raw, raw.replace('\n', ' '), raw.replace('\r', '')]:
        try:
            return json.loads(candidate)
        except Exception:
            continue
    return None


def normalize_task(task_data: dict) -> dict:
    """
    Normalize nested tool call formats into a flat structure.
    Handles: {name, arguments}, {tool_call: {name, arguments}}, etc.
    """
    # Unwrap nested formats
    for wrapper_key in ["tool_call", "tool", "function"]:
        if wrapper_key in task_data and isinstance(task_data[wrapper_key], dict):
            task_data = task_data[wrapper_key]
            break

    return task_data


def extract_tool_name(task_data: dict) -> str:
    """Extract tool name from various possible key names."""
    for key in ["name", "tool", "function", "tool_name"]:
        val = task_data.get(key)
        if val and isinstance(val, str):
            return val.strip()
    return "UNKNOWN"


def extract_tool_args(task_data: dict) -> dict:
    """Extract arguments from various possible key names."""
    for key in ["arguments", "args", "parameters", "params", "input"]:
        val = task_data.get(key)
        if val and isinstance(val, dict):
            return val
    return {}

# ============================================================
# MAIN CHAT ENDPOINT
# ============================================================
@router.post("/chat")
async def dispatch_copilot_chat(
    payload: ChatInquiryPayload,
    current_user=Depends(allow_user_session)
):
    """
    Advanced sequential agent stream pipeline.
    Phase 1: LLM plans tool calls
    Phase 2: Tools execute sequentially
    Phase 3: LLM summarizes results naturally
    """

    async def stream_response_generator() -> AsyncGenerator[str, None]:
        loop = asyncio.get_event_loop()
        user_query = payload.message
        context_data = {"id": payload.employee_id_context} if payload.employee_id_context else None

        # ── PHASE 1: Agent Planning ──────────────────────────────────────
        yield _sse("status", {"message": "🤖 Agent analyzing request..."})

        try:
            agent_intent_raw = await loop.run_in_executor(
                _executor,
                lambda: hr_ai_assistant.execute_agent_planning(
                    system_prompt=AGENT_SYSTEM_PROMPT,
                    user_query=user_query,
                    employee_context=context_data
                )
            )
        except Exception as e:
            logger.error(f"❌ Agent planning phase failed: {str(e)}")
            agent_intent_raw = ""

        logger.info(f"📋 Raw Agent Plan:\n{agent_intent_raw}")

        # ── PHASE 2: Tool Extraction & Execution ─────────────────────────
        executed_tools: List[str] = []
        tool_outputs: List[dict] = []
        action_trigger = "NONE"
        action_meta: dict = {}

        extracted_tasks = extract_json_objects_from_text(agent_intent_raw or "")

        if not extracted_tasks:
            logger.warning("⚠️ No tool calls extracted from agent response")
            yield _sse("status", {"message": "💬 Processing as conversational query..."})
        else:
            yield _sse("status", {"message": f"⚙️ Executing {len(extracted_tasks)} tool(s)..."})

        for task_raw in extracted_tasks:
            try:
                task = normalize_task(task_raw)
                tool_name = extract_tool_name(task)
                tool_args = extract_tool_args(task)

                if tool_name == "UNKNOWN":
                    logger.warning(f"⚠️ Skipping unresolvable task: {task_raw}")
                    continue

                yield _sse("status", {"message": f"🔧 Running: {tool_name}"})

                # Build fresh registry per tool (injects correct args)
                registry = build_tool_registry(tool_args, context_data)

                if tool_name not in registry:
                    logger.warning(f"⚠️ Unknown tool requested: {tool_name}")
                    yield _sse("status", {"message": f"⚠️ Unknown tool: {tool_name}"})
                    continue

                # Execute tool in thread pool (non-blocking)
                try:
                    tool_output = await loop.run_in_executor(
                        _executor,
                        registry[tool_name]
                    )
                except Exception as exec_err:
                    logger.error(f"❌ Tool {tool_name} execution error: {str(exec_err)}")
                    tool_output = {"status": "error", "message": str(exec_err)}

                # Check for action triggers
                if tool_name in ACTION_TRIGGER_MAP:
                    action_trigger = ACTION_TRIGGER_MAP[tool_name]["trigger"]
                    action_meta = ACTION_TRIGGER_MAP[tool_name]["meta"]

                executed_tools.append(tool_name)
                tool_outputs.append({"tool": tool_name, "result": tool_output})

                logger.info(f"✅ Tool {tool_name} completed: {str(tool_output)[:200]}")
                yield _sse("step_complete", {
                    "tool": tool_name,
                    "result": tool_output
                })

            except Exception as block_err:
                logger.warning(f"⚠️ Pipeline block error: {str(block_err)}")
                continue

        # ── PHASE 3: Natural Language Summary ───────────────────────────
        yield _sse("status", {"message": "📝 Generating summary..."})

        final_response = ""

        if executed_tools:
            try:
                summary_prompt = (
                    f"The user asked: '{user_query}'.\n"
                    f"You executed these tools: {json.dumps(executed_tools)}.\n"
                    f"Results: {json.dumps(tool_outputs)}.\n\n"
                    f"Write a clear, friendly, professional summary of what was accomplished. "
                    f"Include specific values from the results. Keep it concise."
                )
                final_response = await loop.run_in_executor(
                    _executor,
                    lambda: hr_ai_assistant.execute_hr_query(summary_prompt, context_data)
                ) or ""
            except Exception as summ_err:
                logger.error(f"❌ Summary generation failed: {str(summ_err)}")

        # Fallback summaries
        if not final_response.strip():
            if executed_tools:
                steps = " → ".join(f"[{t}]" for t in executed_tools)
                final_response = f"✅ Completed: {steps}"

                # Inject key result values into fallback
                for output in tool_outputs:
                    result = output.get("result", {})
                    if isinstance(result, dict):
                        for key, val in result.items():
                            if key not in ["status", "action"]:
                                final_response += f"\n• {key.replace('_', ' ').title()}: {val}"
            else:
                # Pure conversational fallback
                try:
                    final_response = await loop.run_in_executor(
                        _executor,
                        lambda: hr_ai_assistant.execute_hr_query(user_query, context_data)
                    ) or "I processed your request but no specific actions were required."
                except Exception:
                    final_response = "I processed your request but no specific actions were required."

        # ── FINAL PAYLOAD ────────────────────────────────────────────────
        yield _sse("complete", {
            "reply": final_response,
            "action_trigger": action_trigger,
            "action_meta": action_meta,
            "agent_telemetry": {
                "tools_executed": executed_tools,
                "tool_outputs": tool_outputs,
                "total_steps": len(executed_tools)
            }
        })

    return StreamingResponse(
        stream_response_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )


def _sse(event_type: str, data: dict) -> str:
    """Format a Server-Sent Event string."""
    return f"DATA:{json.dumps({'type': event_type, **data})}\n"