# import streamlit as st
# import time

# def get_llm_response(user_input):
#     time.sleep(1)
#     return f"LLM response to: {user_input}"

# st.title("TripTrek")

# if 'messages' not in st.session_state:
#     st.session_state.messages = []

# for message in st.session_state.messages:
#     st.chat_message(message['role']).markdown(message['content'])

# prompt = st.chat_input('Pass your prompt here')

# if prompt:
#     st.chat_message('user').markdown(prompt)
#     st.session_state.messages.append({'role': 'user', 'content': prompt})
#     response = get_llm_response(prompt)
#     st.chat_message('assistant').markdown(response)
#     st.session_state.messages.append({'role': 'assistant', 'content': response})

import streamlit as st
import time

def get_llm_response(user_input):
    time.sleep(1)
    return f"LLM response to: {user_input}"

def get_generic_response(user_input):
    time.sleep(1)
    return f"Generic response to: {user_input}"

st.title("TripTrek")

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'input_submitted' in st.session_state:
    user_input = st.session_state.user_input
    action = st.session_state.action

    st.session_state.messages.append({'role': 'user', 'content': user_input})

    if action == 'llm':
        response = get_llm_response(user_input)
    elif action == 'generic':
        response = get_generic_response(user_input)
    st.session_state.messages.append({'role': 'assistant', 'content': response})

    del st.session_state.input_submitted
    st.session_state.user_input = ''
    st.session_state.action = ''

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

with st.form(key='chat_form', clear_on_submit=True):
    user_input = st.text_input('Pass your prompt here')
    col1, col2 = st.columns(2)
    with col1:
        send_llm = st.form_submit_button('Send LLM Response')
    with col2:
        send_generic = st.form_submit_button('Send Generic Response')

    if (send_llm or send_generic) and user_input:
        st.session_state.user_input = user_input
        if send_llm:
            st.session_state.action = 'llm'
        elif send_generic:
            st.session_state.action = 'generic'
        st.session_state.input_submitted = True
