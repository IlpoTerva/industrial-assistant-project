from __future__ import annotations
import json
from typing import Annotated, Any,  TypedDict

from langchain_core.messages import (AnyMessage, 
                                     ToolMessage)
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages
from langgraph.config import get_stream_writer

import operator
from mes_agent.agent_tools_api import TOOL_SCHEMAS, DISPATCH
from api.config import settings


ANALYTICS_TOOLS = {
    "get_most_common_codes_API",
    "get_fault_code_summary_API",
    "get_routings"
}
RETRIEVAL_TOOLS = {
    "search_documents",
}


SYSTEM_PROMPT = """
You are an assistant for factory-floor operators. Answer concisely and practically, in the language of the question (Finnish or English).

# Source of truth
Answer ONLY from tool results. Do not use general knowledge, assumptions, or your own calculations.
If the tools return nothing relevant, say plainly that no relevant records were found. Never guess.

# Tools
1. Date tool: returns today's date (YYYY-MM-DD).
2. MES tools:
   - MES API: fetches the raw fault data. Call it first; analytics tools only work on data it has fetched.
   - Analytics tools: search fault codes and their instructions, summarize fault codes, list the most common codes in a category.
     All counts, rankings, trends and summaries must come from these tools. Do not compute or estimate them yourself.
3. Retrieval tools: search the factory knowledge base for past incidents and similar cases.

# Choosing tools
- Fault code mentioned, MES not mentioned → retrieval only.
- MES explicitly mentioned, or the question asks for counts, frequencies, rankings or trends over a period → MES API, then analytics.
- Mixed questions (MES data AND past incidents, e.g. "Is there fault X in MES and has it happened before?") → use both, in this order:
  MES API → analytics → retrieval.
  Wait for the analytics result before calling retrieval, and build the retrieval query from it
  (codes, categories, machines found in the analytics result).

# Dates
- MES data covers 2024-01-01 to 2025-12-31.
- For relative dates ("last week", "this month", "viime kuussa"), call the date tool first and convert to an explicit date range. Never assume today's date.
- If the requested period is entirely outside the coverage, say that no MES data is available for that period and do not call MES tools.
- If it partly overlaps, use the covered part and state which dates the answer covers.

# Retrieval queries
Include every concrete identifier you have: fault code, category, machine or line, and symptom keywords.
Never use vague queries like "this fault" or "the problem above".

# Answer content
- Report only what the tools returned. Do not add causes, steps or instructions that are not in the results.
- Fixes: if the user asks how to fix something or what to do, lead with any past fix that the records show worked.
  If no fix is recorded, say plainly that no recorded fix was found. If the user did not ask about fixes, do not lead with one.
- When the tools return identifiers (incident ID, date, machine), include them so the operator can check the source.
- Put the answer first, then the supporting details. No preamble.

# Tool messages
- If a tool says the call was deferred, read the other results and call it again with an updated query.
- If a tool says the exact call was already made, use the earlier result and do not repeat the call.
- If a tool returns an error, say the data could not be retrieved. Do not fill the gap yourself.
"""

def _make_llm(with_tools:bool)-> Any:
    """Create a LangChain LLM instance with or without tools."""
    llm = ChatOpenAI(
        base_url=settings.OLLAMA_BASE_URL,
        api_key="ollama",
        model_name=settings.OLLAMA_MODEL,
        temperature=0,
    )

    if with_tools:
        llm = llm.bind_tools(TOOL_SCHEMAS)
    return llm

LLM_TOOLS = _make_llm(with_tools=True)
LLM_PLAIN = _make_llm(with_tools=False)

