import arrow
import requests

from openai import OpenAI
from settings.settings import settings

SERVICE_KEY = settings.service_key
API_URL = settings.api_url

STATUS_OF_SKY = {
    "1": "맑음 ☀️",
    "3": "구름많음 ☁️",
    "4": "흐림 ⛅️",
}

params = {
    "serviceKey": SERVICE_KEY,
    "numOfRows": "10",
    "dataType": "JSON",
    "base_time": "0200",
    "nx": "62",
    "ny": "125",
}


def get_openai_client() -> OpenAI:
    return OpenAI(api_key=settings.openai_api_key)


def get_region_name_keyword_extract(llm_client: OpenAI, query: str) -> str:
    prompt = f"{query}에서 지역명 키워드 추출해줘."
    response = llm_client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=50,
    )
    return response.choices[0].message.content.strip()


def get_weater_data_from_kma(
    fcst_time: str,
) -> str:
    base_date = arrow.now("Asia/Seoul").format("YYYYMMDD")
    params["base_date"] = base_date
    params["pageNo"] = "3"

    response = requests.get(API_URL, params=params)
    response.raise_for_status()
    data = response.json()

    items = data["response"]["body"]["items"]["item"]
    found = next(
        filter(
            lambda x: x["category"] == "SKY" and x["fcstTime"] == fcst_time,
            items,
        ),
        None,
    )

    return STATUS_OF_SKY[found["fcstValue"]]


def get_result_food_and_travel_rec_info(
    llm_client: OpenAI,
    weather_condition: str,
    local_name: str,
) -> str:
    prompt = f"현재 날씨는 {weather_condition}인데 날씨에 어울리는 {local_name}지역에서의 음식과 날씨에 어울리는 {local_name}지역의 여행정보 추천해줘."
    response = llm_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
    )
    return response.choices[0].message.content.strip()


def test_scenario() -> str:
    query = "서울의 음식정보와 여행정보 추천해줘."
    llm_client = get_openai_client()
    local_name = get_region_name_keyword_extract(llm_client, query)
    weather_condition = get_weater_data_from_kma("0500")
    result = get_result_food_and_travel_rec_info(
        llm_client, weather_condition, local_name
    )
    return print(result)


if __name__ == "__main__":
    test_scenario()
