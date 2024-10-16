import streamlit as st
import time

def get_llm_response(user_input):
    time.sleep(1)
    return f"LLM response to: {user_input}"

st.title("TripTrek")

if 'messages' not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    st.chat_message(message['role']).markdown(message['content'])

prompt = st.chat_input('Pass your prompt here')

if prompt:
    st.chat_message('user').markdown(prompt)
    st.session_state.messages.append({'role': 'user', 'content': prompt})
    response = get_llm_response(prompt)
    st.chat_message('assistant').markdown(response)
    st.session_state.messages.append({'role': 'assistant', 'content': response})