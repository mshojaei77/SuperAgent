from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Qdrant
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from Tools.PdfLoader import PdfTool
import os
from dotenv import load_dotenv
load_dotenv()

'''
pdf_link = "E:\\Codes\\LLM Apps\\SuperAgent\\Tools\\pdf_files\\python.pdf"
loader = PdfTool(pdf_link)
texts = loader.extract_text()
'''
texts = "hello python is a programming laguage"
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)

docs = text_splitter.split_text(texts)
embeddings = OpenAIEmbeddings()
'''
qdrant = Qdrant.from_texts(
    docs,
    embeddings,
    path="/data/vector_db",
    collection_name="my_documents",
)
'''
url = os.getenv('Qdrant_URL')
qdrant_api_key = os.getenv('Qdrant_API_KEY')
qdrant = Qdrant.from_texts(
    docs,
    embeddings,
    url=url,
    prefer_grpc=True,
    api_key=qdrant_api_key,
    collection_name="my_documents",
)

query = "What is python"
found_docs = qdrant.similarity_search(query)
print(found_docs)