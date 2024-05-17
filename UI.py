import streamlit as st
from ChatWithWebsite import WebAssistantAgent

from openai import OpenAI
import streamlit as st

agent = WebAssistantAgent()

with st.sidebar:
    st.header('Web Assistant', divider='violet')
    url = st.text_input("Enter Website URL")

if "messages" not in st.session_state:
    st.session_state.messages = []
user_input = st.chat_input("Talk with me")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    conversation_history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
    with st.chat_message("assistant"):
        answer = agent.execute(url, user_input)
        response = st.write(answer)
    st.session_state.messages.append({"role": "assistant", "content": response})