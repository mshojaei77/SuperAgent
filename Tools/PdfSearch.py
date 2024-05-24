from pathlib import Path
import requests
import ssl
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
import sys
sys.path.append('E:\\Codes\\LLM Apps\\SuperAgent\\Knowledge\\')
sys.path.append('E:\\Codes\\LLM Apps\\SuperAgent\\Tools\\')
from PdfLoader import SimplePdfReader
from DuckduckgoSearch import SearchTool


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
        full_query = query + " " + self.dork
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

    def read_pdfs(self, query):
        extractor = SimplePdfReader()
        results = self.search(query=query)

        for item in results:
            self.download_pdf(item['href'])

        text = ""
        for pdf_file in self.pdf_path.glob("*.pdf"):
            text += extractor.extract_text(str(pdf_file))

        info = {
            "titles": [item['title'].replace('PDF', '') for item in results],
            "content": text,
        }

        return info


if __name__ == "__main__":
    search_pdf = SearchPdfTool(max_results=3)
    query = "python"
    result_info = search_pdf.read_pdfs(query=query)
    print(result_info)