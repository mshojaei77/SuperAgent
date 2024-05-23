# Importing libraries
from dotenv import load_dotenv
import os
from tenacity import retry, wait_random_exponential, stop_after_attempt

from langchain_openai.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

from Knowledge.ArxivLoader import ArxivReader
from Knowledge.PdfLoader import PdfReader
from Knowledge.WebLoader import WebReader
from Knowledge.YoutubeLoader import YoutubeReader

load_dotenv()
class RagApp:
    def __init__(self, gpt_model, openai_api_key):
        self.client =ChatOpenAI(openai_api_key=openai_api_key, model=gpt_model)
        self.embeddings=OpenAIEmbeddings()
        self.parser = StrOutputParser()
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)

        
    def anwer_with_rag(self,user_input,text_data):
        
        documents = self.text_splitter.split_text(text_data)
        
        data_length = len(text_data)
        chunks_count = len(documents)
        print(f"The data with length {data_length} is split into {chunks_count} chunks")
        
        vector_store = FAISS.from_texts(documents, self.embeddings)
        retriever = vector_store.as_retriever() #Context Retrieved
        print(retriever)
        
        template = """
            Answer the question based on the context below. If you can't answer the question, reply "I don't know".

            ## Context: {context}

            # Question: {question}
            """
            
        prompt = ChatPromptTemplate.from_template(template)
        setup = RunnableParallel(context=retriever, question=RunnablePassthrough())

        chain = setup | prompt | self.client | self.parser
        
        return chain.invoke(user_input)
    
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
    app = RagApp("gpt-3.5-turbo",openai_api_key)
    user_input = "tell me about python"
    text_data = str("pathon is a oop programming language")
    answer = app.anwer_with_rag(user_input,text_data)
    print(answer)
 
if __name__ == "__main__":
    main()


