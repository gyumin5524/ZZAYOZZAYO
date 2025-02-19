import requests
import openai
import json
from django.conf import settings
from openai import OpenAIError


NAVER_CLIENT_ID = settings.NAVER_CLIENT_ID
NAVER_CLIENT_SECRET = settings.NAVER_CLIENT_SECRET
OPENAI_API_KEY = settings.OPENAI_API_KEY


def get_travel_recommendations(keyword='국내 여행지 추천'):
    url = 'https://openapi.naver.com/v1/search/local.json'
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    
    params = {'query' : keyword, 'display' : 5}
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        try:
            data = response.json()
            travel_spots = [item['title'].replace('<b>', '').replace('</b>', '') for item in data['items']]
            return travel_spots
        except json.JSONDecodeError:
            return ['API 응답을 처리하는 중 오류가 발생했습니다.']
    else:
        return [f'네이버 API 오류 발생 (상태 코드: {response.status_code})']
    

def adjust_travel_schedule(schedule):
    for day, activities in schedule.items():
        if "한라산 등반" in activities:
            activities.remove("한라산 등반") 
            activities.insert(0, "한라산 등반 (오전 등반 필수)") 

    return schedule
    
    
class ChatbotService:
    @staticmethod    
    def get_chatgpt_response(user_input):
        try:
            response = openai.ChatCompletion.create(
                model = 'gpt-4',
                messages = [{'role' : 'system', 'content' : '당신은 경력 20년차 베테랑 여행 가이드입니다. 사용자가 요청하면 JSON 형식으로 일정을 반환하세요. 예시: {"day1": ["한라산 등반", "성산일출봉"], "day2": ["우도 탐방", "카페 투어"]}'},
                            {'role' : 'user', 'content' : user_input}],
                temperature = 0.7
            )
            raw_schedule = response['choices'][0]['message']['content'].strip()
            
            try:
                schedule = json.loads(raw_schedule)
            except json.JSONDecodeError:
                return {'error' : '일정 추천 결과를 처리하는 중 오류가 발생했습니다. 다시 시도해 주세요.', 'raw_response' : raw_schedule}
            
            adjusted_schedule = adjust_travel_schedule(schedule)
            return {'success' : True, 'schedule' : adjusted_schedule}
        
        except OpenAIError as oe:
            return {'error': f'OpenAI API 호출 오류: {str(oe)}'}
        
        except Exception as e:
            return f'오류 발생: {str(e)}'
