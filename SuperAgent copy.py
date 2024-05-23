import json
import os
from openai import OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt
from dotenv import load_dotenv
from Tools.ArxivLoader import ArxivTool
from Tools.DorkSearch import DorkSearch
from Tools.DuckduckgoSearch import SearchTool
from Tools.PdfLoader import PdfTool


class GPTApp:
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
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_internet",
                    "description": "Use this function to answer user questions based on web search results.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": f"""
                                        The search query
                                        The query should be returned in plain text.
                                        """,
                            }
                        },
                        "required": ["query"],
                    },
                }
            }
        ]

    @retry(wait=wait_random_exponential(multiplier=1, max=20), stop=stop_after_attempt(3))
    def get_arxiv_article(self, query, num_articles=1):
        arxiv_tool = ArxivTool()
        search_results = arxiv_tool.search_arxiv_and_return_articles(query, num_articles)
        return search_results

    @retry(wait=wait_random_exponential(multiplier=1, max=20), stop=stop_after_attempt(3))
    def search_in(self, query, max_results, allowed_urls):
        dork_search = DorkSearch(max_results, timeout=15)
        return dork_search.run(query, allowed_urls)

    @retry(wait=wait_random_exponential(multiplier=1, max=20), stop=stop_after_attempt(3))
    def read_pdf(self, file_name):
        extractor = PdfTool(file_name)
        print(extractor.extract_text())

    @retry(wait=wait_random_exponential(multiplier=1, max=20), stop=stop_after_attempt(3))
    def search_internet(self, query):
        engine = SearchTool(max_results=5, timeout=15)
        data = engine.duckduckgo_search(query)
        return str(data)

def main():
    load_dotenv()
    GPT_MODEL = "gpt-3.5-turbo"
    api_key = os.environ["OPENAI_API_KEY"]
    app = GPTApp(gpt_model=GPT_MODEL, api_key=api_key)
    user_input = input("Ask Anything: ")
    

    messages = [{"role": "user", "content": user_input}]
    tools = app.generate_tools()
    response = app.chat_completion_request(messages=messages, tools=tools, tool_choice="auto")
    response_message = response.choices[0].message
    messages.append(response_message)


    tool_calls = response_message.tool_calls
    
    print("Running : ",tool_calls[0].function.name)
    print("Searching : ", eval(tool_calls[0].function.arguments)['query'])
    
    if tool_calls:
        tool_call_id = tool_calls[0].id
        tool_function_name = tool_calls[0].function.name
        tool_query_string = eval(tool_calls[0].function.arguments)['query']

        if tool_function_name == 'search_internet':
            results = app.search_internet(tool_query_string)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "name": tool_function_name,
                "content": results
            })

            model_response_with_function_call = app.chat_completion_request(messages=messages)
            print(model_response_with_function_call.choices[0].message.content)
        else:
            print(f"Error: function {tool_function_name} does not exist")
    else:
        print(response_message.content)

if __name__ == "__main__":
    main()