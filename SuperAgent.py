import os
import json
from openai import OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt
from dotenv import load_dotenv
import uuid

from SuperMemory import MemoryApp
from SuperRag import RagApp

import sys
sys.path.append('E:\\Codes\\LLM Apps\\SuperAgent\\')

from Knowledge.ArxivLoader import ArxivReader
from Knowledge.PdfLoader import SimplePdfReader
from Knowledge.FileLoader import FileReader
from Knowledge.WebLoader import WebReader
from Knowledge.YoutubeLoader import YoutubeReader

from Tools.PdfSearch import SearchPdfTool
from Tools.DorkSearch import DorkSearchTool
from Tools.DuckduckgoSearch import SearchTool
from Tools.SerpApiSearch import SerpApiTool

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
            print("Unable to generate ChatCompletion response")
            print(f"Exception: {e}")
            return e

    def generate_tools(self):
        with open('tools.json') as f:
            tools = json.load(f)

        return tools

    def read_arxiv_article(self, query, num_articles=1):
        arxiv_tool = ArxivReader()
        search_results = arxiv_tool.search_arxiv_articles(query, num_articles)
        link = search_results[0].get("pdf_url")
        text = arxiv_tool.read_file(link)
        data = f"Article Information: {search_results} \n\n Article: {text}"
        context = self.rag.retrieve(query, data)
        return context

    def read_files(self, query, directory_path, urls): 
        reader = FileReader(directory_path)
        contents = reader.download_and_read_files(urls)
        for filename, content in contents.items():
            if isinstance(content, dict) and 'images' in content:
                data = (f"Contents of {filename}:\nText:\n{content['text']}\nImages: {content['images']}\nImage Text:\n{content['image_text']}\n")
            else:
                data = (f"Contents of {filename}:\n{content}\n")

        context = self.rag.retrieve(query, data)
        return context

    def read_pdf(self, query, file_path): 
        extractor = SimplePdfReader()
        data = extractor.extract_text(file_path)
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
            print(f"Error: {e}")
            try:
                load_dotenv()
                engine = SerpApiTool(query)
                data = engine.execute_search()
                return str(data)
            except Exception as e2:
                print(f"Error: {e2}")
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


def main():
    openai_api_key = os.environ["OPENAI_API_KEY"]
    app = ToolApp(gpt_model="gpt-3.5-turbo", api_key=openai_api_key)
    memory_app = MemoryApp(table_name="chat_sessions", db_path="Memory\\memory.db")

    user_input = "hello chatgpt"

    messages = [{"role": "user", "content": user_input}]
    tools = app.generate_tools()

    try:
        response = app.chat_completion_request(messages=messages, tools=tools, tool_choice="auto")
        response_message = response.choices[0].message
        messages.append(response_message)
        tool_calls = response_message.tool_calls

        if tool_calls:
            print(tool_calls)

            tool_call_id = tool_calls[0].id
            tool_function_name = tool_calls[0].function.name
            print("Running : ",tool_function_name)

            if tool_function_name == 'search_internet':
                query = eval(tool_calls[0].function.arguments)['query']
                print(f"Searching for {query} in web")
                results = app.search_internet(query)

            elif tool_function_name == 'read_arxiv_article':
                query = eval(tool_calls[0].function.arguments)['query']
                print(f"Searching for {query} in arxiv")
                results = app.read_arxiv_article(query, num_articles=1)

            elif tool_function_name == 'custom_site_search':
                query = eval(tool_calls[0].function.arguments)['query']
                urls = eval(tool_calls[0].function.arguments)['urls']
                print(f"Searching for {query} in {urls}")
                results = app.custom_site_search(query, urls)

            elif tool_function_name == 'search_and_read_pdf': 
                query = eval(tool_calls[0].function.arguments)['query']
                print(f"Searching for PDF files about {query} ")
                results = app.search_and_read_pdf(query, max_results=10) 
                
            elif tool_function_name == 'read_pdf':
                file_path = eval(tool_calls[0].function.arguments)['file_path']
                print(f"Reading PDF file from {file_path} ")
                results = app.read_pdf(query, file_path)

            elif tool_function_name == 'read_url':
                url = eval(tool_calls[0].function.arguments)['url']
                print(f"Reading {url} ")
                results = app.read_url(url)

            elif tool_function_name == 'read_youtube_url':
                query = eval(tool_calls[0].function.arguments)['video_url']
                results = app.read_youtube_url(query)

            else:
                print(f"Error: function {tool_function_name} does not exist")

            messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "name": tool_function_name,
                    "content": results
                })

            model_response_with_function_call = app.chat_completion_request(messages=messages)

            print(model_response_with_function_call.choices[0].message.content)


            


        else:
            print(response_message.content)

        conversation_id = str(uuid.uuid4())

        for message in messages:
            if isinstance(message, dict):  # Check if message is a dictionary
                agent_role = message['role']
                message_content = message['content']
            else:  # Otherwise, assume it's a ChatCompletionMessage object
                agent_role = message.role
                message_content = message.content
            
            # Note: tool_calls needs to be handled similarly if it's part of the ChatCompletionMessage object
            memory_app.save_message({
                "conversation_id": conversation_id,
                "agent": agent_role,
                "message": message_content,
                "knowledge_source": tool_calls,  # Ensure this is correctly passed or handled
            })

        memory_app.close()

    except Exception as e:
        print("Exception: ", e)


if __name__ == "__main__":
    main()