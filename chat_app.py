import streamlit as st
from gpt_cli import *


if "past" not in st.session_state:
    st.session_state["past"] = []

if "generated" not in st.session_state:
    st.session_state["generated"] = []

if "history" not in st.session_state:
    st.session_state["history"] = []


def end_click():
    st.session_state["past"] = []
    st.session_state["generated"] = []
    st.session_state["history"] = []
    # st.session_state["user"] = ""


def chat_click():
    if st.session_state["user"] != "":
        question = st.session_state["user"]
        history = st.session_state["history"]

        sep = tokenizer.convert_ids_to_tokens(tokenizer.eos_token_id)

        gpt_model = model.eval()

        gen_kwargs = {"max_new_tokens": 1024,
                      "do_sample": True,
                      "top_p": 0.7,
                      "temperature": 0.3,
                      "repetition_penalty": 1.1}

        prompt = generate_prompt(question, history)
        inputs = tokenizer([prompt], return_tensors="pt")
        inputs = inputs.to(gpt_model.device)

        streamer = TextIteratorStreamer(tokenizer, skip_prompt=True)
        generation_kwargs = dict(input_ids=inputs["input_ids"], streamer=streamer, **gen_kwargs)

        thread = Thread(target=gpt_model.generate, kwargs=generation_kwargs)
        thread.start()

        container = st.container(border=True)

        with container:
            for i in range(0, len(st.session_state["generated"]), 1):
                st.chat_message(name="user", avatar="./images/avatar/user.png").write(st.session_state["past"][i])
                st.chat_message(name="ai", avatar="./images/avatar/ai.png").write(st.session_state["generated"][i])

            user_message = st.chat_message(name="user", avatar="./images/avatar/user.png")
            gpt_message = st.chat_message(name="ai", avatar="./images/avatar/ai.png")

            user_message.write(question)

            with gpt_message:
                with st.spinner("思考中..."):
                    writer = st.empty()
                    generated_text = ""

                    for new_text in streamer:
                        if sep in new_text:
                            new_text = remove_overlap(generated_text, new_text[:-len(sep)])
                            for char in new_text:
                                generated_text += char
                                # print(char, end="", flush=True)
                                writer.write(generated_text)
                            break
                        for char in new_text:
                            generated_text += char
                            # print(char, end="", flush=True)
                            writer.write(generated_text)
            # print("\n", end="")

        st.button("清空", on_click=end_click, type="primary")

        st.session_state["past"].append(question)
        st.session_state["generated"].append(generated_text)
        st.session_state["history"].append((question, generated_text))


st.sidebar.header("医疗GPT", divider="rainbow")
st.chat_input(placeholder="请输入要咨询的问题", key="user", on_submit=chat_click)
