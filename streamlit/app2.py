import streamlit as st
import openai
import os
from dotenv import load_dotenv

# .env 파일 불러오기
load_dotenv()

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="AI 챗봇", page_icon="🤖")
st.title("💬 ZZAYOZZAYO")

# 채팅 기록 저장
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# 이전 대화 불러오기
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 받기
user_input = st.chat_input("메시지를 입력하세요...")

if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("답변을 생성 중..."):
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=st.session_state["messages"]
            )
            assistant_reply = response.choices[0].message.content
            st.markdown(assistant_reply)

    st.session_state["messages"].append({"role": "assistant", "content": assistant_reply})
