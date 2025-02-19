import re
import requests
from openai import OpenAI

client = OpenAI()
import json
from django.conf import settings
from openai import OpenAIError


NAVER_CLIENT_ID = settings.NAVER_CLIENT_ID
NAVER_CLIENT_SECRET = settings.NAVER_CLIENT_SECRET
OPENAI_API_KEY = settings.OPENAI_API_KEY


def get_travel_recommendations(keyword, display_count=5):
    url = 'https://openapi.naver.com/v1/search/local.json'
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }

    params = {'query' : keyword, 'display' : display_count}
    response = requests.get(url, headers=headers, params=params)

    print(f'네이버 API 응답 코드: {response.status_code}')

    if response.status_code == 200:
        try:
            data = response.json()
            print(data)
            travel_spots = [item['title'].replace('<b>', '').replace('</b>', '') for item in data['items']]
            print(f'📌 네이버 API 응답 데이터: {json.dumps(data, indent=2, ensure_ascii=False)}')

            if not travel_spots:
                return [f"네이버 API에서 여행지 데이터를 찾을 수 없습니다. (total: {data.get('total', 0)})"]

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
    def get_chatgpt_response(user_input, user_data):
        print(user_input, user_data)
        try:
            response = client.chat.completions.create(model = 'gpt-4',
            messages = [{'role' : 'system', 'content' : '당신은 경력 20년차 베테랑 여행 가이드입니다. '
                '사용자가 요청하면 JSON 형식으로 상세한 여행 일정을 반환합니다. '
                '일정은 하루를 오전, 점심, 오후, 저녁 순으로 나누고 각 활동에 대해 상세한 설명을 추가하세요. '
                '사용자가 요청한 여행에 맞게 여행 일정을 계획해주세요. 예를 들어 "서울 2일 여행 일정"이라면 서울에 맞는 여행 일정을 제공해 주세요. '
                f'사용자가 요청한 여행: '
                f'시작 날짜: {user_data["start_date"]}, '
                f'종료 날짜: {user_data["end_date"]}, '
                f'목적지: {user_data["destination"]}, '
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
