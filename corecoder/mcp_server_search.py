"""MCP server exposing Bing search via FastMCP.

Requires: BING_SEARCH_API_KEY environment variable (Azure Bing Search API key).
Run as: python -m corecoder.mcp_server_bing
"""

import os
import json
import requests
import httpx
from fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()
mcp = FastMCP("Web-Search")

BING_API_KEY = os.getenv("BING_SEARCH_API_KEY", "")
BING_ENDPOINT = os.getenv(
    "BING_SEARCH_ENDPOINT", "https://api.bing.microsoft.com/v7.0/search"
)
VOLCENGINE_WEB_SEARCH_API_KEY = os.getenv("VOLCENGINE_WEB_SEARCH_API_KEY")


# @mcp.tool()
def duckduckgo_search(query: str, max_results: int = 10) -> str:
    """Search the web using DuckDuckGo. No API key required.

    Args:
        query: The search query string.
        max_results: Number of results to return (1-20). Default 10.
    """
    from duckduckgo_search import DDGS

    max_results = max(1, min(20, max_results))

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
    except Exception as e:
        return f"Error: {e}"

    if not results:
        return f"No results found for: {query}"

    output = []
    for i, r in enumerate(results, 1):
        output.append(f"{i}. {r['title']}\n   {r['href']}\n   {r['body']}")

    return "\n\n".join(output)


# @mcp.tool()
async def bing_search(query: str, count: int = 10) -> str:
    """Search the web using Bing. Returns search results with titles, URLs, and snippets.

    Args:
        query: The search query string.
        count: Number of results to return (1-50). Default 10.
    """
    if not BING_API_KEY:
        return "Error: BING_SEARCH_API_KEY environment variable not set. Get one from https://portal.azure.com"

    count = max(1, min(50, count))
    headers = {"Ocp-Apim-Subscription-Key": BING_API_KEY}
    params = {"q": query, "count": count, "responseFilter": "Webpages"}

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(BING_ENDPOINT, headers=headers, params=params)
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPStatusError as e:
        return f"Error: Bing API returned {e.response.status_code}: {e.response.text[:200]}"
    except Exception as e:
        return f"Error: {e}"

    results = data.get("webPages", {}).get("value", [])
    if not results:
        return f"No results found for: {query}"

    output = []
    for i, r in enumerate(results, 1):
        output.append(f"{i}. {r['name']}\n   {r['url']}\n   {r.get('snippet', '')}")

    return "\n\n".join(output)


@mcp.tool()
async def volcengine_search(query, count) -> str:
    """Search the web using volcengine. Returns search results with titles, URLs, and snippets.

    Args:
        query: The search query string.
        count: Number of results to return (1-50). Default 5.
    """
    body = {
        "Query": query,
        "SearchType": "web",
        "Count": 5,
        "Filter": {"NeedContent": False, "NeedUrl": True},
        "NeedSummary": True,
        "TimeRange": "OneYear",
    }
    # 请求URL
    url = "https://open.feedcoopapi.com/search_api/web_search"

    # 请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {VOLCENGINE_WEB_SEARCH_API_KEY}",
    }

    try:
        # 发送 POST 请求
        response = requests.post(url, headers=headers, json=body)

        # 打印响应状态码
        print(f"Response Status Code: {response.status_code}")
        return response.text

    except Exception as e:
        return f"Web search Error occurred: {str(e)}"


if __name__ == "__main__":
    mcp.run()
