import logging
import streamlit as st
from SuperAgent import ToolApp
from SuperMemory import MemoryApp
from dotenv import load_dotenv
import os
import uuid

# Setup logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()

# Initialize SuperAgent and SuperMemory apps
openai_api_key = os.environ["OPENAI_API_KEY"]
app = ToolApp(gpt_model="gpt-3.5-turbo", api_key=openai_api_key)
memory_app = MemoryApp(table_name="chat_sessions", db_path="Memory/memory.db")
conversation_id = str(uuid.uuid4())

# User input widget
user_input = st.text_input("Enter your query:")

# Generate tools based on user input
if user_input:
    logging.info("User input received")
    messages = [{"role": "user", "content": user_input}]

    try:
        tools = app.generate_tools()
    except Exception as e:
        st.error(f"Error generating tools: {e}")
        logging.error(f"Error generating tools: {e}")
        tools = []

    if tools:
        try:
            logging.info("Sending chat completion request")
            response = app.chat_completion_request(messages=messages, tools=tools, tool_choice="auto")
            response_message = response.choices[0].message
            messages.append(response_message)
            tool_calls = response_message.tool_calls

            if tool_calls:
                logging.info(f"Tool Calls: {tool_calls}")

                tool_call_id = tool_calls[0].id
                tool_function_name = tool_calls[0].function.name
                with st.spinner(f"Running: {tool_function_name}"):
                    logging.info(f"Running tool function: {tool_function_name}")

                    try:
                        # Execute tool calls based on function names
                        if tool_function_name == 'search_internet':
                            query = eval(tool_calls[0].function.arguments)['query']
                            with st.spinner(f"Searching for {query} in web"):
                                logging.info(f"Searching internet with query: {query}")
                                results = app.search_internet(query)
                                logging.info(results)

                        elif tool_function_name == 'read_arxiv_article':
                            query = eval(tool_calls[0].function.arguments)['query']
                            with st.spinner(f"Searching for {query} in arxiv"):
                                results = app.read_arxiv_article(query, num_articles=1)

                        elif tool_function_name == 'custom_site_search':
                            query = eval(tool_calls[0].function.arguments)['query']
                            urls = eval(tool_calls[0].function.arguments)['urls']
                            with st.spinner(f"Searching for {query} in {urls}"):
                                results = app.custom_site_search(query, urls)

                        elif tool_function_name == 'search_and_read_pdf':
                            query = eval(tool_calls[0].function.arguments)['query']
                            with st.spinner(f"Searching for PDF files about {query} "):
                                results = app.search_and_read_pdf(query, max_results=10)

                        elif tool_function_name == 'read_pdf':
                            file_path = eval(tool_calls[0].function.arguments)['file_path']
                            with st.spinner(f"Reading PDF file from {file_path} "):
                                results = app.read_pdf(file_path)

                        elif tool_function_name == 'read_url':
                            url = eval(tool_calls[0].function.arguments)['url']
                            with st.spinner(f"Reading {url} "):
                                results = app.read_url(url)

                        elif tool_function_name == 'read_youtube_url':
                            query = eval(tool_calls[0].function.arguments)['video_url']
                            with st.spinner(f"Reading {query} "):
                                results = app.read_youtube_url(query)

                        else:
                            logging.info(f"Error: function {tool_function_name} does not exist")
                            results = None

                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call_id,
                            "name": tool_function_name,
                            "content": results
                        })

                    except Exception as e:
                        st.error(f"Error while executing tool function {tool_function_name}: {e}")
                        logging.error(f"Error while executing tool function {tool_function_name}: {e}")

                try:
                    model_response_with_function_call = app.chat_completion_request(messages=messages)
                    st.write(model_response_with_function_call.choices[0].message.content)
                except Exception as e:
                    st.error(f"Error in chat completion with function call: {e}")
                    logging.error(f"Error in chat completion with function call: {e}")

            else:
                st.write(response_message.content)
                logging.info("No tool calls in response message")

            for message in messages:
                if isinstance(message, dict):  # Check if message is a dictionary
                    agent_role = message['role']
                    message_content = message['content']
                else:  # Otherwise, assume it's a ChatCompletionMessage object
                    agent_role = message.role
                    message_content = message.content

                try:
                    memory_app.save_message({
                        "conversation_id": conversation_id,
                        "agent": agent_role,
                        "message": message_content,
                        "knowledge_source": str(tool_calls[0].function.name) if tool_calls else None,  # Handle if tool_calls is empty
                    })
                except Exception as e:
                    st.error(f"Error saving message to memory: {e}")
                    logging.error(f"Error saving message to memory: {e}")

            try:
                memory_app.close()
            except Exception as e:
                st.error(f"Error closing memory app: {e}")
                logging.error(f"Error closing memory app: {e}")

        except Exception as e:
            st.error(f"Exception: {e}")
            logging.error(f"Exception occurred: {e}")

else:
    st.warning("Please enter a query.")
    logging.warning("User did not enter a query")