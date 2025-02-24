import requests
import openai
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from django.conf import settings
from openai import OpenAIError

# LangChain 관련 모듈 임포트
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# OpenAI API 키 전역 설정
openai.api_key = settings.OPENAI_API_KEY

# 네이버 API 키는 settings에서 가져옴
NAVER_CLIENT_ID = settings.NAVER_CLIENT_ID
NAVER_CLIENT_SECRET = settings.NAVER_CLIENT_SECRET

# 임베딩 모델 초기화 (BERT 기반 SentenceTransformer)
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
embedding_dim = embedding_model.get_sentence_embedding_dimension()

# FAISS 인덱스 생성 (메모리 내 인덱스, 실제 서비스에서는 디스크 저장 고려)
faiss_index = faiss.IndexFlatL2(embedding_dim)
# 문서(텍스트) 저장 리스트 (인덱스와 매핑)
document_texts = []

def crawl_naver_api(query, display_count=5):
    """
    네이버 API를 호출하여 여행 관련 데이터를 크롤링하는 함수.
    반환: 각 문서(텍스트)의 리스트.
    """
    url = 'https://openapi.naver.com/v1/search/local.json'
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {'query': query, 'display': display_count}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        docs = []
        for item in data.get('items', []):
            # 크롤링 시 제목과 설명을 결합하여 하나의 문서로 구성
            text = item.get('title', '') + " " + item.get('description', '')
            # HTML 태그 제거 (간단하게)
            text = text.replace('<b>', '').replace('</b>', '')
            docs.append(text.strip())
        return docs
    else:
        return []

def build_faiss_index(docs):
    """
    주어진 문서 목록을 임베딩하고, FAISS 인덱스를 구축합니다.
    """
    global faiss_index, document_texts
    if docs:
        embeddings = embedding_model.encode(docs, convert_to_numpy=True)
        # FAISS 인덱스 초기화 (reset)
        faiss_index.reset()
        faiss_index.add(embeddings)
        document_texts = docs
    return faiss_index

def search_faiss_index(query, top_k=3):
    """
    FAISS 인덱스를 이용하여 쿼리에 가장 유사한 문서들을 검색합니다.
    """
    query_embedding = embedding_model.encode([query], convert_to_numpy=True)
    distances, indices = faiss_index.search(query_embedding, top_k)
    results = []
    for idx in indices[0]:
        if idx < len(document_texts):
            results.append(document_texts[idx])
    return results

def generate_response(user_query, retrieved_context):
    """
    LangChain의 LLMChain을 사용하여 사용자 질문에 대한 답변을 생성하는 함수.
    """
    prompt_template = PromptTemplate(
        input_variables=["retrieved_context", "user_query"],
        template=(
            "다음 참고 자료를 바탕으로 사용자의 질문에 대해 답변해 주세요:\n"
            "참고 자료:\n{retrieved_context}\n\n"
            "사용자 질문: {user_query}\n\n"
            "답변:"
        )
    )
    chat_model = ChatOpenAI(model_name='gpt-4', temperature=0)
    chain = LLMChain(llm=chat_model, prompt=prompt_template)
    result = chain.run({
        "retrieved_context": retrieved_context,
        "user_query": user_query
    })
    return result

def retrieve_travel_context(query, display_count=3):
    """
    OpenAI API를 사용하여 여행 일정 가이드 관련 간결한 참고 자료(텍스트)를 생성합니다.
    """
    prompt = (
        f"'{query}'에 대한 여행 일정을 계획하기 위한 간결한 여행 컨텍스트와 가이던스를 제공해 주세요. "
        "답변은 짧은 문단 형식으로 작성해 주세요."
    )
    try:
        response = openai.ChatCompletion.create(
            model='gpt-4o-mini',
            messages=[
                {"role": "system", "content": "당신은 동선 및 시간 효율까지 고려하는 경력 20년차의 섬세한 베테랑 여행 가이드입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        context_text = response['choices'][0]['message']['content'].strip()
        return context_text
    except Exception as e:
        return f"오류 발생: {str(e)}"

def build_retrieval_context(user_data, user_query):
    """
    RAG를 위한 검색 쿼리를 생성하고, FAISS 인덱스를 통해 관련 문서를 검색하여
    하나의 텍스트(참고 자료)로 구성합니다.
    """
    # 예를 들어, 사용자 목적지와 관련된 정보를 검색 쿼리로 사용
    retrieval_query = f"{user_data['destination']} 여행 정보"
    # 크롤링을 통해 문서를 수집
    crawled_docs = crawl_naver_api(retrieval_query, display_count=5)
    if crawled_docs:
        build_faiss_index(crawled_docs)
        top_docs = search_faiss_index(user_query, top_k=3)
        context = "\n".join(top_docs)
        return context
    else:
        return "관련 정보가 없습니다."

class ChatbotService:
    @staticmethod
    def get_chatgpt_response(user_input, user_data):
        """
        LangChain의 LLMChain을 사용하여 사용자의 요청에 맞는 답변(여행 일정 또는 일반 질문 응답)을 생성합니다.
        
        동작 원리:
        1. RAG: 사용자 목적지 기반으로 관련 참고 자료(여행 컨텍스트)를 구축합니다.
           - 크롤링 → 임베딩(FAISS) → 검색을 통해 retrieval_context를 구성합니다.
        2. retrieval_context와 사용자 질문을 LangChain 체인에 전달하여 최종 답변 생성.
        """
        try:
            response = client.chat.completions.create(model = 'gpt-4',
            messages = [{'role' : 'system', 'content' : '당신은 경력 20년차 베테랑 여행 가이드입니다. '
                '사용자가 요청하면 JSON 형식으로 상세한 여행 일정을 반환합니다. '
                '일정은 하루를 오전, 점심, 오후, 저녁 순으로 나누고 각 활동에 대해 상세한 설명을 추가하세요. '
                '사용자가 요청한 여행에 맞게 여행 일정을 계획해주세요. 예를 들어 "서울 2일 여행 일정"이라면 서울에 맞는 여행 일정을 제공해 주세요. '
                f'사용자가 요청한 여행: '
                f'시작 날짜: {user_data.get["start_date"]}, '
                f'종료 날짜: {user_data["end_date"]}, '
                f'목적지: {user_data.get["destination"]}, '
                f'여행 선호도: {user_data["preference"]}'},
                        {'role' : 'user', 'content' : user_input}],
            temperature = 0.7)
            raw_schedule = response.choices[0].message.content.strip()

            # try:
            #     schedule = json.loads(raw_schedule)
            # except json.JSONDecodeError:
            #     return {'error' : '일정 추천 결과를 처리하는 중 오류가 발생했습니다. 다시 시도해 주세요.', 'raw_response' : raw_schedule}

            # adjusted_schedule = adjust_travel_schedule(schedule)
            # return {'schedule' : raw_schedule}
            return raw_schedule

        except OpenAIError as oe:
            return {'error': f'OpenAI API 호출 오류: {str(oe)}'}
        except Exception as e:
            return f'오류 발생: {str(e)}'
