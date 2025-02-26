import requests
from django.conf import settings
from .models import CrawledData

def fetch_data_from_naver():
    """
    PDF 예시처럼, 네이버 API에 요청을 보내어 데이터를 크롤링하고
    CrawledData 모델에 저장하는 함수.
    """
    # 실제로 사용할 네이버 API URL (여기서는 예시)
    naver_api_url = "https://openapi.naver.com/v1/search/local.json"

    # 네이버 API 호출에 필요한 인증 정보
    headers = {
        "X-Naver-Client-Id": settings.NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": settings.NAVER_CLIENT_SECRET
    }

    # 검색 파라미터(예: query, display 등)
    params = {
        "query": "여행",
        "display": 5
        # 필요한 다른 파라미터를 추가
    }

    response = requests.get(naver_api_url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        for item in data.get("items", []):
            title = item.get("title", "").replace("<b>", "").replace("</b>", "")
            url = item.get("link", "")
            address = item.get("address", "")

            # 모델에 저장 (이미 존재하면 중복 저장 방지 로직 등을 추가할 수 있음)
            CrawledData.objects.create(
                title=title,
                url=url,
                address=address,
                embedding=None  # 임베딩은 추후 업데이트
            )
    else:
        print(f"네이버 API 오류 발생 (상태 코드: {response.status_code})")
