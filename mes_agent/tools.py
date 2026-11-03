from langchain_core.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from api.config import settings
from tools.core import ANALYTICS, RETRIEVAL

ANALYTICS_TOOLS = {f.__name__ for f in ANALYTICS}
RETRIEVAL_TOOLS = {f.__name__ for f in RETRIEVAL}

async def load_tools():
    if settings.USE_MCP:
        print("Loading tools from MCP")
        client = MultiServerMCPClient({
                "mes": {"url": settings.MCP_URL, "transport": "streamable_http"},
             })
        return await client.get_tools()
    return [tool(f, parse_docstring=True) for f in ANALYTICS + RETRIEVAL]




