from django.db import models
from django.core.exceptions import ValidationError
from .services import retrieve_travel_context


class UserData(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    preference = models.TextField()
    destination = models.CharField(max_length=255, null=True, blank=True)
    
    def duration(self):
        try:
            if self.start_date > self.end_date:
                raise ValidationError("시작 날짜는 종료 날짜보다 이후일 수 없습니다.")
            
            return (self.end_date - self.start_date).days + 1

        except ValidationError as e:
            raise e

        except Exception as e:
            raise ValidationError(f"예기치 못한 오류가 발생했습니다: {str(e)}")
    
    def __str__(self):
        duration = self.duration()
        return f'{self.destination} ({self.start_date} ~ {self.end_date}, 총 {duration}일)'
        
        
class Place(models.Model): # 네이버 API 땡겨쓰면 사라질 가능성 있는 애임
    name = models.CharField(max_length=255)
    data = models.JSONField()
    
    def __str__(self):
        return self.name


class ChatInteraction(models.Model):
    user_data = models.ForeignKey(UserData, on_delete=models.CASCADE)
    user_input = models.TextField() # 사용자가 선택한 예시값을 프롬프팅할 때 포함시켜서 일정을 짜주도록 해야함
    bot_response = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def recommend_destination(self):
        recommend_destinations = retrieve_travel_context('인기 여행지')
        
        if recommend_destinations:
            return f"추천 여행지: {', '.join(recommend_destinations)} 중 하나를 선택해 주세요!"
        else:
            return '현재 추천할 여행지 정보를 가져올 수 없습니다. 나중에 다시 시도해 주세요.'
        
        
    def process_interaction(self):
        if '여행지 추천' in self.user_input:
            self.bot_response = self.recommend_destination()
        else:
            self.bot_response = '여행에 대해 더 알고 싶은 정보를 입력해 주세요!'
            
        self.save()
