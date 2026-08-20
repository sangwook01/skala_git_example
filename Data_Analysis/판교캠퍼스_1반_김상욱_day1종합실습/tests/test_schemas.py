"""
스키마 검증 테스트
--------------------------------------------------------------
WeatherHourRecord / CountryInfo / IPInfo가 정상 데이터는 통과시키고,
범위를 벗어나거나 필수 조건을 어긴 데이터는 ValidationError를 내는지 검증한다.

pytest를 기반으로 확인

"""

import pytest
from pydantic import ValidationError

from src.schemas import CountryInfo, IPInfo, WeatherHourRecord


class TestWeatherHourRecord:
    def test_valid_record_passes(self):
        record = WeatherHourRecord(
            time="2026-08-03T09:00",
            temperature=27.5,
            precipitation_probability=40,
        )
        assert record.temperature == 27.5
        assert record.precipitation_probability == 40

    def test_precipitation_probability_out_of_range_raises(self):
        with pytest.raises(ValidationError):
            WeatherHourRecord(
                time="2026-08-03T09:00",
                temperature=27.5,
                precipitation_probability=150,  # 100 초과 -> 오류
            )

    def test_temperature_out_of_range_raises(self):
        with pytest.raises(ValidationError):
            WeatherHourRecord(
                time="2026-08-03T09:00",
                temperature=120.0,  # 현실적인 상한 초과 -> 오류
                precipitation_probability=10,
            )


class TestCountryInfo:
    def test_valid_record_passes(self):
        record = CountryInfo(
            name="Korea (Republic of)",
            capital="Seoul",
            region="Asia",
            population=51780579,
            area=100210,
        )
        assert record.capital == "Seoul"

    def test_negative_population_raises(self):
        with pytest.raises(ValidationError):
            CountryInfo(
                name="Korea (Republic of)",
                capital="Seoul",
                region="Asia",
                population=-1,  # 0 이하 -> 오류
                area=100210,
            )

    def test_blank_capital_raises(self):
        with pytest.raises(ValidationError):
            CountryInfo(
                name="Korea (Republic of)",
                capital="   ",  # 빈 값 -> 오류
                region="Asia",
                population=51780579,
                area=100210,
            )


class TestIPInfo:
    def test_valid_record_passes(self):
        record = IPInfo(
            query="8.8.8.8",
            status="success",
            country="United States",
            region_name="Virginia",
            city="Ashburn",
            isp="Google LLC",
            lat=39.0438,
            lon=-77.4874,
        )
        assert record.status == "success"

    def test_failed_status_raises(self):
        with pytest.raises(ValidationError):
            IPInfo(
                query="0.0.0.0",
                status="fail",  # ip-api 조회 실패 -> 오류
                country="",
                region_name="",
                city="",
                isp="",
                lat=0,
                lon=0,
            )

    def test_latitude_out_of_range_raises(self):
        with pytest.raises(ValidationError):
            IPInfo(
                query="8.8.8.8",
                status="success",
                country="United States",
                region_name="Virginia",
                city="Ashburn",
                isp="Google LLC",
                lat=999,  # 위도 범위(-90~90) 초과 -> 오류
                lon=-77.4874,
            )
