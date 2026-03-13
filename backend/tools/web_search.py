import json
from tavily import TavilyClient
from config.settings import settings

class WebSearchTool:
    """
    Web search tool for the Research Agent utilizing the Tavily API.
    """
    def __init__(self):
        self.api_key = settings.TAVILY_API_KEY
        # Attempt to initialize client if API key exists
        self.client = TavilyClient(api_key=self.api_key) if self.api_key else None
    
    def search(self, query: str) -> str:
        """
        Executes a real web search based on the query using Tavily API.
        Extracts title, snippet, and url, and returns summarized text results.
        """
        print(f"[WebSearchTool] Searching for: {query}")
        
        if not self.client:
            return "Error: TAVILY_API_KEY is not configured in environment variables."
            
        try:
            # Call Tavily search API gracefully
            results = self.client.search(query=query)
            
            # Format and return the top search results
            formatted_results = []
            for result in results.get("results", []):
                formatted_results.append({
                    "title": result.get("title", ""),
                    "snippet": result.get("content", ""),
                    "url": result.get("url", "")
                })
                
            return json.dumps(formatted_results, indent=2)
            
        except Exception as e:
            return f"Error executing web search: {str(e)}"
