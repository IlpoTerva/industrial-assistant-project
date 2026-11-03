from __future__ import annotations
import json
from typing import Annotated, Any,  TypedDict

from langchain_core.messages import (AIMessage, 
                                     AnyMessage, 
                                     HumanMessage, 
                                     SystemMessage, 
                                     ToolMessage)
from langgraph.types import Command
from typing import Any

from mes_agent.chat_lang import SYSTEM_PROMPT, _build_graph
from mes_agent.tools import load_tools
from api.schemas import ChatResponse

GRAPH = None

def _build_message(message: str, history: list[dict[str, Any]]) -> list[AnyMessage]:
    messages: list[AnyMessage] = [SystemMessage(content=SYSTEM_PROMPT)]
    for item in (history or [])[-6:]:
        role = item.get("role")
        content = item.get("content")
        if not isinstance(content, str):
            continue
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
        elif role == "system":
            messages.append(SystemMessage(content=content))
    messages.append(HumanMessage(content=message))
    return messages

def _initial_state(message: str, history: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "messages": _build_message(message, history),
        "tool_calls_log": [],
        "steps": 0,
        "answer": "",
        "user_message":message,
    }


def _answer_response(state: dict) -> ChatResponse:
    return ChatResponse(
        blocks=[{"type": "text", "text": state["answer"]}],#TODO add sources.
    )

async def init():
    global GRAPH
    GRAPH = _build_graph(await load_tools())

async def stream_chat_response(message: str, session_id: str, choice_id: str | None = None):
    cfg = {"configurable": {"thread_id": session_id}}
    graph_input = _initial_state(message=message, history=[])

    async for chunk in GRAPH.astream(graph_input, cfg, stream_mode="custom"):
        if "stage" in chunk:
            yield {"type": "stage", **chunk}

    snap = await GRAPH.aget_state(cfg)
    #NOTE fix this, no need for interrupts in the agent loop
    resp = _answer_response(snap.values)

    yield {"type": "result", "data": resp.model_dump()}