_MAX_TOOL_RESULT_CHARS = 4000
def _render_result(result: dict[str, Any]) -> str:
    """Compact JSON rendering of a tool result for the model, size-bounded."""
    try:
        text = json.dumps(result, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        text = str(result)
    if len(text) > _MAX_TOOL_RESULT_CHARS:
        text = text[:_MAX_TOOL_RESULT_CHARS] + " ...[truncated]"
    return text



class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    tool_calls_log: Annotated[list[dict[str, Any]], operator.add]
    steps: int
    answer: str
    user_message: str

    

def agent_node(state: AgentState) -> dict[str, Any]:
    get_stream_writer()({"stage": "tools", "label": "choosing tools"})
    resp = LLM_TOOLS.invoke(state["messages"])
    update: dict[str, Any] = {"messages": [resp], "steps": state["steps"]+1}
    if not resp.tool_calls:
        update["answer"] = (resp.content or "").strip()
    return update

def tools_node(state: AgentState):

    last = state["messages"][-1]
    print(f"[TOOL CALLS LOG] -> {state['tool_calls_log']} \n") #Debuggins print
    seen = { 
        (e["tool_name"], json.dumps(e["arguments"], sort_keys=True, default=str))
        for e in state["tool_calls_log"]
    }
    has_analytics = any(tc["name"] in ANALYTICS_TOOLS for tc in last.tool_calls)
    new_messages: list[AnyMessage] = []
    log_adds: list[dict[str, Any]] = []
    #src_adds: list[str] = [] #TODO add source (if retrieving where the answer is from)
    for tc in last.tool_calls:
        name = tc["name"]
        args = tc.get("args") or {}
        tc_id = tc["id"]

        if name not in DISPATCH:
            new_messages.append(
                ToolMessage(
                    content=f"Unknown tool '{name}'. Available tools: {', '.join(DISPATCH)}",
                    tool_call_id=tc_id,
                )
            )
   
            continue
        if has_analytics and name in RETRIEVAL_TOOLS:
            new_messages.append(ToolMessage(
                content=(
                    "Deferred: this search was requested before the analytics result "
                    "was available. Read the analytics result, then call this tool again "
                    "with a query that uses it."
                ),
                tool_call_id=tc_id,
            ))
            continue
        dedupe_key = (name, json.dumps(args, sort_keys=True, default=str))
        if dedupe_key in seen:
            new_messages.append(
                ToolMessage(
                    content="This exact call was already made. Use the previous result and write final answer",
                    tool_call_id=tc_id,
                )
            )
            continue
        seen.add(dedupe_key)

        try:
            get_stream_writer()({"stage": "execute", "label": f"Executing tool: {name}"})
            print(f"[CALLING TOOL] -> {name} with args: {args} \n") #Debuggins print
            out = DISPATCH[name](**args)
            result = out.get("result", {})
        except Exception as exc:
            result = {"error": str(exc)}


        log_adds.append({"tool_name": name, "arguments": args, "result": result})

        new_messages.append(ToolMessage(content=_render_result(result=result), tool_call_id=tc_id))

    return {
        "messages": new_messages,
        "tool_calls_log": log_adds,
    }




def force_final_node(state: AgentState) -> dict[str, Any]:
    last = state["messages"][-1]
    notes = [
        ToolMessage(
            content="Tool call budget reached. Write the final answer now from the information already gathered.",
            tool_call_id=tc["id"],
        )
        for tc in last.tool_calls
    ]
    try:
        resp = LLM_PLAIN.invoke(state["messages"] + notes)
        answer = (resp.content or "").strip()
    except Exception:
        answer = ""
    return {"messages": notes, "answer": answer}

def finalize_node(state: AgentState) -> dict[str, Any]:
    get_stream_writer()({"stage": "generate", "label": "answering"})
    answer = (state.get("answer") or "").strip()
    if not answer:
        answer = (
            "I could not provide a grounded answer from the available tools and data"
            "Please try rephrasing your question"
        )
    return {"answer": answer}



def _route_after_agent(state: AgentState)-> str:
    last = state["messages"][-1]
    if getattr(last, "tool_calls", None):
        return "tools" if state["steps"] < settings.MAX_TOOL_ITERS else "force_final"
    return "finalize"



def _build_graph()-> Any:
    g = StateGraph(AgentState)
    g.add_node("agent", agent_node)
    g.add_node("tools", tools_node)
    g.add_node("force_final", force_final_node)
    g.add_node("finalize", finalize_node)
    g.add_edge(START, "agent")
    g.add_conditional_edges(
        "agent",
        _route_after_agent,
        {"tools":"tools", "force_final": "force_final", "finalize": "finalize"}
    )
    g.add_edge("tools", "agent")
    g.add_edge("force_final", "finalize")
    g.add_edge("finalize", END)
    return g.compile(checkpointer=InMemorySaver())


GRAPH = _build_graph()