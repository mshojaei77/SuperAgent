import os
from openai import OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt
from dotenv import load_dotenv

from Knowledge.ArxivLoader import ArxivReader
from Knowledge.PdfLoader import PdfReader
from Knowledge.WebLoader import WebReader
from Knowledge.YoutubeLoader import YoutubeReader

from Tools.PdfSearch import SearchPdfTool
from Tools.DorkSearch import DorkSearchTool
from Tools.DuckduckgoSearch import SearchTool
from Tools.SerpApiSearch import SepApiTool

load_dotenv()

class ToolApp:
    def __init__(self, gpt_model, api_key):
        self.gpt_model = gpt_model
        self.client = OpenAI(api_key=api_key)

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
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_arxiv_article",
                    "description": "Search for articles on Arxiv and return the results.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query."
                            },
                            "num_articles": {
                                "type": "integer",
                                "default": 1,
                                "description": "The number of articles to return."
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "custom_site_search",
                    "description": "Search for specific keywords within a set of Custom URLs",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query."
                            },
                            "urls": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                                "description": "The list of URLs to search within."
                            }
                        },
                        "required": ["query", "urls"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_pdf",
                    "description": "Search for PDF files and return the titles and download paths.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query."
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "The maximum number of results to return."
                            }
                        },
                        "required": ["query", "max_results"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_pdf",
                    "description": "Read the contents of a PDF file.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": """
                                The path or link of the PDF file to read.
                                this function works for local pdf file (e.g E:\pdf_files\python.pdf) and urls (https://www.pdfdownload.com/python.pdf) 
                                """
                            }
                        },
                        "required": ["file_path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_internet",
                    "description": "Search the internet for a query and return the results.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query."
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_url",
                    "description": "Read the contents of a URL as text.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The URL to read."
                            },
                        },
                        "required": ["url"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_youtube_url",
                    "description": "Read the transcript of a YouTube video.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "video_url": {
                                "type": "string",
                                "description": "The URL of the YouTube video."
                            }
                        },
                        "required": ["video_url"]
                    }
                }
            }
        ]
        
        return tools
    
    @retry(wait=wait_random_exponential(multiplier=1, max=20), stop=stop_after_attempt(3))
    def get_arxiv_article(self, query, num_articles=1):
        arxiv_tool = ArxivReader()
        search_results = arxiv_tool.search_arxiv_and_return_articles(query, num_articles)
        return search_results
            
    @retry(wait=wait_random_exponential(multiplier=1, max=20), stop=stop_after_attempt(3))
    def read_pdf(self, file_path):
        extractor = PdfReader()
        print(extractor.extract_text(file_path))

    @retry(wait=wait_random_exponential(multiplier=1, max=20), stop=stop_after_attempt(3))
    def custom_site_search(self, query, urls):
        dork_search = DorkSearchTool(max_results=5, timeout=15)
        return dork_search.run(query,urls)
    
    @retry(wait=wait_random_exponential(multiplier=1, max=20), stop=stop_after_attempt(3))
    def search_pdf(self, query,max_results):
        search_pdf = SearchPdfTool(max_results)
        results = search_pdf.search(query)
        for item in results:
            search_pdf.download_pdf(item['href'])
        info = {
                "titles": [item['title'].replace('PDF', '') for item in results],
                "path": search_pdf.get_pdf_path(),
            }
            
        return info

    @retry(wait=wait_random_exponential(multiplier=1, max=20), stop=stop_after_attempt(3))
    def search_internet(self, query):
        try:
            engine = SearchTool(max_results=5, timeout=15)
            data = engine.duckduckgo_search(query)
            return str(data)
        except Exception as e:
            print(f"Error: {e}")
            try:
                load_dotenv()
                engine = SepApiTool(query)
                data = engine.execute_search()
                return str(data)
            except Exception as e2:
                print(f"Error: {e2}")
                return "No result found from web"
    
    @retry(wait=wait_random_exponential(multiplier=1, max=20), stop=stop_after_attempt(3))
    def read_url(self, url):
        scraper = WebReader(parser='html.parser')
        clean_texts = scraper.scrape_texts(url)
        return " ".join(clean_texts)
        
    @retry(wait=wait_random_exponential(multiplier=1, max=20), stop=stop_after_attempt(3))
    def read_youtube_url(self, vide_url):
        tool = YoutubeReader()
        transcript = tool.fetch_transcript(vide_url)
        return transcript
        

def main():
    openai_api_key = os.environ["OPENAI_API_KEY"]
    app = ToolApp(gpt_model="gpt-3.5-turbo", api_key=openai_api_key)

    user_input = "Search for 'elon musk last tweets' within https://twitter.com"

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
                
            elif tool_function_name == 'get_arxiv_article':
                query = eval(tool_calls[0].function.arguments)['query']
                print(f"Searching for {query} in arxiv")
                results = app.get_arxiv_article(query, num_articles=1)
                
            elif tool_function_name == 'custom_site_search':
                query = eval(tool_calls[0].function.arguments)['query']
                urls = eval(tool_calls[0].function.arguments)['urls']
                print(f"Searching for {query} in {urls}")
                results = app.custom_site_search(query, urls)
                
            elif tool_function_name == 'search_pdf':
                query = eval(tool_calls[0].function.arguments)['query']
                print(f"Searching for PDF files about {query} ")
                results = app.search_pdf(query, max_results=10)
                
            elif tool_function_name == 'read_pdf':
                file_path = eval(tool_calls[0].function.arguments)['file_path']
                print(f"Reading PDF file from {file_path} ")
                results = app.read_pdf(file_path)
                
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
    except Exception as e:
        print("Exception: ", e)


if __name__ == "__main__":
    main()

