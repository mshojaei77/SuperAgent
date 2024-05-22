import json
from DuckduckgoSearch import SearchTool

class DorkSearch:
    def __init__(self, max_results, timeout):
        self.tool = SearchTool(max_results=max_results, timeout=timeout)

    def search(self, query):
        return self.tool.duckduckgo_search(query)

    def filter_results(self, results, urls):
        data = []
        for item in results:
            if any(item.get('href').startswith(url) for url in urls):
                data.append(item)
        return data

    def run(self, query, urls):
        dork = " site:"+" OR site:".join(allowed_urls)
        query = query + dork
        print(query)
        results = self.search(query)
        filtered_data = self.filter_results(results, urls)
        return json.dumps(filtered_data, indent=1)

if __name__ == "__main__":
    search_app = DorkSearch(max_results=30, timeout=15)
    allowed_urls = ['https://twitter.com', 'https://x.com'] #
    query = "gpt-4o"
    print(search_app.run(query, allowed_urls))