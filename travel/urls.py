from django.urls import path
from .views import UserDataView, PlaceRecommendView, ChatbotResponseView

urlpatterns = [
    path('user-data/', UserDataView.as_view(), name='user-data'),
    path('place-recommend/', PlaceRecommendView.as_view(), name='place-recommend'),
    path('chatbot-response/', ChatbotResponseView.as_view(), name='chatbot-response'),
]
