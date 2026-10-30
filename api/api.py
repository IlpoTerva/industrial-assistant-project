from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.schemas import ChatRequest
import json
from app.registry import _pick_agent, AGENTS
router = APIRouter()



@router.post("/api/chat/stream")
def chat_stream(payload: ChatRequest):
    agent_name = _pick_agent(payload.mode, payload.message)
    agent = AGENTS[agent_name]

    def events():
        try:
            for event in agent(message=payload.message, session_id=payload.session_id, choide_id=payload.choice_id):
                yield json.dumps(event, ensure_ascii=False) + "\n"
        except Exception as exc:
            yield json.dumps({"type": "error", "message": str(exc)}) + "\n"

    return StreamingResponse(events(), media_type="application/x-ndjson")

