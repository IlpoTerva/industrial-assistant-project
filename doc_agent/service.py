
from langgraph.types import Command
from langchain.messages import HumanMessage
from typing import Any

from doc_agent.chat_lang import GRAPH 
from api.schemas import ChatResponse


def _initial_state(message: str) -> dict[str, Any]:
    return {
        "messages": [HumanMessage(content=message)],
        "steps": 0,
        "answer": "",
        "candidates": [],
        "route": "",
        "query": "",
        "context": [],
        "excluded": [],
        "resolved": False,
        "user_message":message,
    }

def _answer_response(state: dict) -> ChatResponse:
    return ChatResponse(
        route=state["route"],
        blocks=[{"type": "text", "text": state["answer"]}],#TODO add sources.
    )

def _choice_response(payload: dict, state: dict) -> ChatResponse:
    options = []
    for i, opt in enumerate(payload["options"], start=1):
        if isinstance(opt, str):
            opt = {"label": opt}
        options.append({"id": str(i), "label": opt["label"], "detail": opt.get("detail", "")})

    return ChatResponse(
        route=state["route"],
        blocks=[{"type":"choices", "prompt": payload["question"], "options": options}]
    )

def stream_chat_response(message: str, session_id: str, choice_id: str | None = None):
    cfg = {"configurable": {"thread_id": session_id}}
    if GRAPH.get_state(cfg).next:
        graph_input = Command(resume=choice_id or message)
    else:
        graph_input = _initial_state(message=message)

    for chunk in GRAPH.stream(graph_input, cfg, stream_mode="custom"):
        if "stage" in chunk:
            yield {"type": "stage", **chunk}

    snap = GRAPH.get_state(cfg)
    interrupts = [i for task in snap.tasks for i in task.interrupts]
    if interrupts:
        resp = _choice_response(payload=interrupts[0].value, state=snap.values)
    else:
        resp = _answer_response(snap.values)

    yield {"type": "result", "data": resp.model_dump()}