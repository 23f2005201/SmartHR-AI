# app/api/v1/websocket_chat.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
import json
import httpx
import os
import re
from app.core.redis_config import get_cached_string, set_cached_string

router = APIRouter()
OLLAMA_URL = os.getenv("OLLAMA_HOST_URL", "http://smarthr-ollama-container:11434/api/generate")

# 🛑 PROMPT INJECTION GUARD: Flag common malicious system override patterns
PROMPT_INJECTION_DENYLIST = re.compile(
    r"(ignore\s+previous\s+instruction|system\s+override|you\s+are\s+now\s+an\s+admin|act\s+as\s+root)", 
    re.IGNORECASE
)

MAX_MESSAGE_LENGTH = 4000  # Prevent memory exhaustion DoS patterns

@router.websocket("/ws/copilot")
async def websocket_copilot_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            raw_data = await websocket.receive_text()
            payload = json.loads(raw_data)
            user_message = str(payload.get("message", "")).strip()
            
            # 🛡️ SAFETY CHECK: Size Constraint Guard
            if len(user_message) > MAX_MESSAGE_LENGTH:
                await websocket.send_json({"event": "error", "details": "Payload size limit exceeded."})
                continue
                
            # 🛡️ SAFETY CHECK: Prompt Injection Neutralizer
            if PROMPT_INJECTION_DENYLIST.search(user_message):
                await websocket.send_json({
                    "event": "token", 
                    "text": "[Security Alert: Malicious interaction pattern detected. Execution terminated.]"
                })
                await websocket.send_json({"event": "execution_complete"})
                continue

            system_prompt = get_cached_string("agent_system_prompt")
            if not system_prompt:
                system_prompt = "You are an autonomous HR Copilot engine running via local streaming."
                set_cached_string("agent_system_prompt", system_prompt, expire_seconds=3600)

            ollama_payload = {
                "model": "llama3.2:1b",
                "prompt": f"System: {system_prompt}\nUser: {user_message}",
                "stream": True
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                async with client.stream("POST", OLLAMA_URL, json=ollama_payload) as response:
                    if response.status_code != 200:
                        await websocket.send_json({"event": "error", "details": "Local LLM service unreachable."})
                        return
                    async for chunk in response.aiter_lines():
                        if chunk:
                            parsed_chunk = json.loads(chunk)
                            token = parsed_chunk.get("response", "")
                            
                            await websocket.send_json({"event": "token", "text": token})
                            if parsed_chunk.get("done", False):
                                break
                                
            await websocket.send_json({"event": "execution_complete"})

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({"event": "error", "details": "An internal system anomaly occurred."})
        except Exception:
            pass