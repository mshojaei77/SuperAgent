import streamlit as st
from ChatWithWebsite import WebAssistantAgent

class Demo:
    def __init__(self):
        self.url = None
        if "messages" not in st.session_state:
            st.session_state.messages = []
        self.agent = None

    def sidebar(self):
        with st.sidebar:
            st.header('Web Assistant', divider='violet')
            self.url = st.text_input("Enter Website URL")
            if self.url:
                with st.spinner('Loading...'):
                    self.agent = WebAssistantAgent()

    def chat(self):
        user_input = st.chat_input("Talk with me")
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if user_input:
            with st.chat_message("user"):
                st.markdown(user_input)
            st.session_state.messages.append({"role": "user", "content": user_input})
            conversation_history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            if self.agent and self.url:
                with st.chat_message("assistant"):
                    with st.spinner('Wait for it...'):
                        answer = self.agent.execute(self.url, user_input)
                    response = st.write(answer)
                st.session_state.messages.append({"role": "assistant", "content": response})

    def run(self):
        self.sidebar()
        self.chat()

if __name__ == "__main__":
    app = Demo()
    app.run()