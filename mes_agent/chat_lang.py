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
from pydantic import ValidationError

import operator
from mes_agent.tools import TOOLS, TOOLS_BY_NAME, ANALYTICS_TOOLS, RETRIEVAL_TOOLS
from mes_agent.analytics.tool_core import get_date
from api.config import settings



SYSTEM_PROMPT_TEMPLATE = """
You are an assistant for factory-floor operators. Answer concisely and practically, in the language of the question (Finnish or English).

Today's date is {today}.

# Source of truth
Answer ONLY from tool results. Do not use general knowledge, assumptions, or your own calculations.
If the tools return nothing relevant, say plainly that no relevant records were found. Never guess.

# Tools
1. get_most_common_codes: ranks the most common values in MES data.
   - data="faults" for fault records, data="operations" for production operations.
   - group_by takes column names, not values. For example, group_by=["fault_code"] ranks fault codes;
     group_by=["work_center_key", "fault_code"] ranks fault codes per work center.
   - metric="count" for how often something happened, metric="duration" for time lost.
   - All counts, rankings and comparisons must come from this tool. Do not compute or estimate them yourself.
2. get_routings: shows how parts of a part family (e.g. Turned, Weldment, SheetMetal) have been routed
   in past jobs, most common routes first. Uses all MES history; it has no date range.
3. search_documents: searches the knowledge base (fault logs, past incidents, reference documents)
   for causes, fixes and similar cases.

# Choosing tools
- Fault code or symptom mentioned, MES data not asked for → search_documents only.
- Counts, frequencies, rankings or time lost over a period, or MES explicitly mentioned → get_most_common_codes.
- How a part or new product should be routed, or which work centers a part family passes through → get_routings.
- Mixed questions (MES data AND past incidents, e.g. "Is fault X in MES and has it happened before?"):
  call get_most_common_codes first. Wait for its result, then call search_documents with a query
  built from it (codes, categories, work centers found in the result).
- To check one specific fault code in MES: rank fault codes with group_by=["fault_code"] for the period
  and look for that code in the result. If it is not in the result, say it is not among the top n codes;
  do not claim it never occurred.

# Dates
- MES data covers 2024-01-01 to 2025-12-31.
- Convert relative dates ("last week", "this month", "viime kuussa") into explicit YYYY-MM-DD ranges using today's date above.
- If the requested period is entirely outside the coverage, say that no MES data is available for that period and do not call MES tools.
- If it partly overlaps, use the covered part and state which dates the answer covers.
- If no period is given for a ranking question, use the full coverage and say so in the answer.

# Search queries
Include every concrete identifier you have: fault code, category, work center or line, and symptom keywords.
Never use vague queries like "this fault" or "the problem above".

# Answer content
- Report only what the tools returned. Do not add causes, steps or instructions that are not in the results.
- Fixes: if the user asks how to fix something or what to do, lead with any past fix that the records show worked.
  If no fix is recorded, say plainly that no recorded fix was found. If the user did not ask about fixes, do not lead with one.
- Routings: present them as routes used in past jobs, not as an approved process plan.
- When the tools return identifiers (incident ID, date, work center, job), include them so the operator can check the source.
- Put the answer first, then the supporting details. No preamble.

# Tool messages
- If a tool says the call was deferred, read the other results and call it again with an updated query.
- If a tool says the exact call was already made, use the earlier result and do not repeat the call.
- If a tool reports invalid arguments, correct the arguments and call it again.
- If a tool returns any other error, say the data could not be retrieved. Do not fill the gap yourself.
"""
SYSTEM_PROMPT = SYSTEM_PROMPT_TEMPLATE.format(today=get_date())

def _make_llm(with_tools:bool)-> Any:
    """Create a LangChain LLM instance with or without tools."""
    llm = ChatOpenAI(
        base_url=settings.OLLAMA_BASE_URL,
        api_key="ollama",
        model_name=settings.OLLAMA_MODEL,
        temperature=0,
    )

    if with_tools:
        llm = llm.bind_tools(tools=TOOLS)
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

        t = TOOLS_BY_NAME.get(name)
        if t is None:
            new_messages.append(ToolMessage(
                content=f"Unknown tool '{name}'. Available tools: {','.join(TOOLS_BY_NAME)}",
                tool_call_id=tc_id,
            ))
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
            result = t.invoke(args)

        except ValidationError as exc:
            result = {"error": f"Invalid arguments for {name}: {exc}. Fix the arguments and call again"}
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