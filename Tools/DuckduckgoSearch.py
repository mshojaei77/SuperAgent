import json
from duckduckgo_search import DDGS, exceptions
import time
import random
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional, Dict, List

class SearchTool:
    def __init__(self, max_results: Optional[int] = None, headers: Optional[Dict[str, str]] = None, proxy: Optional[str] = None, timeout: int = 10):
        self.headers = headers or {"User-Agent": "Mozilla/5.0"}
        self.proxy = proxy
        self.timeout = timeout
        self.max_results = max_results
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        session = requests.Session()
        retries = Retry(total=5, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retries)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def duckduckgo_search(self, query: str, max_results: int = 5) -> List[Dict]:
        ddgs = DDGS(headers=self.headers, proxy=self.proxy, timeout=self.timeout)
        retries = 5
        backoff_factor = 0.5
        for attempt in range(retries):
            try:
                results = ddgs.text(keywords=query, max_results=(self.max_results or max_results))
                return results
            except exceptions.RatelimitException as e:
                if attempt < retries - 1:
                    backoff_time = (2 ** attempt) * backoff_factor + random.random() * 0.5
                    print(f"RatelimitException: {e}. Retrying in {backoff_time:.2f} seconds...")
                    time.sleep(backoff_time)
                else:
                    print(f"RatelimitException: {e}. Failed after {retries} retries.")
                    return []

if __name__ == "__main__":
    tool = SearchTool(max_results=30, timeout=15)
    query = " gpt-4o"
    data = tool.duckduckgo_search(query)
    print(json.dumps(data, indent=1))