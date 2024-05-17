import logging
from DuckduckgoSearch import SearchTool
import json
from pathlib import Path
import requests

logging.basicConfig(level=logging.INFO)

class SearchPdfTool:
    def __init__(self, max_results=3, timeout=15):
        self.dork = "filetype:pdf"
        self.tool = SearchTool(max_results=max_results, timeout=timeout)
        self.download_links = []
        self.pdf_path = Path(__file__).parent / "pdf_files"
        if not self.pdf_path.exists():
            self.pdf_path.mkdir(parents=True)


    def search(self, query):

        full_query = query + self.dork
        results = self.tool.duckduckgo_search(full_query)

        parsed_data = json.loads(results)

        for item in parsed_data:
            self.download_links.append(item['href'])


        return self.download_links

    def download_pdf(self, url):
        response = requests.get(url)
        pdf_file_path = self.pdf_path / url.split("/")[-1]
        with open(pdf_file_path, 'wb') as f:
            f.write(response.content)

        logging.info(f"PDF downloaded successfully to {pdf_file_path}")


if __name__ == "__main__" :
    query = input("Enter your query: ")
    search_pdf = SearchPdfTool()
    download_links = search_pdf.search(query)
    for link in download_links:
        search_pdf.download_pdf(link)