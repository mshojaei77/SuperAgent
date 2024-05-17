import os
from dotenv import load_dotenv
from langchain_openai.chat_models import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import PyPDFLoader

from Tools.PdfFileLoader import PDFLoader


load_dotenv()

# input args
#llm
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm_model = "gpt-3.5-turbo"
llm_temperature = "0.7"
llm_streaming=True
#embedding
embedding_model = 'text-embedding-ada-002'
embedding_chunk_size = 10000
#loader
file_name = "example.pdf"
pdf_loader = PDFLoader(file_name)
pages = pdf_loader.load_and_split()


#instances
model = ChatOpenAI(api_key=OPENAI_API_KEY, model=llm_model, temperature=llm_temperature,streaming=llm_streaming)
embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY,model=embedding_model,chunk_size=embedding_chunk_size)
parser = StrOutputParser()

#prompt template
context = "my name is mohammad"
question = "what is my name?"
prompt = f"""
Answer the question based on the context below. If you can't 
answer the question, reply "I don't know".

Context: {context}

Question: {question}
"""


#running
#chain =  model | parser 
#result = chain.invoke(prompt)
#print(result)
if __name__ == "__main__":
    path = input("enter the [df path]: ")
    user_input = input("ask anything? ")
    agent = PdfAssistantAgent()
    answer = agent.execute(path, user_input)
    print(answer)