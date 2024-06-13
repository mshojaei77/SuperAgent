import logging
from dotenv import load_dotenv
import os
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
logging.basicConfig(level=logging.WARNING)

dir = Path.cwd().absolute()
FILES_DIR = dir / "files"

load_dotenv()
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

class DocumentRetriever:
    def __init__(self, api_key, n=1, search_type='similarity', chunk_size=1000, chunk_overlap=0):
        try:
            print("Initializing DocumentRetriever...")
            if not api_key:
                raise ValueError("API key is required")
            self.api_key = api_key
            self.embeddings = OpenAIEmbeddings(api_key=api_key)
            self.text_splitter = RecursiveCharacterTextSplitter(separators=['</p>','.\n\n'] , chunk_size=chunk_size, chunk_overlap=chunk_overlap)  # Initialize text splitter
            self.n = n
            self.search_type = search_type
        except Exception as e:
            logging.error("Error initializing DocumentRetriever: %s", e)

    def retrieve(self, query, data):
        try:
            print("Starting document retrieval process...")
            documents = self.text_splitter.split_text(str(data)) 
            print(f"Number of document chunks: {len(documents)}")
            print("Creating embeddings & Storing in vector database...")
            vector_db = FAISS.from_texts(documents, self.embeddings)  
            
            results = vector_db.search(query, n_results=self.n, search_type=self.search_type)  
            if not results:
                raise IndexError("Search returned no results")
            top_docs = [doc.page_content for doc in results]
            print("Document retrieval successful.")

            return '\n-------\n'.join(top_docs)
        
        except Exception as e:
            logging.error("Error retrieving documents: %s", e)
            return ""

class ReadFiles():
    def __init__(self, directory):
        self.directory = directory
        
    def read_html_files(self):
        print("Reading HTML files...")
        def read_html_file(file):
            return file.read_text(encoding='utf-8')

        html_files = filter(lambda f: f.suffix == '.html', self.directory.iterdir())
        with ThreadPoolExecutor() as executor:
            contents_list =  list(executor.map(read_html_file, html_files))

        print(f"Number of HTML files read: {len(contents_list)}")
        contents= '\n</>\n'.join(contents_list)
        print(f"Total length of combined contents: {len(contents)} characters")
        
        return contents
    
    def get_images(self,context):
        img_regex = r'<img [^>]*src="([^"]+)"'
        images = re.findall(img_regex, context)
        return images

if __name__ == "__main__":
    directory = FILES_DIR
    query = 'what is dsm5'
    api_key = os.getenv('OPENAI_API_KEY')
    reader = ReadFiles(directory)
    data = reader.read_html_files()
    retriever = DocumentRetriever(api_key, n=1, search_type='similarity', chunk_size=1000, chunk_overlap=0)
    context = retriever.retrieve(query,data)
    print(context)
    images = reader.get_images(context)
    if images:
        print(images)