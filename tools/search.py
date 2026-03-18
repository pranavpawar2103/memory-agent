from tavily import TavilyClient
import os

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def web_search(query: str) -> str:
    response = client.search(query=query, max_results=3)
    results = response.get("results", [])
    output = ""
    for r in results:
        content = r['content'][:500]      # increase from default
        output += f"Title: {r['title']}\nURL: {r['url']}\nSummary: {content}\n\n"
    return output or "No results found."