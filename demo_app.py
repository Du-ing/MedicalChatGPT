import streamlit as st
from streamlit_chat import message
from gpt_cli import model, tokenizer, question_to_answer


if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

if 'history' not in st.session_state:
    st.session_state['history'] = []

if 'user' not in st.session_state:
    st.session_state['user'] = ""


def generate_response(question, history):
    answer = question_to_answer(model, tokenizer, question, history)
    return answer


def end_click():
    st.session_state['past'] = []
    st.session_state['generated'] = []
    st.session_state['history'] = []
    st.session_state['user'] = ""


def chat_click():
    if st.session_state['user'] != "":
        chat_input = st.session_state['user']
        history = st.session_state['history']
        output = generate_response(chat_input, history)
        st.session_state['past'].insert(0, chat_input)
        st.session_state['generated'].insert(0, output)
        st.session_state['history'].append((chat_input, output))
        st.session_state['user'] = ""


st.sidebar.title("医疗GPT")
st.header("医疗GPT", divider="rainbow")

c1, c2, c3 = st.columns([6, 1, 1])
with c1:
    user_input = st.text_input("提问", placeholder="请输入要咨询的问题", key="user", label_visibility="collapsed")
with c2:
    chat_button = st.button("发送", on_click=chat_click, type="primary")
with c3:
    end_button = st.button("新聊天", on_click=end_click)

container = st.container(border=True)

if st.session_state['generated']:
    with container:
        for i in range(0, len(st.session_state['generated']), 1):
            message(st.session_state['past'][i], is_user=True)
            message(st.session_state['generated'][i], key=str(i))
