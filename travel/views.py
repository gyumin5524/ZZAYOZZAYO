from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import UserData
from .services import get_travel_recommendations, ChatbotService
from .serializers import UserDataSerializer

# Create your views here.

class UserDataView(APIView):
    def post(self, request):
        try:
            serializer = UserDataSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message' : '사용자 정보 저장 성공!'}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message' : f'오류 발생: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# 1.요청--> 사용자 정보 받아오기= 메소드 : 포스트
# 2.처리--> 디비에 저장해야함
# 3.응답--> 리스폰스 저장 성공



class PlaceRecommendView(APIView):
    def get(self, request):
        keyword = request.GET.get('query', '국내 여행지 추천')
        
        try:
            display = int(request.GET.get('display', 5))
        except ValueError:
            return Response({'message' : 'display 값이 올바르지 않습니다. 숫자를 입력하세요.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            travel_recommendations = get_travel_recommendations(keyword, display)
            return Response({'추천 여행지' : travel_recommendations}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message' : f'오류 발생: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#1.요청--> 사용자에게 정보를 보여줘야함= 메소드 : 겟
#2.처리--> 네이버 API 끌어땡겨서 보여줘야댐
#3.응답--> 2번의 데이터를 제이슨형태로 변환하여 보여줄 것


class ChatbotResponseView(APIView):
    def post(self, request):
        try:
            user_input = request.data.get('user_input')
            if not user_input:
                return Response({'message' : '사용자의 입력이 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)
            
            bot_response = ChatbotService.get_chatgpt_response(user_input)
            
            return Response({'user_input' : user_input, 'bot_response' : bot_response}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error' : f'서버 오류: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#1.요청--> 지피티한테 사용자와의 대화정보 데이터를 입력해서 넘겨줘야함= 메소드 : 포스트
#2.처리--> 지피티 API 양식 입력
#3.응답--> 지피티가 정리해서 response (얘도 응답방식을 모르기 땜에 네이버 클래스뷰 응답처럼 제이슨 변환해야함)