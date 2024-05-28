import arxiv

import sys
from settings import BASE_DIR, FILES_DIR
sys.path.append(BASE_DIR)

from Knowledge.PdfLoader import SimplePdfReader


class ArxivReader:
    def __init__(self, search_arxiv=True, read_arxiv_papers=True):
        try:
            self.download_dir = FILES_DIR 
        except Exception as e:
            print(f"Error initializing download_dir: {e}")
            raise

    def search_arxiv_articles(self, query: str, num_articles: int = 10):
        try:
            client = arxiv.Client()
            print(f"Searching arxiv for: {query}")
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
            return articles
        except Exception as e:
            print(f"Error during arxiv search: {e}")
            return []

    def read_file(self, link):
        try:
            extractor = SimplePdfReader()
            text = extractor.extract_text(link)
            return text
        except FileNotFoundError as e:
            print(f"File not found: {e}")
        except Exception as e:
            print(f"Error reading file: {e}")
        return ""

# Example usage of ArxivToolkit
if __name__ == "__main__":
    try:
        arxiv_tool = ArxivReader()
        search_results = arxiv_tool.search_arxiv_articles(query="transformers", num_articles=1)
        if search_results:
            link = search_results[0].get("pdf_url")
            text = arxiv_tool.read_file(link)
            data = f"Article Information: {search_results} \n\n Article: {text}"
            print(data)
        else:
            print("No search results found.")
    except Exception as e:
        print(f"Error in example usage: {e}")