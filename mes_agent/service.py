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

from mes_agent.chat_lang import GRAPH, SYSTEM_PROMPT
from mes_agent.tools import tool_get_date
from api.schemas import ChatResponse

def _build_message(message: str, history: list[dict[str, Any]]) -> list[AnyMessage]:
    messages: list[AnyMessage] = [SystemMessage(content=SYSTEM_PROMPT + f"\n\nToday's date: {tool_get_date()}")]
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

def stream_chat_response(message: str, session_id: str, choide_id: str | None = None):
    cfg = {"configurable": {"thread_id": session_id}}
    graph_input = _initial_state(message=message)

    for chunk in GRAPH.stream(graph_input, cfg, stream_mode="custom"):
        if "stage" in chunk:
            yield {"type": "stage", **chunk}

    snap = GRAPH.get_state(cfg)
    resp = _answer_response(snap.values)

    yield {"type": "result", "data": resp.model_dump()}




def generate_chat_response(message: str, history: list[dict[str, Any]]) -> dict[str, Any]:
    final = GRAPH.invoke(_initial_state(message=message, history=history))
    return {
        "answer": final["answer"],
        "tool_calls": final["tool_calls_log"],
    }