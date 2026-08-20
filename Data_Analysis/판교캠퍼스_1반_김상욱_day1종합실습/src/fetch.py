"""
비동기 데이터 수집
--------------------------------------------------------------
httpx.AsyncClient + asyncio.gather()로 
3개 API(Open-Meteo, countries.dev, ip-api)를 동시에 호출. 
 
비동기 처리를 기반으로 코드를 작성하며 개별 API가 실패해도(타임아웃/네트워크 오류/HTTP오류) 전체 파이프라인이 죽지 않도록 
각 요청을 fetch_json()에서 개별적으로 try-except 처리하고, 실패 시 None을 반환한다.
"""

import asyncio
import logging

import httpx

logger = logging.getLogger(__name__)

# 교수님께서 주신 url 기반으로 변수명 세팅
WEATHER_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=37.5665&longitude=126.9780"
    "&hourly=temperature_2m,precipitation_probability"
    "&forecast_days=3&timezone=Asia/Seoul"
)
COUNTRY_URL = "https://countries.dev/alpha/KOR"
IP_URL = "http://ip-api.com/json/8.8.8.8"

REQUEST_TIMEOUT = 10.0  # 초


async def fetch_json(client: httpx.AsyncClient, url: str, name: str) -> dict | None:
    """단일 API를 호출해 JSON을 반환. 실패 시 로그만 남기고 None 반환
    (다른 API 수집까지 실패시키지 않기 위함)."""
    try:
        response = await client.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        logger.info(f"[{name}] 수집 성공 (status={response.status_code})")
        return response.json()
    except httpx.TimeoutException:
        logger.error(f"[{name}] 요청 시간 초과: {url}")
    except httpx.HTTPStatusError as e:
        logger.error(f"[{name}] HTTP 오류 {e.response.status_code}: {url}")
    except httpx.RequestError as e:
        logger.error(f"[{name}] 네트워크 오류: {e}")
    except ValueError as e:  # response.json() 파싱 실패
        logger.error(f"[{name}] JSON 파싱 오류: {e}")
    return None


async def fetch_all() -> dict:
    """
    3개 API를 asyncio.gather()로 동시에 호출해 원본 JSON을 dict로 반환.
    키: 'weather', 'country', 'ip'. 각 값은 실패 시 None일 수 있다.
    """
    async with httpx.AsyncClient() as client:
        weather, country, ip = await asyncio.gather(
            fetch_json(client, WEATHER_URL, "weather"),
            fetch_json(client, COUNTRY_URL, "country"),
            fetch_json(client, IP_URL, "ip"),
        )
    return {"weather": weather, "country": country, "ip": ip}
