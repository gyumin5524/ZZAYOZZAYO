import random
import requests
import json
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from django.conf import settings
from openai import OpenAI, OpenAIError
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

client = OpenAI(api_key=settings.OPENAI_API_KEY)

# ✅ OpenAI API 및 네이버 API 설정
NAVER_CLIENT_ID = settings.NAVER_CLIENT_ID
NAVER_CLIENT_SECRET = settings.NAVER_CLIENT_SECRET

# ✅ 임베딩 모델 초기화 (BERT 기반 SentenceTransformer)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
embedding_dim = embedding_model.get_sentence_embedding_dimension()

# ✅ FAISS 인덱스 생성
faiss_index = faiss.IndexFlatL2(embedding_dim)
document_texts = []  # 문서 원본 저장


# ------------------------------------------------------------------------------
# ✅ 1. 네이버 API 여행지 추천 (get_travel_recommendations)
# ------------------------------------------------------------------------------
def get_travel_recommendations(keyword, display_count=5):
    """
    네이버 API를 사용하여 여행지 추천 목록을 가져오는 함수.
    """
    url = "https://openapi.naver.com/v1/search/local.json"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    }
    params = {"query": keyword, "display": display_count}
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        try:
            data = response.json()
            travel_spots = [item["title"].replace("<b>", "").replace("</b>", "") for item in data["items"]]
            print(data)
            return "\n".join(travel_spots) if travel_spots else "네이버 API에서 여행지 데이터를 찾을 수 없습니다."
        except json.JSONDecodeError:
            return "API 응답을 처리하는 중 오류가 발생했습니다."
    else:
        return f"네이버 API 오류 발생 (상태 코드: {response.status_code})"


# ------------------------------------------------------------------------------
# ✅ 2. 네이버 API 크롤링 데이터 수집 (fetch_data_from_naver, crawl_naver_api)
# ------------------------------------------------------------------------------
def fetch_data_from_naver(query="여행", display_count=50):
    from .models import CrawledData
    """
    네이버 API를 호출하여 여행 관련 데이터를 가져오는 함수.
    """
    url = "https://openapi.naver.com/v1/search/local.json"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    }
    params = {"query": query, "display": display_count}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        for item in data['items']:  # API 응답 형식에 맞게 데이터 처리
            title = item['title'].replace("<b>", "").replace("</b>", "").replace("&amp;", "")
            content = item['description'].replace("<b>", "").replace("</b>", "").replace("&amp;", "")
            url = item['link']

            # 네이버 크롤링 데이터를 데이터베이스에 저장
            crawled_data = CrawledData.objects.create(
                title=title,
                content=content,
                url=url,
                embedding=None  # 임베딩은 나중에 처리
            )


def crawl_naver_api(query, display_count=50):
    """
    네이버 API를 사용하여 여행 관련 데이터를 크롤링하는 함수.
    """
    url = "https://openapi.naver.com/v1/search/local.json"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    }
    params = {"query": query, "display": display_count}
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        try:
            data = response.json()
            docs = []
            for item in data.get("items", []):
                text = item.get("title", "") + " " + item.get("description", "")
                text = text.replace("<b>", "").replace("</b>", "")
                docs.append(text.strip())
            return docs
        except json.JSONDecodeError:
            return []
    else:
        return []


# ------------------------------------------------------------------------------
# ✅ 3. FAISS 인덱스 구축 및 검색
# ------------------------------------------------------------------------------
def build_faiss_index(docs):
    """
    크롤링한 문서를 임베딩하고, FAISS 인덱스를 구축합니다.
    """
    global faiss_index, document_texts
    if docs:
        embeddings = embedding_model.encode(docs, convert_to_numpy=True)
        faiss_index.reset()
        faiss_index.add(embeddings)
        document_texts = docs
    return faiss_index


def search_faiss_index(query, top_k=3):
    """
    FAISS 인덱스를 이용하여 쿼리에 가장 유사한 문서 검색.
    """
    query_embedding = embedding_model.encode([query], convert_to_numpy=True)
    distances, indices = faiss_index.search(query_embedding, top_k)
    results = [document_texts[idx] for idx in indices[0] if idx < len(document_texts)]
    return results


# ------------------------------------------------------------------------------
# ✅ 4. RAG 기반 여행 컨텍스트 검색
# ------------------------------------------------------------------------------
def retrieve_travel_context(query, display_count=3):
    """
    OpenAI API를 사용하여 여행 일정 관련 참고 자료를 생성하는 함수.
    """
    prompt = (
        f"'{query}'에 대한 여행 일정을 계획하기 위한 간결한 여행 컨텍스트와 가이드를 제공해 주세요. "
        "답변은 짧은 문단 형식으로 작성해 주세요."
    )
    
    docs = crawl_naver_api(query=query, display_count=display_count)
    
    if docs:
        build_faiss_index(docs)
        top_docs = search_faiss_index(query, top_k=5)
        print(top_docs)
        return top_docs  # 🔹 개행으로 문장 구분
    else:
        return "관련 정보가 없습니다."


# ------------------------------------------------------------------------------
# ✅ 5. LangChain LLM을 이용한 챗봇 응답 생성
# ------------------------------------------------------------------------------
def generate_response(user_data, user_input):
    """
    LangChain의 LLMChain을 사용하여 사용자 질문에 대한 답변을 생성하는 함수.
    """
    retrieved_context = retrieve_travel_context(user_input)

    prompt_template = PromptTemplate(
        input_variables=["retrieved_context", "user_input", "user_data"],
        template="📌 참고 자료:\n{retrieved_context}\n\n"
                 "❓ 사용자 질문:\n{user_input}\n\n"
                 "✏️ 답변:"
    )

    chat_model = OpenAI(model="gpt-4", temperature=0)
    
    chain = LLMChain(llm=chat_model, prompt=prompt_template)

    response = chain.invoke({
        "retrieved_context": retrieved_context,
        "user_input": user_input,
        "user_data": user_data,
    })
    print(response)

    return response.replace("\n", " ")  # 🔹 개행 없이 문장 유지


# ------------------------------------------------------------------------------
# ✅ 6. ChatbotService (LangChain + RAG 기반 응답 생성)
# ------------------------------------------------------------------------------
class ChatbotService:
    @staticmethod
    def get_chatgpt_response(user_input, user_data):
        try:
            return generate_response(user_data, user_input)
        except OpenAIError as oe:
            return {"error": f"OpenAI API 호출 오류: {str(oe)}"}
        except Exception as e:
            return f"오류 발생: {str(e)}"
