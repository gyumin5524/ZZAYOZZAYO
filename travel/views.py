from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import UserData
from .serializers import UserDataSerializer
from .services import fetch_data_from_naver, build_faiss_index, ChatbotService, retrieve_travel_context, crawl_naver_api
from .langchain_llm import generate_response
from .rag import search_similar_documents
from .embedding import generate_embedding
from .update_embedding import update_embeddings_for_crawled_data
import numpy as np


class UserDataView(APIView):
    def post(self, request):
        serializer = UserDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': '사용자 정보 저장 성공!'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class PlaceRecommendView(APIView):
    def post(self, request):
        user_input = request.data.get('user_input', '').strip()
        display_count = request.data.get('display_count', 5)
        
        if not user_input:
            return Response({'message' : '메세지를 입력하세요.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            travel_recommendations = crawl_naver_api(user_input, display_count)
            return Response({'추천 여행지' : travel_recommendations}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'message' : f'오류 발생: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CrawlAndIndexView(APIView):
    """
    네이버 API로 여행 데이터를 크롤링하고 임베딩(FAISS, BERT)을 통해 데이터 저장 및 인덱스 구축하는 엔드포인트.
    """
    def post(self, request):
        # 예시: 클라이언트에서 검색어를 보내면 해당 키워드로 크롤링 진행
        query = request.data.get("query", "여행")
        docs = fetch_data_from_naver()  # 네이버 API 크롤링
        if docs:
            build_faiss_index(docs)
            return Response({"message": "크롤링 및 인덱스 구축 완료", "documents": docs}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "크롤링 실패"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChatResponseView(APIView):
    """
    RAG와 LangChain LLM을 사용하여 사용자 질문에 대해 답변을 생성하는 엔드포인트.
    """
    def post(self, request):
        user_query = request.data.get("user_query")
        user_data = request.data.get("user_data")
        if not user_query:
            return Response({"error": "질문을 입력하세요."}, status=status.HTTP_400_BAD_REQUEST)
        if not user_data:
            return Response({"error": "사용자 정보를 제공하세요."}, status=status.HTTP_400_BAD_REQUEST)
        
        answer = ChatbotService.get_chatgpt_response(user_query, user_data)
        return Response({
            "user_query": user_query,
            "answer": answer
        }, status=status.HTTP_200_OK)

# class ChatbotAPIView(APIView):
#     def post(self, request, *args, **kwargs):
#         query = request.data.get('query', {})
#         print(query)
#         # 여기서 쿼리의 유저데이터, 인풋 분리시킬 것
#         user_data = query.get('user_data', '')
#         user_input = query.get('user_input', '')
        
#         print(type(user_data))
#         print(user_input)
        
#         if not query:
#             return Response({"error": "query is required"}, status=status.HTTP_400_BAD_REQUEST)

#         # 1. 사용자가 입력한 질문에 대해 임베딩을 생성
#         query_embedding = generate_embedding(''.join(user_data[2:])).reshape(1, -1)
#         print(''.join(user_data[2:]))
        
#         # 2. RAG 방식으로 유사한 문서 검색
#         # similar_document = search_similar_documents(query_embedding)
        
#         # if similar_document is None:
#         #     return Response({"error": "No similar documents found."}, status=status.HTTP_404_NOT_FOUND)
        
#         # 3. LangChain을 사용하여 유사한 문서를 기반으로 답변 생성
#         try:
#             response = generate_response(query_embedding, user_input)
#             return Response({"response": response}, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ChatbotAPIView(APIView):
    def post(self, request, *args, **kwargs):
        query = request.data.get('query', {})
        print(query)

        if not query:
            return Response({"error": "query is required"}, status=status.HTTP_400_BAD_REQUEST)

        user_data = query.get('user_data', '')
        user_input = query.get('user_input', '')
        print(user_data)
        print(user_input)

        if not user_input:
            return Response({"error": "user_input 내놔."}, status=status.HTTP_400_BAD_REQUEST)

        # if isinstance(user_data, list):
        #     user_data_text = ' '.join([str(item) for item in user_data[2:]]) if len(user_data) > 2 else ' '.join([str(item) for item in user_data])
        # else:
        #     user_data_text = str(user_data).strip()
        
        if user_data is None:
            user_data_text = "" 
        elif isinstance(user_data, dict):
            user_data_text = user_data.get('destination', '')
        else:
            user_data_text = ' '.join([str(item) for item in user_data])

        print(f"Processed user_data_text: {user_data_text}")

        try:
            query_embedding = generate_embedding(user_data_text)

            # NaN 벡터 검사
            if np.isnan(query_embedding).any() or np.isinf(query_embedding).any():
                print(f"zero vector 변환.")
                query_embedding = np.zeros(768, dtype=np.float32)

            query_embedding = query_embedding.reshape(1, -1)

            if np.isnan(query_embedding).any() or np.isinf(query_embedding).any():
                return Response({"error": "임베딩이 NaN을 포함하고 있어 안됨."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({"error": f"임베딩 생성 중 오류 발생: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            print(f"query_embedding.shape: {query_embedding.shape}")
            print(f"user_input: {user_input}")

            response = generate_response(query_embedding, user_input, user_data)

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"LangChain 응답 생성 오류: {str(e)}\n{error_details}")
            response = "LangChain 응답 생성 오류.. 후... 뭐야 이게."

        return Response({"response": response}, status=status.HTTP_200_OK)
        
        
class FetchDataAPIView(APIView):
    def post(self, request, *args, **kwargs):
        query = request.data.get('query')  # 'query'는 요청의 바디에서 받아오는 키워드
        if not query:
            return Response({"error": "query is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 네이버 API 크롤링 실행, 키워드를 전달
            fetch_data_from_naver(query=query)
            return Response({"message": "데이터 크롤링이 완료되었습니다."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    
        

class EmbeddingDataView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            update_embeddings_for_crawled_data()

            return Response({"message": "임베딩 업데이트가 완료되었습니다."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"임베딩 업데이트 중 오류 발생: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)