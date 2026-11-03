from tools.retrieve_tools import retrieve_manuals, retrieve_case
from typing import Any


def _r(result: dict[str, Any]):
    return {"result": result}

def _missing(param: str):
    return _r({"message": f"Missing required parameter: {param}"})




def tool_retrieve(query):
    """
    Tool function to retrieve relevant information based on a query.
    This function can be used as a tool in the chat pipeline.
    """
    query = (str(query).strip() if query is not None else "")
    print(f"[CALLING RETRIEVE] QUERY: {query}")
    if not query:
        return _missing("query")
    return _r(retrieve_manuals(query))


def tool_troubleshoot_lookup(query: str, exclude: list[str]|None = None):
    """
    Use this tool ONLY when a machine fails, throws an error/alarm code,
    makes strange noises, or breaks down mechanically.
    """
    query = (str(query).strip() if query is not None else "")
    print(f"[CALLING CASE RETRIEVE] QUERY: {query}")
    if not query:
        return _missing("query")
    return _r(retrieve_case(query=query, exclude=exclude))


#NOTE not used since do not require tool calling
TOOL_SCHEMAS = [tool_retrieve] #NOTE add more when more tools
