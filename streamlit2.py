import streamlit as st
import requests
from datetime import datetime, date

# OpenAPI 기반 Django 서버 주소
BASE_URL = "http://127.0.0.1:8000/travel"

st.set_page_config(page_title="짜요짜요 여행 플래너", page_icon="🗺️")

st.title("짜요짜요 여행 플래너 🗺️")

# 세션 상태 초기화
if "user_data" not in st.session_state:
    st.session_state["user_data"] = {}
if "recommendations" not in st.session_state:
    st.session_state["recommendations"] = []
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "step" not in st.session_state:
    st.session_state["step"] = 1

# 💬 대화 메시지 표시 함수
def display_messages():
    for message in st.session_state["messages"]:
        if message["role"] == "user":
            st.markdown(
                f"""
                <div style='text-align: left; background-color: #DCF8C6; padding: 10px; border-radius: 10px; margin: 5px 50px 5px 0;'>
                    🙋 {message['content']}
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif message["role"] == "bot":
            st.markdown(
                f"""
                <div style='text-align: right; background-color: #E6E6E6; padding: 10px; border-radius: 10px; margin: 5px 0 5px 50px;'>
                    🤖 {message['content']}
                </div>
                """,
                unsafe_allow_html=True,
            )

# 💬 대화 메시지 표시
display_messages()

# ★ 1단계: 여행 시작 날짜 입력 ★
if st.session_state["step"] == 1:
    st.header("📅 여행 시작 날짜를 선택해 주세요.")
    start_date = st.date_input("여행 시작 날짜", key="start_date")
    if st.button("시작 날짜 저장") and start_date:
        st.session_state["user_data"]["start_date"] = str(start_date)
        st.session_state["step"] = 2

# ★ 2단계: 여행 종료 날짜 입력 ★
if st.session_state["step"] == 2:
    st.header("📅 여행 종료 날짜를 선택해 주세요.")
    end_date = st.date_input("여행 종료 날짜", key="end_date")
    if st.button("종료 날짜 저장") and end_date:
        start_date = datetime.strptime(st.session_state["user_data"]["start_date"], "%Y-%m-%d").date()
        if end_date < start_date:
            st.error("🚫 여행 종료 날짜는 시작 날짜보다 이전일 수 없습니다.")
        else:
            st.session_state["user_data"]["end_date"] = str(end_date)
            st.session_state["step"] = 3

# ★ 3단계: 여행 목적지 입력 ★
if st.session_state["step"] == 3:
    st.header("📍 여행 목적지를 입력해 주세요.")
    destination = st.text_input("여행 목적지 입력", key="destination")
    if st.button("목적지 저장") and destination:
        st.session_state["user_data"]["destination"] = destination
        st.session_state["step"] = 4

# ★ 4단계: 여행 스타일 및 선호도 입력 ★
if st.session_state["step"] == 4:
    st.header("🎯 여행 스타일 및 선호도를 선택해 주세요.")
    preference = st.radio("여행 스타일 및 선호도 (예: 맛집, 핫플 등)",
                          ['맛집', '핫플', '자연경관', '힐링', '액티비티', '드라이브', '전시회'])
    if st.button("선호도 저장") and preference:
        st.session_state["user_data"]["preference"] = preference
        st.session_state["step"] = 5

# ★ 5단계: 저장 완료 및 초기화 버튼 표시 ★
if st.session_state["step"] == 5:
    st.header("✅ 여행 정보가 저장되었습니다!")
    st.write("여행 기본설정을 모두 저장했습니다. .")
    

# ★ 사이드바에 추천 여행지 목록 지속 표시 ★
if st.session_state['recommendations']:
    st.sidebar.subheader('📍 추천 여행지 목록')
    for idx, place in enumerate(st.session_state['recommendations'], 1):
        st.sidebar.write(f'{idx}. {place}')

# ★ 챗봇과 대화 섹션 ★
st.header("💬 챗봇과 대화하기")

if st.session_state["messages"]:
    st.subheader("대화 내역")
    

# 메시지 전송 함수
def send_message():
    user_message = st.session_state.new_message
    if not user_message:
        st.warning("🚨 메시지를 입력해 주세요.")
        return

    st.session_state["messages"].append({"role": "user", "content": user_message})
    # 저장된 여행 정보를 자동으로 대화에 활용하도록 함
    auto_message = f"저장된 여행 계획은 {st.session_state['user_data'].get('start_date')}부터 {st.session_state['user_data'].get('end_date')}까지 {st.session_state['user_data'].get('destination')}로 {st.session_state['user_data'].get('preference')} 컨셉으로 예정되어 있습니다."
    st.session_state["messages"].append({"role": "bot", "content": auto_message})

    payload = {
        "user_data": st.session_state["user_data"],
        "recommended_places": st.session_state["recommendations"],
        "user_input": user_message
    }
    try:
        response = requests.post(f"{BASE_URL}/chatbot-response/", json=payload)
        response.raise_for_status()
        bot_response = response.json().get("bot_response", "응답 없음")
        st.session_state["messages"].append({"role": "bot", "content": bot_response})
    except requests.exceptions.RequestException as e:
        st.error(f"❌ 챗봇 오류: {str(e)}")
        st.session_state["messages"].append({"role": "bot", "content": "죄송합니다. 챗봇 응답을 가져오지 못했습니다."})
    st.session_state.new_message = ""

st.text_input("메시지 입력", key="new_message", on_change=send_message, placeholder="예: 일정짜줘")
if st.button("🏠 초기 화면으로 돌아가기"):
        st.session_state.clear()
        st.session_state["step"] = 1