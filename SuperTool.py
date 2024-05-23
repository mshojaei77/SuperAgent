import os
from openai import OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt
from dotenv import load_dotenv

from Tools.DorkSearch import DorkSearchTool
from Tools.DuckduckgoSearch import SearchTool
from Tools.SerpApiSearch import SerpApiTool

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
        ]
        
        return tools

        
    @retry(wait=wait_random_exponential(multiplier=1, max=5), stop=stop_after_attempt(3))
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
            
    @retry(wait=wait_random_exponential(multiplier=1, max=5), stop=stop_after_attempt(3))
    def custom_site_search(self, query, urls):
        dork_search = DorkSearchTool(max_results=5, timeout=15)
        return dork_search.run(query,urls)
        

def main():
    openai_api_key = os.environ["OPENAI_API_KEY"]
    app = ToolApp(gpt_model="gpt-3.5-turbo", api_key=openai_api_key)

    user_input = "openai news"

    messages = [{"role": "user", "content": user_input}]
    tools = app.generate_tools()

    try:
        response = app.chat_completion_request(messages=messages, tools=tools, tool_choice="auto")
        response_message = response.choices[0].message
        messages.append(response_message)
        tool_calls = response_message.tool_calls
        

        if tool_calls:
            #print(tool_calls)
            
            tool_call_id = tool_calls[0].id
            tool_function_name = tool_calls[0].function.name
            print("Running : ",tool_function_name)

            if tool_function_name == 'search_internet':
                query = eval(tool_calls[0].function.arguments)['query']
                print(f"Searching for {query} in web")
                results = app.search_internet(query)
                
            elif tool_function_name == 'custom_site_search':
                query = eval(tool_calls[0].function.arguments)['query']
                urls = eval(tool_calls[0].function.arguments)['urls']
                print(f"Searching for {query} in {urls}")
                results = app.custom_site_search(query, urls)
                
                
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

