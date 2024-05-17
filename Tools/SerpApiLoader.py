from serpapi import GoogleSearch
from dotenv import load_dotenv
import os

class SearchService:
    def __init__(self, query):
        self.query = query
        self.api_key = os.getenv("SERPAPI_KEY")
        self.search_instance = None

    def execute_search(self):
        self.search_instance = GoogleSearch({
            "q": self.query,
            "api_key": self.api_key
        })
        return self.search_instance.get_dict() if self.search_instance else None


if __name__ == "__main__":
    load_dotenv()
    query = input("Enter your query: ")
    search_service = SearchService(query)
    results = search_service.execute_search()
    print(results)