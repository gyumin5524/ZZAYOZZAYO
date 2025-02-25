from langchain_openai import OpenAI
from langchain.schema import HumanMessage
from .rag import search_similar_documents  # (코사인 유사도 버전) 또는 search_similar_document_faiss

def generate_response(query_embedding, user_input):
    """
    (6) LangChain을 이용해 LLM을 연결하고, RAG를 통해 검색된 문서를 기반으로 답변 생성
    """
    # 유사한 문서 검색
    # 쿼리 안에 유저 데이터, 유저 인풋 분리하기
    similar_doc = search_similar_documents(query_embedding)
    if not similar_doc:
        return "검색된 문서가 없습니다."

    # 검색된 문서의 내용
    doc_content = similar_doc.content

    # 실제로 사용할 LangChain LLM (PDF 예시 기준)
    llm = OpenAI(model="gpt-4", api_key="YOUR_API_KEY")  # 예시

    # 사용자 질문과 관련 문서를 이용하여 프롬프트 생성
    prompt = f"이 질문에 대한 답을 이 문서를 기반으로 생성하세요:\n\n{doc_content}\n\n질문: {user_input}"

    # LLM 호출
    response = llm([HumanMessage(content=prompt)])
    # response는 통상 {'text': '...'} 형태이거나, ChatOpenAI 객체 구조에 따라 변동
    # langchain==0.0.100 이후 ChatOpenAI는 보통 AIMessage를 반환
    return response['text']
