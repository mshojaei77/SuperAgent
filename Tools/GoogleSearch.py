from googlesearch import search
import requests
from WebLoader import WebTool
from concurrent.futures import ThreadPoolExecutor
import json

class GoogleTool:

    def __init__(self, query, num_results, lang):
        self.query = query
        self.num_results = num_results
        self.lang = lang
        self.scraper = WebTool(
            parser='html.parser',
            headers=None,
            proxy=None,
            timeout=10,
            cache_expiry=3600,
            max_cache_size=1000,
            max_workers=None
        )

    def search_and_scrape(self):
        links = search(self.query, num_results=self.num_results, lang=self.lang)
        def scrape_url(url):
            return {
                "href": url,
                "body": self.scraper.scrape_texts(url, min_result_length=70)
            }
        with ThreadPoolExecutor() as executor:
            clean_texts = list(executor.map(scrape_url, links))

        return json.dumps(clean_texts, indent=4)


if __name__ == "__main__":
    query = "python"
    num_results = 10
    lang = 'en'
    search_agent = GoogleTool(query, num_results, lang)
    results = search_agent.search_and_scrape()
    print(results)