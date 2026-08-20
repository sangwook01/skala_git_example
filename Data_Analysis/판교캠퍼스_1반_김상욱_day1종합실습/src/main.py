"""
[Day 1] 종합 실습 - 실무형 수집/검증/품질 파이프라인
--------------------------------------------------------------
<실습 과제 내용 정리>
1. Open-Meteo(서울 3일 시간대별 기온/강수확률), countries.dev(대한민국 국가 정보), ip-api(IP 지역 정보) 
  => 3개 API를 asyncio + httpx로 동시에 수집
2. Pydantic v2 스키마로 타입/범위를 검증 
3. 검증을 통과한 데이터만 CSV와 Parquet 두 형식으로 저장 -> 이후 다시 읽어 쓰기/읽기 시간을 비교

< 코드 실행 순서 >
  실행 순서:
1) fetch.fetch_all()  - 3개 API 동시 수집 (asyncio.gather)
2) 각 API의 raw JSON에서 필요한 필드만 추출해 dict 리스트로 변환
3) schemas의 Pydantic 모델로 검증 (valid/errors 분리, 한글 오류 로그)
4) storage.save_and_compare()로 CSV/Parquet 저장 + 성능 비교
"""

import asyncio
import logging

import pandas as pd
from pydantic import ValidationError

from src.fetch import fetch_all
from src.schemas import CountryInfo, IPInfo, WeatherHourRecord, format_validation_error
from src.storage import print_comparison, save_and_compare

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

OUTPUT_DIR = "data"


def extract_weather_rows(raw: dict | None) -> list[dict]:
    """
    Open-Meteo 응답의 hourly 블록을 시간 단위 dict 리스트로 변환.
    """
    if not raw or "hourly" not in raw:
        return []
    hourly = raw["hourly"]
    times = hourly.get("time", [])
    temps = hourly.get("temperature_2m", [])
    precs = hourly.get("precipitation_probability", [])
    return [
        {"time": t, "temperature": temp, "precipitation_probability": prec}
        for t, temp, prec in zip(times, temps, precs)
    ]


def extract_country_row(raw: dict | None) -> dict | None:
    """
    countries.dev 응답에서 필요한 필드만 추출.
    """
    if not raw:
        return None
    return {
        "name": raw.get("name"),
        "capital": raw.get("capital"),
        "region": raw.get("region"),
        "population": raw.get("population"),
        "area": raw.get("area"),
    }


def extract_ip_row(raw: dict | None) -> dict | None:
    """
    ip-api 응답에서 필요한 필드만 추출 (regionName -> region_name).
    """
    if not raw:
        return None
    return {
        "query": raw.get("query"),
        "status": raw.get("status"),
        "country": raw.get("country"),
        "region_name": raw.get("regionName"),
        "city": raw.get("city"),
        "isp": raw.get("isp"),
        "lat": raw.get("lat"),
        "lon": raw.get("lon"),
    }


def validate_rows(rows: list[dict], model) -> tuple[list, list[dict]]:
    """
    rows를 model로 검증. 성공→valid, 실패→errors({row, error}).
    """
    valid, errors = [], []
    for row in rows:
        try:
            valid.append(model(**row))
        except ValidationError as e:
            error_msg = format_validation_error(e)
            logger.error(f"검증 실패({model.__name__}): {row} -> {error_msg}")
            errors.append({"row": row, "error": error_msg})
    return valid, errors


def run_pipeline() -> None:
    """
    전체 파이프라인 실행: 수집 -> 검증 -> 저장/성능비교.
    """
    raw = asyncio.run(fetch_all())

    # weather: 여러 행
    weather_rows = extract_weather_rows(raw["weather"])
    weather_valid, weather_errors = validate_rows(weather_rows, WeatherHourRecord)
    print(f"[weather] 원본 {len(weather_rows)}건 / valid {len(weather_valid)}건 "
          f"/ errors {len(weather_errors)}건")

    # country: 단일 행
    country_row = extract_country_row(raw["country"])
    country_valid, country_errors = validate_rows(
        [country_row] if country_row else [], CountryInfo
    )
    print(f"[country] valid {len(country_valid)}건 / errors {len(country_errors)}건")

    # ip: 단일 행
    ip_row = extract_ip_row(raw["ip"])
    ip_valid, ip_errors = validate_rows([ip_row] if ip_row else [], IPInfo)
    print(f"[ip] valid {len(ip_valid)}건 / errors {len(ip_errors)}건")

    # 검증 통과분만 저장 + CSV/Parquet 성능 비교
    for name, records in (
        ("weather", weather_valid),
        ("country", country_valid),
        ("ip", ip_valid),
    ):
        if not records:
            print(f"[{name}] 저장할 valid 데이터가 없어 건너뜁니다.")
            continue
        df = pd.DataFrame([r.model_dump() for r in records])
        timings = save_and_compare(df, OUTPUT_DIR, name)
        print_comparison(name, timings)

    print("\n파이프라인 실행 완료")


if __name__ == "__main__":
    run_pipeline()
