import os
import logging
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
# Set the environment variable to allow duplicate OpenMP libraries
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

logging.basicConfig(level=logging.WARNING)

class RagApp:
    def __init__(self):
        try:
            logging.info("Loading environment variables...")
            load_dotenv()  # Load environment variables from a .env file
            logging.info("Initializing embeddings...")
            self.embeddings = OpenAIEmbeddings()  # Initialize embeddings
            logging.info("Initializing output parser...")
            self.parser = StrOutputParser()  # Initialize output parser
            logging.info("Initializing text splitter...")
            self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)  # Initialize text splitter
            logging.info("Initialization complete.")
        except Exception as e:
            logging.error(f"Initialization error: {e}")

    def retrieve(self, query, data):
        try:
            logging.info("Splitting text into chunks...")
            documents = self.text_splitter.split_text(str(data))  # Split text into chunks
            logging.info("Creating FAISS vector database from text chunks...")
            vector_db = FAISS.from_texts(documents, self.embeddings)  # Create FAISS vector database from text chunks

            logging.info("Searching for top documents...")
            top_docs = [doc.page_content for doc in vector_db.search(query, n_results=5, search_type='similarity')]  # Search for top documents

            logging.info("Search complete.")
            return ' '.join(top_docs)
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return ""

def main():
    try:
        data = ("Python is a high-level, general-purpose programming language. Its design philosophy emphasizes code readability "
                "with the use of significant indentation. Python is dynamically typed and garbage-collected. It supports multiple "
                "programming paradigms, including structured, object-oriented and functional")
        query = "python"

        logging.info("Creating RagApp instance...")
        rag = RagApp()
        logging.info("Retrieving context...")
        context = rag.retrieve(query, data)
        logging.info("Retrieved context:")
        print(context)
    except Exception as e:
        logging.error(f"An error occurred in main: {e}")

if __name__ == "__main__":
    main()