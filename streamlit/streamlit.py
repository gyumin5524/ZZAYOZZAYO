import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:8000/travel"  # Django 서버 주소

st.title("짜요짜요 여행 플래너 🗺️")

# 추천 키워드 생성 함수
def generate_recommendation_query(destination, preference):
    if destination and preference:
        return f"{destination} {preference} 추천 여행지"
    elif destination:
        return f"{destination} 추천 여행지"
    else:
        return "국내 여행지 추천"

# 세션 상태 초기화
if "returns" not in st.session_state:
    st.session_state["returns"] = "국내 여행지 추천"  # 기본 키워드
if "user_data" not in st.session_state:
    st.session_state["user_data"] = None  # 사용자 데이터를 저장할 공간

# 사용자 데이터 입력
st.header("📌 여행 정보 입력")
start_date = st.date_input("여행 시작 날짜")
end_date = st.date_input("여행 종료 날짜")
destination = st.text_input("여행 목적지")
preference = st.text_area("여행 스타일 및 선호도")

if st.button("여행 정보 저장"):
    user_data = {
        "start_date": str(start_date),
        "end_date": str(end_date),
        "destination": destination,
        "preference": preference
    }
    
    response = requests.post(f"{BASE_URL}/user-data/", json=user_data)
    
    if response.status_code == 201:
        st.session_state["user_data"] = user_data  # 세션 상태에 저장
        st.session_state["returns"] = generate_recommendation_query(destination, preference)
        st.success("✅ 여행 정보가 저장되었습니다!")
    else:
        st.error(f"❌ 저장 실패: {response.json()}")

# 여행지 추천 요청
st.header("🏝️ 여행지 추천 받기")
query = st.text_input("여행지 추천 키워드", st.session_state["returns"])
display_count = st.slider("추천 여행지 개수", 1, 10, 5)

if st.button("여행지 추천 요청"):
    user_data = {
        'user_input' : query,
        'display_count' : display_count
    }
    print(f"📝 사용자가 입력한 검색어: {query}")
    
    response = requests.post(f"{BASE_URL}/place-recommend/", data=user_data)
        
    if response.status_code == 200:
        recommendations = response.json().get("추천 여행지", [])
        st.write("📍 추천 여행지:")
        if recommendations:
            for idx, place in enumerate(recommendations, 1):
                st.write(f"{idx}. {place}")
        else:
            st.warning('추천 여행지를 찾을 수 없습니다.')
    else:
        st.error(f"❌ 추천 실패: {response.json()}")

# 챗봇과 대화
st.header("💬 챗봇과 대화하기")
user_input = st.text_input("질문 입력")
user_data = st.session_state['user_data']

if st.button("챗봇 응답 요청"):
    response = requests.post(f"{BASE_URL}/chatbot-response/", json={"user_data": user_data, "user_input": user_input})
    
    if response.status_code == 200:
        print(response.json())
        st.write(f"🤖 챗봇: {response.json().get('bot_response', '응답 없음')}")
    else:
        st.error(f"❌ 챗봇 오류: {response.json()}")