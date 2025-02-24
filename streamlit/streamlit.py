import streamlit as st
import requests

# BASE_URL: Django 서버 주소
BASE_URL = "http://127.0.0.1:8000/travel"

st.title("짜요짜요 여행 플래너 🗺️")

# 추천 키워드 생성 함수
def generate_recommendation_query(destination, preference):
    if destination and preference:
        return f"{destination} {preference}"
    elif destination:
        return f"{destination}"
    else:
        return "여행지 추천"

# 세션 상태 초기화
if "user_data" not in st.session_state:
    st.session_state["user_data"] = None    # 여행 정보 저장
if "recommendations" not in st.session_state:
    st.session_state["recommendations"] = []  # 추천 여행지 목록 저장
if "messages" not in st.session_state:
    st.session_state["messages"] = []         # 챗봇 대화 내역 저장

# ★ 여행 정보 입력 섹션 ★
st.header("📌 여행 정보 입력")
start_date = st.date_input("여행 시작 날짜")
end_date = st.date_input("여행 종료 날짜")
destination = st.text_input("여행 목적지")
preference = st.radio("여행 스타일 및 선호도 (예: 맛집, 핫플 등)",
                      ['맛집', '핫플', '자연경관', '힐링', '액티비티', '드라이브', '전시회'])

# 날짜 예외 처리: 종료 날짜가 시작 날짜보다 이전이면 오류 메시지 출력
if end_date < start_date:
    st.error("여행 종료 날짜는 여행 시작 날짜보다 이전일 수 없습니다.")

if st.button("여행 정보 저장"):
    # 저장 전에 날짜 오류가 있을 경우 저장하지 않음
    if end_date < start_date:
        st.error("여행 정보 저장 실패: 종료 날짜가 시작 날짜보다 이전입니다.")
    else:
        user_data = {
            "start_date": str(start_date),
            "end_date": str(end_date),
            "destination": destination,
            "preference": preference
        }
        try:
            response = requests.post(f"{BASE_URL}/user-data/", json=user_data)
            response.raise_for_status()
            st.session_state["user_data"] = user_data
            st.success("✅ 여행 정보가 저장되었습니다!")
        except requests.exceptions.RequestException as e:
            st.error(f"❌ API 실패: {str(e)}")
            # fallback: Django 서버 연결 실패 시에도 임시로 저장
            st.session_state["user_data"] = user_data
            st.info("※ Django 서버 연결 실패로 인해, 여행 정보를 임시로 저장합니다.")

# ★ 여행지 추천 섹션 ★
st.header("🏝️ 여행지 추천 받기")
default_query = generate_recommendation_query(destination, preference) if st.session_state["user_data"] else "국내 여행지 추천"
query = st.text_input("여행지 추천 키워드", default_query)

# 추천 여행지 개수 슬라이더 제거 – 기본값 5 사용
default_display_count = 5

if st.button("여행지 추천 요청"):
    payload = {
        'user_input': query,
        'display_count': default_display_count
    }
    try:
        response = requests.post(f"{BASE_URL}/place-recommend/", json=payload)
        response.raise_for_status()
        recommendations = response.json().get("추천 여행지", [])
        st.session_state["recommendations"] = recommendations
        st.write("📍 추천 여행지:")
        if recommendations:
            for idx, place in enumerate(recommendations, 1):
                st.write(f"{idx}. {place}")
        else:
            st.warning('추천 여행지를 찾을 수 없습니다.')
    except requests.exceptions.RequestException as e:
        st.error(f"❌ 추천 실패: {str(e)}")
        st.session_state["recommendations"] = []
        st.info("※ Django 서버 연결 실패로 인해, 추천 여행지 목록이 비어있습니다.")
        
# ★ 사이드바에 추천 여행지 목록 지속 표시 ★
if st.session_state['recommendations']:
    st.sidebar.subheader(f'🏝️ 여행지 추천 키워드:\n{default_query}')
    st.sidebar.subheader('📍 추천 여행지 목록')
    for idx, place in enumerate(st.session_state['recommendations'], 1):
        st.sidebar.write(f'{idx}. {place}')

# ★ 챗봇과 대화 섹션 ★
st.header("💬 챗봇과 대화하기")

if st.session_state["messages"]:
    st.subheader("대화 내역")
    for message in st.session_state["messages"]:
        if message["role"] == "user":
            st.write(f"🙋 사용자: {message['content']}")
        elif message["role"] == "bot":
            st.write(f"🤖 챗봇: {message['content']}")

def send_message():
    user_message = st.session_state.new_message
    if not user_message:
        st.warning("🚨 메시지를 입력해 주세요.")
        return

    st.session_state["messages"].append({"role": "user", "content": user_message})
    
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

st.text_input("메시지 입력", key="new_message", on_change=send_message)
