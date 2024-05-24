from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

class RagApp:
    def __init__(self):
        load_dotenv()
        self.embeddings = OpenAIEmbeddings()
        self.parser = StrOutputParser()
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)

    def retrieve(self, query, data):
        documents = self.text_splitter.split_text(str(data))
        vector_db = FAISS.from_texts(documents, self.embeddings)  #

        top_docs = vector_db.search(query, n_results=5, search_type='similarity') 

        return top_docs

if __name__ == "__main__":
    data = "Python is a high-level, general-purpose programming language. Its design philosophy emphasizes code readability with the use of significant indentation. Python is dynamically typed and garbage-collected. It supports multiple programming paradigms, including structured, object-oriented and functional"
    query = "python"
    rag = RagApp()
    context = rag.retrieve(query, data)
    print(context)