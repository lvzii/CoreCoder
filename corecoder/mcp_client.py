"""MCP client - discovers and wraps MCP server tools as CoreCoder Tool instances."""

import asyncio
from .tools.base import Tool


class MCPTool(Tool):
    """A Tool backed by an MCP server."""

    def __init__(self, name: str, description: str, parameters: dict, server_path: str):
        self.name = name
        self.description = description
        self.parameters = parameters
        self._server_path = server_path

    def execute(self, **kwargs) -> str:
        try:
            return asyncio.run(self._call_async(kwargs))
        except RuntimeError as e:
            if "asyncio.run()" in str(e):
                return f"Error: MCP tools cannot run inside an existing event loop"
            return f"Error calling MCP tool {self.name}: {e}"
        except Exception as e:
            return f"Error calling MCP tool {self.name}: {e}"

    async def _call_async(self, arguments: dict) -> str:
        from fastmcp import Client

        async with Client(self._server_path) as client:
            result = await client.call_tool(self.name, arguments)

        if hasattr(result, "content"):
            items = result.content
        elif isinstance(result, list):
            items = result
        else:
            return str(result)

        texts = []
        for item in items:
            if hasattr(item, "text"):
                texts.append(item.text)
            else:
                texts.append(str(item))
        return "\n".join(texts) or "(no output)"


def discover_mcp_tools(server_paths: list[str]) -> list[MCPTool]:
    """Connect to MCP servers and discover their tools.

    Args:
        server_paths: Paths to MCP server scripts.

    Returns:
        List of MCPTool instances.
    """
    tools: list[MCPTool] = []
    for path in server_paths:
        try:
            server_tools = asyncio.run(_discover_from_server(path))
            tools.extend(server_tools)
        except Exception as e:
            print(f"Warning: Failed to connect to MCP server '{path}': {e}")
    return tools


async def _discover_from_server(server_path: str) -> list[MCPTool]:
    from fastmcp import Client

    async with Client(server_path) as client:
        tool_list = await client.list_tools()

    return [
        MCPTool(
            name=t.name,
            description=t.description or "",
            parameters=t.inputSchema if hasattr(t, "inputSchema") else {},
            server_path=server_path,
        )
        for t in tool_list
    ]
