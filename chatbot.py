from rag import ReadFiles, DocumentRetriever
from responder import RagResponder

import os
from dotenv import load_dotenv
import logging
load_dotenv()
logging.basicConfig(level=logging.WARNING, format='%(message)s')


query = 'what is Anxiety Diagnostic Features'
FILES_DIR = dir / "files"
api_key = os.getenv('OPENAI_API_KEY')
model = 'gpt-3.5-turbo'

#Read file and Search and Retrive in them
reader = ReadFiles(directory=FILES_DIR)
data = reader.read_html_files()
retriever = DocumentRetriever(api_key, n=1, search_type='similarity', chunk_size=1000, chunk_overlap=0)
context = retriever.retrieve(query,data)
print(context)

# Get the answer
responder = RagResponder(api_key,)

answer = responder.generate_response(query, context)
print(answer) 