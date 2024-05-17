# Importing libraries
from dotenv import load_dotenv
import os
import logging
import streamlit as st
from langchain_core.output_parsers import StrOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai.chat_models import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import ChatPromptTemplate
from Tools.WebLoader import WebScraper
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
import sys

# Setting up logging
logging.basicConfig(level=logging.INFO)

class WebAssistantAgent:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = ChatOpenAI(openai_api_key=self.api_key, model="gpt-3.5-turbo")
        self.embeddings = OpenAIEmbeddings()
        self.scraper = WebScraper(parser='html.parser', timeout=10, cache_expiry=3600, max_cache_size=1000)
        self.parser = StrOutputParser()
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)

    def execute(self, url: str, user_input: str) -> str:
        try:
            web_context = "\n".join(self.scraper.scrape_texts(url, min_result_length=75))
            if web_context:
                logging.info(f"Website Scraped. Length: {len(web_context)}")

            documents = self.text_splitter.split_text(web_context)
            if documents:
                logging.info(f"Website Texts split into {len(documents)} chunks.")

            vector_store = FAISS.from_texts(documents, self.embeddings)
            retriever = vector_store.as_retriever()
            if retriever:
                logging.info(f"Context Retrieved: {retriever}")

            template = """
            Answer the question based on the context below. If you can't answer the question, reply "I don't know".

            ## Context: {context}

            # Question: {question}
            """
            prompt = ChatPromptTemplate.from_template(template)
            setup = RunnableParallel(context=retriever, question=RunnablePassthrough())

            chain = setup | prompt | self.model | self.parser
            return chain.invoke(user_input)
        except Exception as e:
            logging.error(f"An error occurred during execution: {e}")
            return "An error occurred while processing your request. Please try again."

if __name__ == "__main__":
    agent = WebAssistantAgent()
    url = input("Enter the URL: ")
    user_input = input("Ask anything? ")
    answer = agent.execute(url, user_input)
    print(answer)
