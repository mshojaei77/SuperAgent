import os
from dotenv import load_dotenv
import openai
import groq
import together
import cohere
import g4f
import ollama

load_dotenv()

class LLM:
    def __init__(self, api_key=None, model=None, system_prompt="You are a helpful assistant", user_prompt=None):
        self.api_key = api_key
        self.model = model
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt

    def openai_llm(self):
        client = openai.OpenAI(api_key=self.api_key)
        completion = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": self.user_prompt}
            ]
        )
        return completion.choices[0].message.content

    def groq_llm(self):
        client = groq.Groq(api_key=self.api_key)
        completion = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": self.user_prompt}
            ]
        )
        return completion.choices[0].message.content

    def deepseek_llm(self):
        client = openai.OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com/v1")
        completion = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": self.user_prompt},
            ]
        )
        return completion.choices[0].message.content

    def openrouter_llm(self):
        client = openai.OpenAI(base_url="https://openrouter.ai/api/v1",api_key=self.api_key)
        completion = client.chat.completions.create(
            model= self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": self.user_prompt},
            ]
        )
        return completion.choices[0].message.content

    def togetherai_llm(self):
        client = together.Together(api_key=self.api_key)
        completion = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": self.user_prompt},
            ]
        )
        return completion.choices[0].message.content

    def firworks_llm(self):
        client = openai.OpenAI(base_url = "https://api.fireworks.ai/inference/v1",api_key=self.api_key)
        completion = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": self.user_prompt},
            ]
        )
        return completion.choices[0].message.content

    def cohere_llm(self):
        co = cohere.Client(self.api_key)
        completion = co.generate(
            model=self.model,
            prompt=self.user_prompt,
        )
        return completion

    def g4f_llm(self):
        client = g4f.Client()
        completion = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": self.user_prompt},
            ]
        )
        return completion.choices[0].message.content

    def ollama_llm(self):
        completion = ollama.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": self.user_prompt},
            ]
        )
        return completion['message']['content']


#Example usage
if __name__ == "__main__":
    prompt = input("ask anything: ")
    llm = LLM(api_key=os.getenv("OPENAI_API_KEY"),system_prompt="You are a helpful assistant", model="gpt-3.5-turbo", user_prompt=prompt)
    answer = llm.openai_llm()
    print(llm)