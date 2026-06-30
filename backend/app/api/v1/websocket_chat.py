# app/api/v1/websocket_chat.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import httpx
import os
from app.core.redis_config import get_cached_string, set_cached_string

router = APIRouter()
OLLAMA_URL = os.getenv("OLLAMA_HOST_URL", "http://smarthr-ollama-container:11434/api/generate")

@router.websocket("/ws/copilot")
async def websocket_copilot_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Receive query from web canvas front-end
            raw_data = await websocket.receive_text()
            payload = json.loads(raw_data)
            user_message = payload.get("message", "")
            
            # 1. Attempt Context Extraction from In-Memory Layer
            system_prompt = get_cached_string("agent_system_prompt")
            if not system_prompt:
                # Fallback template if missing from cache
                system_prompt = "You are an autonomous HR Copilot engine running via local streaming."
                set_cached_string("agent_system_prompt", system_prompt, expire_seconds=3600)

            # 2. Asynchronous Stream Pipeline direct to Ollama
            ollama_payload = {
                "model": "llama3.2:1b",
                "prompt": f"System: {system_prompt}\nUser: {user_message}",
                "stream": True
            }

            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream("POST", OLLAMA_URL, json=ollama_payload) as response:
                    async for chunk in response.aiter_lines():
                        if chunk:
                            parsed_chunk = json.loads(chunk)
                            token = parsed_chunk.get("response", "")
                            
                            # Real-time message frame dispatch
                            await websocket.send_json({
                                "event": "token",
                                "text": token
                            })
                            if parsed_chunk.get("done", False):
                                break
                                
            await websocket.send_json({"event": "execution_complete"})

    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({"event": "error", "details": str(e)})