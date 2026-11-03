from fastmcp import FastMCP 
from tools.core import ALL_TOOLS

mcp = FastMCP("mes")

for f in ALL_TOOLS:
    mcp.add_tool(f)

if __name__=="__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8001)