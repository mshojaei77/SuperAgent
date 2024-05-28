import json
from openai import OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt
from dotenv import load_dotenv
import logging
import os
from settings import FILES_DIR

from SuperRag import RagApp

from Knowledge.ArxivLoader import ArxivReader
from Knowledge.PdfLoader import SimplePdfReader
from Knowledge.FileLoader import FileManager
from Knowledge.WebLoader import WebReader
from Knowledge.YoutubeLoader import YoutubeReader

from Tools.PdfSearch import SearchPdfTool
from Tools.DorkSearch import DorkSearchTool
from Tools.DuckduckgoSearch import SearchTool
from Tools.SerpApiSearch import SerpApiTool

logging.basicConfig(level=logging.INFO)

class ToolApp:
    def __init__(self, gpt_model, api_key):
        load_dotenv()
        self.gpt_model = gpt_model
        self.client = OpenAI(api_key=api_key)
        self.rag = RagApp()

    @retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
    def chat_completion_request(self, messages, tools=None, tool_choice=None):
        try:
            response = self.client.chat.completions.create(
                model=self.gpt_model,
                messages=messages,
                tools=tools,
                tool_choice=tool_choice,
            )
            return response
        except Exception as e:
            logging.error("Unable to generate ChatCompletion response")
            logging.error(f"Exception: {e}")
            return e

    def generate_tools(self):
        with open('tools.json') as f:
            tools = json.load(f)

        return tools

    def read_arxiv_article(self, query, num_articles=1):
        try:
            arxiv_tool = ArxivReader()
            search_results = arxiv_tool.search_arxiv_articles(query, num_articles)
            if search_results:
                link = search_results[0].get("pdf_url")
                text = arxiv_tool.read_file(link)
                data = f"Article Information: {search_results} \n\n Article: {text}"
            else:
                logging.info("No search results found.")
        except Exception as e:
            logging.error(f"Error in example usage: {e}")
        context = self.rag.retrieve(query, data)
        return context

    def search_and_read_pdf(self, query, max_results=3):
        search_pdf = SearchPdfTool(max_results)
        result_info = search_pdf.read_pdfs(query=query)
        data = result_info
        context = self.rag.retrieve(query, data)
        return context

    def search_internet(self, query):
        try:
            engine = SearchTool(max_results=5, timeout=15)
            data = engine.duckduckgo_search(query)
            return str(data)
        except Exception as e:
            logging.error(f"Error: {e}")
            try:
                load_dotenv()
                engine = SerpApiTool(query)
                data = engine.execute_search()
                return str(data)
            except Exception as e2:
                logging.error(f"Error: {e2}")
                return "No result found from web"

    def custom_site_search(self, query, urls):
        dork_search = DorkSearchTool(max_results=5, timeout=15)
        data = dork_search.run(query, urls)
        return data

    def read_url(self, url):
        scraper = WebReader(parser='html.parser')
        clean_texts = scraper.scrape_texts(url)
        return " ".join(clean_texts)

    def read_youtube_url(self, video_url):
        tool = YoutubeReader()
        transcript = tool.fetch_transcript(video_url)
        return transcript

    #File Uploades:


    def read_files(self, query, directory_path, urls):
        file_manager = FileManager(ocr_languages=['en', 'fa'], enable_ocr=False)
        
        file_uploaded = False
        
        directory_path = FILES_DIR
        
        filename = input("Please upload a file (example: sample.pdf): ").strip()
        
        if filename:
            file_uploaded = True
            
            
        if filename.lower().endswith(('.txt', '.pdf', '.docx', '.pptx', '.xlsx', '.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
            valid_file = True
        else:
            valid_file = False
        
        if file_uploaded & valid_file:
            file_path = os.path.join(directory_path, filename)
            
            content = file_manager.read(file_path)
            #file_manager.cleanup(file_path)
            print(content)
        else:
            print("Invalid file type.")



    def read_pdf(self, query, file_path):
        extractor = SimplePdfReader()
        data = extractor.extract_text(file_path)
        context = self.rag.retrieve(query, data)
        return context