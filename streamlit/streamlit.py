import streamlit as st
import requests
from datetime import datetime

# ✅ 세션 상태 초기화 (존재하지 않으면 초기값 설정)
if "user_data" not in st.session_state:
    st.session_state["user_data"] = {}
if "recommendations" not in st.session_state:
    st.session_state["recommendations"] = []
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "step" not in st.session_state:  # ✅ 'step' 초기화 추가
    st.session_state["step"] = 1

BASE_URL = "http://127.0.0.1:8000/travel"

st.set_page_config(page_title="짜요짜요 여행 플래너", page_icon="🌍")
st.title("짜요짜요 여행 플래너 🌍")

# ✅ 'step'이 초기화되지 않았던 문제 해결
if "step" not in st.session_state:
    st.session_state["step"] = 1


# 🏠 추천 여행지 업데이트 함수
def update_recommendations():
    """네이버 API에서 추천 여행지 가져오기"""
    query = st.session_state["user_data"].get("destination")  # 기본값 설정
    display_count = 5

    response = requests.post(f"{BASE_URL}/place-recommend/", json={"user_input": query, "display_count": display_count})
    
    if response.status_code == 200:
        recommendations = response.json().get("추천 여행지", [])
        st.session_state["recommendations"] = recommendations
        st.sidebar.subheader("📍 추천 여행지 목록")
        for idx, place in enumerate(st.session_state["recommendations"], 1):
            st.sidebar.write(f"{idx}. {place}")
    else:
        st.sidebar.write("🚨 여행지 추천을 가져오지 못했습니다.")

# # 🏠 Streamlit 사이드바에서 추천 여행지 목록 표시
# if "recommendations" in st.session_state and st.session_state["recommendations"]:
#     st.sidebar.subheader("📍 추천 여행지 목록")
#     for idx, place in enumerate(st.session_state["recommendations"], 1):
#         st.sidebar.write(f"{idx}. {place}")
# else:
#     st.sidebar.write("🚨 추천 여행지가 없습니다.")

# 🏠 여행 계획이 저장되었을 때 추천 여행지를 자동 업데이트
# if st.session_state["step"] == 5:
#     update_recommendations()

# 🗨️ 대화 메시지 표시 함수
def display_messages():
    for message in st.session_state["messages"]:
        formatted_message = message['content'].replace("\n", "<br>")
        if message["role"] == "user":
            st.markdown(
                f"<div style='text-align: left; background-color: #DCF8C6; padding: 10px; border-radius: 10px; margin: 5px 50px 5px 0;'>👤 {formatted_message}</div>",
                unsafe_allow_html=True,
            )
        elif message["role"] == "bot":
            st.markdown(
                f"<div style='text-align: right; background-color: #E6E6E6; padding: 10px; border-radius: 10px; margin: 5px 0 5px 50px;'>🤖 {formatted_message}</div>",
                unsafe_allow_html=True,
            )

# 🏁 1단계: 여행 시작 날짜 입력
if st.session_state["step"] == 1:
    st.header("📅 여행 시작 날짜를 선택해 주세요.")
    start_date = st.date_input("여행 시작 날짜", key="start_date")
    if st.button("시작 날짜 저장") and start_date:
        st.session_state["user_data"]["start_date"] = str(start_date)
        st.session_state["step"] = 2

# 🏁 2단계: 여행 종료 날짜 입력
if st.session_state["step"] == 2:
    st.header("📅 여행 종료 날짜를 선택해 주세요.")
    end_date = st.date_input("여행 종료 날짜", key="end_date")
    if st.button("종료 날짜 저장") and end_date:
        start_date = datetime.strptime(st.session_state["user_data"]["start_date"], "%Y-%m-%d").date()
        if end_date < start_date:
            st.error("⛔ 여행 종료 날짜는 시작 날짜보다 이전일 수 없습니다.")
        else:
            st.session_state["user_data"]["end_date"] = str(end_date)
            st.session_state["step"] = 3

# 🏁 3단계: 여행 목적지 입력
if st.session_state["step"] == 3:
    st.header("📍 여행 목적지를 입력해 주세요.")
    destination = st.text_input("여행 목적지 입력", key="destination")
    if st.button("목적지 저장") and destination:
        st.session_state["user_data"]["destination"] = destination
        st.session_state["step"] = 4

# 🏁 4단계: 여행 스타일 및 선호도 입력
if st.session_state["step"] == 4:
    st.header("🎯 여행 스타일 및 선호도를 선택해 주세요.")
    preference = st.radio("여행 스타일 및 선호도", ['맛집', '핫플', '자연', '힐링'])
    if st.button("선호도 저장") and preference:
        st.session_state["user_data"]["preference"] = preference
        st.session_state["step"] = 5

# 🏁 5단계: 저장 완료
if st.session_state["step"] == 5:
    st.header("✅ 여행 정보가 저장되었습니다!")
    st.write("여행 기본설정을 모두 저장했습니다.")

# 🏠 추천 여행지 목록 표시
if st.session_state["recommendations"]:
    st.sidebar.subheader("📍 추천 여행지 목록")
    for idx, place in enumerate(st.session_state["recommendations"], 1):
        st.sidebar.write(f"{idx}. {place}")

# 🗨️ 챗봇과 대화하기
st.header("💬 챗봇과 대화하기")
if st.session_state["messages"]:
    st.subheader("대화 내역")

# 💬 메시지 전송 함수
def send_message(user_message):
    # user_message = st.session_state.new_message
    if not user_message:
        st.warning("🚨 메시지를 입력해 주세요.")
        return 
    print(user_message)
    st.session_state["messages"].append({"role": "user", "content": user_message})

    auto_message = (
        f"여행 계획: {st.session_state['user_data'].get('start_date')}부터 "
        f"{st.session_state['user_data'].get('end_date')}까지 "
        f"{st.session_state['user_data'].get('destination')}"
        f"{st.session_state['user_data'].get('preference')} 컨셉으로 예정되어 있습니다."
    )
    st.session_state["messages"].append({"role": "bot", "content": auto_message})

    payload = {
    "query": {
        "user_data": st.session_state.get("user_data", {}),
        "recommended_places": st.session_state.get("recommendations", []),
        "user_input": user_message
    }
}

    print(f"📌 전송 데이터: {payload}")
    print(f"📌 전송 데이터: {st.session_state["messages"]}")

    try:
        response = requests.post(f"{BASE_URL}/chatbot/", json=payload)
        response.raise_for_status()
        bot_response = response.json().get("response", "응답 없음")
        st.session_state["messages"].append({"role": "bot", "content": bot_response})

    except requests.exceptions.RequestException as e:
        st.error(f"❌ 챗봇 오류: {str(e)}")
        st.session_state["messages"].append({"role": "bot", "content": "죄송합니다. 챗봇 응답을 가져오지 못했습니다."})

    # st.session_state["new_message"] = ""

# 💬 메시지 입력
message_input = st.text_input("메시지 입력", placeholder="예: 일정짜줘")

if st.button("메세지 전송"):
    send_message(message_input)
    

# 🏠 초기 화면으로 돌아가기 버튼
if st.button("🏠 초기 화면으로 돌아가기"):
    st.session_state.clear()
    st.session_state["step"] = 1
    
    
# 🗨️ 대화 메시지 표시
display_messages()
