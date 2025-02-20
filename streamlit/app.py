import streamlit as st
import requests

# Django 서버 주소
BASE_URL = "http://127.0.0.1:8000/travel"

# Streamlit 페이지 설정
st.set_page_config(page_title="짜요짜요 여행 챗봇", page_icon="🤖")
st.title("💬 짜요짜요 여행 플래너 챗봇 🗺️")

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state["messages"] = []  # 채팅 기록 저장

if "user_data" not in st.session_state or not isinstance(st.session_state["user_data"], dict):
    st.session_state["user_data"] = {
        "start_date": "날짜 없음",
        "end_date": "날짜 없음",
        "destination": "미정",
        "preference": "없음"
    }

# 이전 대화 불러오기
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 데이터 저장 API 요청 (예외 처리 추가)
if st.button("여행 정보 저장"):
    user_data = st.session_state["user_data"]
    
    try:
        response = requests.post(f"{BASE_URL}/user-data/", json=user_data)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 처리
        st.success("✅ 여행 정보가 저장되었습니다!")
    except requests.exceptions.RequestException as e:
        st.error(f"❌ API 요청 실패: {str(e)}")

# 여행지 추천 API 요청 (예외 처리 추가)
st.header("🏝️ 여행지 추천 받기")
query = st.text_input("여행지 추천 키워드", st.session_state["user_data"]["destination"])
display_count = st.slider("추천 여행지 개수", 1, 10, 5)

if st.button("여행지 추천 요청"):
    user_data = {
        'user_input': query,
        'display_count': display_count
    }

    try:
        response = requests.post(f"{BASE_URL}/place-recommend/", data=user_data)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 처리
        recommendations = response.json().get("추천 여행지", [])
        
        st.write("📍 추천 여행지:")
        if recommendations:
            for idx, place in enumerate(recommendations, 1):
                st.write(f"{idx}. {place}")
        else:
            st.warning('추천 여행지를 찾을 수 없습니다.')
    except requests.exceptions.RequestException as e:
        st.error(f"❌ API 요청 실패: {str(e)}")

# 챗봇 대화 API 요청 (예외 처리 추가)
st.header("💬 챗봇과 대화하기")
user_input = st.chat_input("질문 입력")

if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        response = requests.post(f"{BASE_URL}/chatbot-response/", json={"user_data": st.session_state["user_data"], "user_input": user_input})
        response.raise_for_status()  # HTTP 오류 발생 시 예외 처리
        bot_reply = response.json().get("bot_response", "응답 없음")

        with st.chat_message("assistant"):
            st.markdown(bot_reply)

        st.session_state["messages"].append({"role": "assistant", "content": bot_reply})
    except requests.exceptions.RequestException as e:
        st.error(f"❌ 챗봇 오류: {str(e)}")
