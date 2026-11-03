from tools.core import ANALYTICS, RETRIEVAL
from langchain_core.tools import tool

TOOLS = [tool(f, parse_docstring=True) for f in ANALYTICS + RETRIEVAL]
TOOLS_BY_NAME = {t.name: t for t in TOOLS}

ANALYTICS_TOOLS = {f.__name__ for f in ANALYTICS}
RETRIEVAL_TOOLS = {f.__name__ for f in RETRIEVAL}