import logging
import os
from openai import OpenAI
logging.basicConfig(level=logging.WARNING)

class RagResponder:

    def __init__(self, api_key=os.getenv('OPENAI_API_KEY'), model='gpt-3.5-turbo'):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate_response(self, query, context=None, system_prompt=None, conversation_history=[]):
        try:
            if context:
                prompt = f'''
                answer the query using the provided contexts :\n
                #query: `{query}`\n
                ## Contexts:\n
                ```html\n{context}\n```
                '''
            else:
                prompt = query
                
            if system_prompt:
                conversation_history.append({"role": "system", "content": system_prompt})
                
            conversation_history.append({"role": "user", "content": prompt})
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages= conversation_history)
            
            answer = completion.choices[0].message.content
            
            return answer

        except Exception as e:
            logging.warning(f'An error occurred while processing the query: {e}')
            return None, []

# Usage
if __name__ == "__main__":
    api_key=os.getenv('OPENAI_API_KEY')
    model='gpt-3.5-turbo'
    
    query = 'explain context'
    
    context = open("sample_context.txt", "r",encoding='utf-5').read()
    system_prompt = open("dsm5_prompt.txt", "r",encoding='utf-5').read()
    
    responder = RagResponder(api_key,)
    
    answer = responder.generate_response(query,context,system_prompt)
    print(answer) 