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
```📦백엔드
 ┣ 📂travel                 # 메인 앱 (여행 및 챗봇 기능 구현)
 ┃ ┣ 📜crawled_data_models.py   # 네이버 API 크롤링 데이터 모델 정의
 ┃ ┣ 📜embedding.py             # 임베딩 모델 초기화 및 FAISS 인덱스 관리
 ┃ ┣ 📜langchain_llm.py         # LangChain과 GPT-4를 활용한 LLM 로직 구현
 ┃ ┣ 📜models.py                # Django 메인 모델 정의 (UserData, CrawledData 등)
 ┃ ┣ 📜rag.py                   # RAG (Retrieval-Augmented Generation) 관련 로직
 ┃ ┣ 📜serializers.py           # Django REST Framework 시리얼라이저 설정
 ┃ ┣ 📜services.py              # 비즈니스 로직을 처리하는 서비스 모음
 ┃ ┣ 📜urls.py                  # travel 앱의 URL 라우팅 설정
 ┃ ┣ 📜views.py                 # Django의 View 로직 (API 엔드포인트 처리)
 ┃ ┗ 📜__init__.py              # Python 패키지 인식용 파일
 ┣ 📂zzayochatbot           # Django 프로젝트 설정 폴더
 ┃ ┣ 📜asgi.py                 # ASGI 서버 설정 (비동기 지원)
 ┃ ┣ 📜settings.py             # Django 프로젝트의 설정 파일
 ┃ ┣ 📜urls.py                 # 전체 프로젝트의 URL 설정
 ┃ ┣ 📜wsgi.py                 # WSGI 서버 설정 (배포용)
 ┃ ┗ 📜__init__.py             # Python 패키지 인식용 파일
 ┣ 📜.env                      # 환경 변수 설정 파일 (API 키 등)
 ┣ 📜.gitignore                # Git에 포함하지 않을 파일/폴더 목록
 ┣ 📜app.py                    # 프로젝트 초기화 스크립트 (예: Streamlit 사용 시)
 ┣ 📜db.sqlite3                # SQLite 데이터베이스 파일 (로컬 개발용)
 ┣ 📜manage.py                 # Django 관리 명령어를 위한 진입점
 ┣ 📜README.md                 # 프로젝트 설명 및 사용법 문서
 ┗ 📜requirements.txt          # Python 패키지 의존성 목록
```
```📦프론트엔드
 ┗ 📂streamlit                 # Streamlit을 사용한 프론트엔드 애플리케이션 폴더
   ┣ 📜app.py                  # 프로토 타입 1
   ┣ 📜app2.py                 # 프로토 타입 2
   ┗ 📜streamlit.py            # 최종 완료 streamlit.py
```



## 트러블슈팅
### **📌**백엔드

- **db설계 대신 네이버 local API를 호출하는 방법을 선택하였습니다. 
그러나 호출시 키워드(ex. 제주도 산, 바다)를 기반으로 네이버 플레이스에 등록된 여행과 관련되지 않은 업체들(ex.산바다서바이벌) 또한 같이 호출되었기 때문에, 네이버 API를 호출하는 방법 대신 네이버 검색 데이터를 크롤링 하여 db에 저장하고, 그 데이터를 기반으로 RAG를 사용하는 방식으로 바꾸었습니다.**

### **📌**프론트엔드

- **1.버튼을 두번 눌러야 작동되는 오류가 있습니다.**

## 팀원
###김민채
###김요한
###이현수
###조규민
