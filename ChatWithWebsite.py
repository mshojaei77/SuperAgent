from Tools.WebLoader import WebScraper
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain.prompts import ChatPromptTemplate

import os
from dotenv import load_dotenv

class WebAssistantAgent:
    def __init__(self):
        load_dotenv()
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.model = ChatOpenAI(openai_api_key=self.OPENAI_API_KEY, model="gpt-3.5-turbo")
        self.embeddings = OpenAIEmbeddings()
        self.scraper = WebScraper(parser='html.parser', timeout=10, cache_expiry=3600, max_cache_size=1000)
        self.parser = StrOutputParser()
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)


    def execute(self, url: str, user_input: str):
        web_context = "\n".join(self.scraper.scrape_texts(url, min_result_length=75))
        documents = self.text_splitter.split_text(web_context)
        vectorstore = FAISS.from_texts(documents, OpenAIEmbeddings())
        retriever = vectorstore.as_retriever()

        template = """
        Answer the question based on the context below. If you can't answer the question, reply "I don't know".

        ##Context: {context}

        #Question: {question}
        """
        prompt = ChatPromptTemplate.from_template(template)
        setup = RunnableParallel(context=retriever, question=RunnablePassthrough())

        chain = setup | prompt | self.model | self.parser
        return chain.invoke(user_input)


if __name__ == "__main__":
    agent = WebAssistantAgent()
    url = input("enter the url: ")
    user_input = input("ask anything? ")
    
    answer = agent.execute(url, user_input)
    print(answer)