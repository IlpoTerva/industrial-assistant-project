from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from api.schemas import ChatRequest
import json
import inspect
from starlette.concurrency import iterate_in_threadpool
from api.registry import _pick_agent, AGENTS
router = APIRouter()


def _as_async(gen):
    return gen if inspect.isasyncgen(gen) else iterate_in_threadpool(gen)

@router.post("/api/chat/stream")
def chat_stream(payload: ChatRequest):
    agent_name = _pick_agent(payload.mode, payload.message)
    agent = AGENTS[agent_name]

    async def events():
        try:
            async for event in _as_async(agent(message=payload.message, session_id=payload.session_id, choice_id=payload.choice_id)):
                yield json.dumps(event, ensure_ascii=False) + "\n"
        except Exception as exc:
            yield json.dumps({"type": "error", "message": str(exc)}) + "\n"

    return StreamingResponse(events(), media_type="application/x-ndjson")

 