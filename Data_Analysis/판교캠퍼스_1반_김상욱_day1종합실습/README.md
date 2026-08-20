# [Day 1] 종합 실습 - 실무형 수집·검증·품질 파이프라인

Open-Meteo(서울 3일 시간대별 기온·강수확률), countries.dev(대한민국 국가 정보),
ip-api(IP 기반 지역 정보) 3개 API를 `asyncio + httpx`로 동시에 수집하고,
`Pydantic v2`로 타입·범위를 검증한 뒤, 검증을 통과한 데이터만 CSV/Parquet
두 형식으로 저장하며 읽기·쓰기 성능을 비교하는 파이프라인입니다.

## 폴더 구조

```
.
├── requirements.txt
├── pyproject.toml        # pytest / ruff 설정
├── .gitignore
├── README.md
├── src/
│   ├── schemas.py         # Pydantic v2 모델 (WeatherHourRecord/CountryInfo/IPInfo)
│   ├── fetch.py            # httpx + asyncio.gather() 동시 수집
│   ├── storage.py          # CSV/Parquet 저장 + 성능 비교
│   └── main.py              # 전체 파이프라인 오케스트레이션
├── tests/
│   └── test_schemas.py     # pytest 스키마 검증 테스트
└── data/                    # 실행 시 CSV/Parquet 결과물이 저장되는 폴더
```

## 설치 및 실행 방법

```bash
# 1) venv 생성 및 활성화
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2) 패키지 설치
pip install -r requirements.txt

# 3) 파이프라인 실행 (수집 -> 검증 -> 저장 -> 성능비교)
python -m src.main

# 4) 테스트 실행
pytest -v

# 5) 코드 스타일 검사
ruff check .

# 6) Git 커밋 (최초 1회)
git init
git add .
git commit -m "chore: 프로젝트 스캐폴딩"
git add src/
git commit -m "feat: 비동기 수집 + Pydantic 검증 + CSV/Parquet 저장 파이프라인 구현"
git add tests/
git commit -m "test: 스키마 검증 pytest 케이스 추가"
# 이후 GitHub 원격 저장소 연결 후 push
```

## 실행 흐름

1. `fetch.fetch_all()` — `httpx.AsyncClient` + `asyncio.gather()`로 3개 API를
   동시에 호출. 개별 API가 실패해도(타임아웃/HTTP 오류/네트워크 오류) 로그만
   남기고 `None`을 반환해 다른 API 수집을 막지 않음.
2. `main.extract_*` 함수들이 각 API의 raw JSON에서 필요한 필드만 추출.
3. `schemas`의 Pydantic 모델로 검증 — 실패한 레코드는 `format_validation_error()`로
   한글 메시지만 남긴 뒤 valid/errors 리스트로 분리.
4. `storage.save_and_compare()`가 검증 통과분을 CSV/Parquet로 저장하고, 저장
   직후 다시 읽어 쓰기/읽기 시간·파일 크기를 측정.
