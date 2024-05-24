from pathlib import Path
import arxiv
import sys
sys.path.append('E:\\Codes\\LLM Apps\\SuperAgent\\Knowledge\\')
from PdfLoader import SimplePdfReader

class ArxivReader:
    def __init__(self, search_arxiv= True, read_arxiv_papers= True, download_dir = None):
        self.download_dir = download_dir or Path(__file__).parent / "files"

    def search_arxiv_articles(self, query: str, num_articles: int = 10):
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
    
    def read_file(self,link):
        extractor = SimplePdfReader()
        
        text = extractor.extract_text(link)
        return text



# Example usage of ArxivToolkit
if __name__ == "__main__":
    arxiv_tool = ArxivReader()
    search_results = arxiv_tool.search_arxiv_articles(query="python", num_articles=1)
    link = search_results[0].get("pdf_url")
    text = arxiv_tool.read_file(link)
    data = f"Article Information: {search_results} \n\n Article: {text}"
    print(data)