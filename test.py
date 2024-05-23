import openai
from dotenv import load_dotenv
load_dotenv()
from langchain_openai import OpenAIEmbeddings
embeddings = OpenAIEmbeddings()



client = openai.OpenAI()
completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "hi"}
            ]
        )
print(completion.choices[0].message.content)