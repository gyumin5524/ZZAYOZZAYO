from django.urls import path
from .views import UserDataView, PlaceRecommendView, ChatResponseView, FetchDataAPIView, ChatbotAPIView, EmbeddingDataView

urlpatterns = [
    path('user-data/', UserDataView.as_view(), name='user-data'),
    path('place-recommend/', PlaceRecommendView.as_view(), name='place-recommend'),
    # path('chatbot-response/', ChatResponseView.as_view(), name='chatbot-response'),
    path('fetch-data/', FetchDataAPIView.as_view(), name='fetch-data'),
    path('chatbot/', ChatbotAPIView.as_view(), name='chatbot'),
    path('update-embedding/', EmbeddingDataView.as_view(), name='update-embedding')
]
