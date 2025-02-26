from langchain_openai import OpenAI
from langchain.schema import HumanMessage
from langchain.chat_models import ChatOpenAI
from .rag import search_similar_documents  # (코사인 유사도 버전) 또는 search_similar_document_faiss
from django.conf import settings
import json

def generate_response(query_embedding, user_input, user_data):
    """
    (6) LangChain을 이용해 LLM을 연결하고, RAG를 통해 검색된 문서를 기반으로 답변 생성
    """
    # 유사한 문서 검색
    # 쿼리 안에 유저 데이터, 유저 인풋 분리하기
    similar_doc = search_similar_documents(query_embedding)
    print(similar_doc)
    if not similar_doc:
        return "검색된 문서가 없습니다."

    # 검색된 문서의 내용
    doc_address = similar_doc.address

    # 실제로 사용할 LangChain LLM (PDF 예시 기준)
    llm = ChatOpenAI(model="gpt-4", api_key=settings.OPENAI_API_KEY)  # 예시

    # 사용자 질문과 관련 문서를 이용하여 프롬프트 생성
    start_date = user_data.get('start_date')  # 시작 날짜
    end_date = user_data.get('end_date')    # 종료 날짜
    destination = user_data.get('destination') # 목적지
    preference = user_data.get('preference')

    prompt = f"""
            당신은 동선 및 시간 효율까지 고려하는 경력 20년차의 섬세한 베테랑 여행 가이드입니다. 
            응답은 사용자가 요청하지 않는 이상 기본 언어는 한국어로 응답하세요.
            여행과 관련되지 않은 질문에는 '여행과 관련되지 않은 질문에는 응답할 수 없습니다.' 라고 대답하세요.
            내국인 관광객 기준으로 여행 일정을 작성하여 응답해주세요.
            아래의 참고 자료를 바탕으로 사용자가 요청한 여행 일정표를 작성해 주세요. 
            일정은 하루를 오전, 점심, 오후, 저녁 순으로 나누고, 맛집 추천도 일정에 포함해야 하며, 각 활동에 대해 상세한 설명을 포함해야 합니다.

            참고 자료:
            {doc_address}

            사용자 여행 정보:
            시작 날짜: {start_date}
            종료 날짜: {end_date}
            목적지: {destination}
            여행 선호도: {preference}

            사용자 요청:
            {user_input}
            """

    # LLM 호출
    response = llm([HumanMessage(content=prompt)])
    print(response.content)
    # response는 통상 {'text': '...'} 형태이거나, ChatOpenAI 객체 구조에 따라 변동
    # langchain==0.0.100 이후 ChatOpenAI는 보통 AIMessage를 반환
    return response.content
