import json
from pathlib import Path
import arxiv
from pypdf import PdfReader
import logging

logger = logging.getLogger(__name__)
#logging.basicConfig(level=logging.INFO)

class ArxivTool:
    def __init__(self, search_arxiv= True, read_arxiv_papers= True, download_dir = None):
        self.download_dir = download_dir or Path(__file__).parent / "pdfs_files"
        if search_arxiv:
            self.register(self.search_arxiv_and_return_articles)
        if read_arxiv_papers:
            self.register(self.read_arxiv_papers)

    def register(self, func):
        setattr(self, func.__name__, func)

    def search_arxiv_and_return_articles(self, query: str, num_articles: int = 10):
        client = arxiv.Client()
        logger.info(f"Searching arxiv for: {query}")
        articles = [
            {
                "title": result.title,
                "id": result.get_short_id(),
                "authors": [author.name for author in result.authors],
                "pdf_url": result.pdf_url,
                "summary": result.summary,
                "comment": result.comment,
            }
            for result in client.results(search=arxiv.Search(query=query, max_results=num_articles))
        ]
        return json.dumps(articles, indent=4)

    def read_arxiv_papers(self, id_list, pages_to_read = None):
        download_dir = self.download_dir
        download_dir.mkdir(parents=True, exist_ok=True)
        client = arxiv.Client()
        logger.info(f"Searching arxiv for: {id_list}")
        articles = []
        for result in client.results(search=arxiv.Search(id_list=id_list)):
            article = {
                "title": result.title,
                "id": result.get_short_id(),
                "authors": [author.name for author in result.authors],
                "pdf_url": result.pdf_url,
                "summary": result.summary,
                "comment": result.comment,
            }
            if result.pdf_url:
                logger.info(f"Downloading: {result.pdf_url}")
                pdf_path = result.download_pdf(dirpath=str(download_dir))
                logger.info(f"To: {pdf_path}")
                pdf_reader = PdfReader(pdf_path)
                article["content"] = [
                    {"page": page_number, "text": page.extract_text()}
                    for page_number, page in enumerate(pdf_reader.pages, start=1)
                    if not pages_to_read or page_number <= pages_to_read
                ]
            articles.append(article)
        return json.dumps(articles, indent=4)


# Example usage of ArxivToolkit
if __name__ == "__main__":
    toolkit = ArxivTool()
    search_results = toolkit.search_arxiv_and_return_articles("deep learning", num_articles=5)
    print("Search Results:", search_results)
    paper_content = toolkit.read_arxiv_papers(["2103.03404v1"], pages_to_read=2)
    print("Paper Content:", paper_content)