import logging
import time
import random
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional, Dict, List
from duckduckgo_search import DDGS, exceptions

# Constants for configuration
DEFAULT_HEADERS = {"User-Agent": "Mozilla/5.0"}
DEFAULT_TIMEOUT = 10
DEFAULT_MAX_RESULTS = 30
RETRY_TOTAL = 3
RETRY_BACKOFF_FACTOR = 0.5
RETRY_STATUS_FORCELIST = [429, 500, 502, 503, 504]

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

class SearchTool:
    def __init__(self, max_results: Optional[int] = DEFAULT_MAX_RESULTS, headers: Optional[Dict[str, str]] = None, 
                 proxy: Optional[str] = None, timeout: int = DEFAULT_TIMEOUT):
        """
        Initialize the SearchTool with optional headers, proxy, and timeout settings.
        """
        self.headers = headers or DEFAULT_HEADERS
        self.proxy = proxy
        self.timeout = timeout
        self.max_results = max_results
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """
        Create a configured requests session with retry logic and connection pooling.
        """
        session = requests.Session()
        retries = Retry(total=RETRY_TOTAL, backoff_factor=RETRY_BACKOFF_FACTOR, status_forcelist=RETRY_STATUS_FORCELIST)
        adapter = HTTPAdapter(max_retries=retries, pool_connections=10, pool_maxsize=10)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def duckduckgo_search(self, query: str, max_results: Optional[int] = None) -> List[Dict]:
        """
        Perform a DuckDuckGo search for the given query, handling rate limits and retries.
        """
        max_results = max_results or self.max_results
        logging.info(f"Starting search for: {query} with max_results={max_results}")
        ddgs = DDGS(headers=self.headers, proxy=self.proxy, timeout=self.timeout)

        for attempt in range(RETRY_TOTAL):
            try:
                results = ddgs.text(keywords=query, max_results=max_results)
                logging.info(f"Search successful. Found {len(results)} results.")
                return results
            except exceptions.RatelimitException as e:
                if attempt < RETRY_TOTAL - 1:
                    backoff_time = (2 ** attempt) * RETRY_BACKOFF_FACTOR + random.random() * 0.5
                    logging.warning(f"RatelimitException: {e}. Retrying in {backoff_time:.2f} seconds...")
                    time.sleep(backoff_time)
                else:
                    logging.error(f"RatelimitException: {e}. Failed after {RETRY_TOTAL} retries.")
                    return []
            except requests.RequestException as req_e:
                logging.error(f"RequestException: {req_e}. Check your network connection or other request parameters.")
                return []
            except Exception as ex:
                logging.error(f"Unexpected Exception: {ex}. An unexpected error occurred.")
                return []

if __name__ == "__main__":
    try:
        tool = SearchTool(max_results=30, timeout=15)
        query = "gpt-4o"
        data = tool.duckduckgo_search(query)
        print(data)
    except Exception as ex:
        logging.error(f"Unexpected Exception in main: {ex}.")

