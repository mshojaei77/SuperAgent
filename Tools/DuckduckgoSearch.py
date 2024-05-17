import json
from duckduckgo_search import DDGS

class SearchTool:
    def __init__(self, max_results = None, headers = None, proxy: str = None, timeout: int = 10):
        self.headers = headers
        self.proxy = proxy
        self.timeout = timeout
        self.max_results = max_results

    def duckduckgo_search(self, query: str, max_results: int = 5) -> str:
        ddgs = DDGS(headers=self.headers, proxy=self.proxy, timeout=self.timeout)
        return json.dumps(ddgs.text(keywords=query, max_results=(self.max_results or max_results)), indent=2)

# Example usage
if __name__ == "__main__":
    tool = SearchTool(max_results=3, timeout=15)
    query = "python programming"
    results = tool.duckduckgo_search(query)
    print(results)