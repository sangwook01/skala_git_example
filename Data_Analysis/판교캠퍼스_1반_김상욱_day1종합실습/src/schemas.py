"""
스키마 정의 (Pydantic v2)
--------------------------------------------------------------
3개 API에서 뽑아낸 필드를 타입·범위 검증하는 모델을 정의

- WeatherHourRecord : Open-Meteo 시간대별 기온/강수확률
- CountryInfo        : countries.dev 국가 정보(대한민국)
- IPInfo             : ip-api IP 기반 지역 정보

세 모델 모두 "범위를 벗어난 값"을 걸러내는 것이 목적이기 때문에, 단순 타입 체크뿐만 아니라 field_validator로 현실적인 상한/하한을 함께 검증하는 로직을 추가
"""

from datetime import datetime

from pydantic import BaseModel, ValidationError, field_validator


def format_validation_error(e: ValidationError) -> str:
    """
    pydantic ValidationError를 '필드: 한글메시지' 형태로 가공.
    pydantic이 자동으로 붙이는 'Value error, ' 접두어와 문서 링크 등
    영어 부가 텍스트를 제거해 로그가 한글 위주로 읽히도록 한다.
    """
    parts = []
    for err in e.errors():
        field = ".".join(str(loc) for loc in err["loc"])
        msg = err["msg"]
        if msg.startswith("Value error, "):
            msg = msg[len("Value error, "):]
        parts.append(f"{field}: {msg}")
    return " / ".join(parts)


class WeatherHourRecord(BaseModel):
    """
    Open-Meteo hourly 응답 한 시간 슬롯에 대응하는 레코드.

    temperature: 서울 기준 현실적인 기온 범위(-40~50℃)를 벗어나면 이상치로 간주.
    precipitation_probability: 확률이므로 0~100 범위를 벗어나면 오류.
    범위 제약은 Field(ge=/le=) 대신 커스텀 validator로 둬서 오류 메시지를 한글로 직접 제어 (Field 제약은 영어 메시지가 고정으로 나옴). -> 가독성을 높이기 위해
    """

    time: datetime
    temperature: float
    precipitation_probability: int

    @field_validator("temperature")
    @classmethod
    def temperature_in_range(cls, v: float) -> float:
        if not (-40 <= v <= 50):
            raise ValueError("temperature는 -40~50 범위를 벗어났습니다.")
        return v

    @field_validator("precipitation_probability")
    @classmethod
    def probability_in_range(cls, v: int) -> int:
        if not (0 <= v <= 100):
            raise ValueError("precipitation_probability는 0~100 범위를 벗어났습니다.")
        return v


class CountryInfo(BaseModel):
    """countries.dev /alpha/{code} 응답에서 뽑은 국가 정보."""

    name: str
    capital: str
    region: str
    population: int
    area: float

    @field_validator("name", "capital", "region")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("빈 값은 허용되지 않습니다.")
        return v

    @field_validator("population")
    @classmethod
    def population_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("population은 0보다 커야 합니다.")
        return v

    @field_validator("area")
    @classmethod
    def area_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("area는 0보다 커야 합니다.")
        return v


class IPInfo(BaseModel):
    """ip-api /json/{ip} 응답에서 뽑은 IP 기반 지역 정보.

    status가 'success'가 아니면(예: 'fail') ip-api 자체가 조회 실패를
    의미하므로 검증 오류로 처리한다.
    """

    query: str
    status: str
    country: str
    region_name: str
    city: str
    isp: str
    lat: float
    lon: float

    @field_validator("status")
    @classmethod
    def must_be_success(cls, v: str) -> str:
        if v != "success":
            raise ValueError(f"ip-api 조회 실패 상태입니다: {v}")
        return v

    @field_validator("lat")
    @classmethod
    def lat_in_range(cls, v: float) -> float:
        if not (-90 <= v <= 90):
            raise ValueError("lat는 -90~90 범위를 벗어났습니다.")
        return v

    @field_validator("lon")
    @classmethod
    def lon_in_range(cls, v: float) -> float:
        if not (-180 <= v <= 180):
            raise ValueError("lon은 -180~180 범위를 벗어났습니다.")
        return v
