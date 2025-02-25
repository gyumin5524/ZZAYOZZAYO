# 🌍 ZZAYOZZAYO
## 프로젝트 개요
ZZAYOZZAYO는 원하는 날짜와 지역을 선택하고 정해진 선호도를 지정하여 원하는 여행을 도출해주는 챗봇입니다.

## 주요 기능  

✅ 맞춤형 날짜 지정 ✅ 사용자의 여행 지역 및 선호도 지정
✅ AI 기반 여행 일정 생성 ✅ 챗봇과 대화하여 일정표 짜기


## 와이어프레임
![Image](https://github.com/user-attachments/assets/933c8735-6525-463c-a01c-711ebb498c67)

## API 명세서
| table | API엔드포인트 | method | 설명 | 요청본문 | 응답본문 |
| --- | --- | --- | --- | --- | --- |
| api/v1/travel | `/api/user-data/` | `POST` | 사용자 정보 저장 | `{ "username": "홍길동", "email": "hong@example.com", "age": 25 }` | `{ "message": "사용자 정보 저장 성공!" }` |
|  | `/api/place-recommendations/` | `GET` | 여행지 추천 목록 조회 | 없음 | `{ "추천 여행지": ["경복궁", "남산타워", "홍대 거리"] }` |
|  | `/api/chatbot/` | `POST` | 사용자 입력을 받아 ChatGPT 응답 반환 | `{ "user_input": "오늘 날씨 어때?" }` | `{ "user_input": "오늘 날씨 어때?", "bot_response": "오늘 서울의 날씨는 맑고 따뜻합니다." }` |
 
## 파일별 역할

## 트러블슈팅

