from Tools.DuckduckgoSearch import SearchTool
from pathlib import Path
import requests
import ssl
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager


class SslAdapter(HTTPAdapter):
    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context or ssl.create_default_context()
        super().__init__(**kwargs)

    def init_poolmanager(self, *args, **kwargs):
        kwargs["ssl_context"] = self.ssl_context
        return super().init_poolmanager(*args, **kwargs)


class SearchPdfTool:
    def __init__(self, max_results=3, timeout=15):
        self.dork = "filetype:pdf"
        self.tool = SearchTool(max_results=max_results, timeout=timeout)
        self.download_links = []
        self.pdf_path = Path(__file__).parent / "pdf_files"
        if not self.pdf_path.exists():
            self.pdf_path.mkdir(parents=True)
        self.session = requests.Session()
        self.session.mount("https://", SslAdapter())


    def search(self, query):

        full_query = query + self.dork
        results = self.tool.duckduckgo_search(full_query)

        return results

    def download_pdf(self, url):
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            pdf_file_path = self.pdf_path / url.split("/")[-1]
            with open(pdf_file_path, 'wb') as f:
                f.write(response.content)
        except requests.exceptions.Timeout:
            print(f"Download timed out: '{url}'")
        except requests.exceptions.HTTPError as err:
            print(f"HTTP error occurred: {err}")
        except requests.exceptions.RequestException as err:
            print(f"Error occurred: {err}")
        except PermissionError:
            print(f"Permission denied: '{pdf_file_path}'")

    def get_pdf_path(self):
        return str(self.pdf_path)


if __name__ == "__main__" :
        search_pdf = SearchPdfTool(max_results=3)
        results = search_pdf.search(query=input("query: "))
        for item in results:
            search_pdf.download_pdf(item['href'])
        info = {
                "titles": [item['title'].replace('PDF', '') for item in results],
                "path": search_pdf.get_pdf_path(),
            }
            
        print(info)