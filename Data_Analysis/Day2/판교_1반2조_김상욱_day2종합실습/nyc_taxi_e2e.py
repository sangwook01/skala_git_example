"""
================================================================================================
[Day 2 종합 실습] End2End 데이터 분석 프로젝트
"가성비 좋은 택시 탑승 조건" (NYC Yellow Taxi, 2026-05)
================================================================================================

목표
----
"어떤 조건일 때 마일당 비용이 저렴한, 가성비 좋은 탑승인가"를 4개의 가설로 정리하고,
통계 검정(t-test)과 ML 분류(RandomForest) 두 가지 방법으로 각각 검증한다.

원본 데이터
----------
URL: https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2026-05.parquet

핵심 지표: cost_per_mile
-----------------------
- cost_per_mile = total_amount / trip_distance  ("마일당 실질 비용")
- fare_amount(정가)가 아니라 total_amount(공항수수료·혼잡통행료 등 부대비용을 포함한
  실결제액)를 분자로 쓴 이유: 가설 2가 "부대비용까지 포함한 실질 비용"을 비교 대상으로
  삼고 있기 때문
- is_cost_effective = cost_per_mile이 중앙값 이하인지(1=가성비 좋음)
  -> median split이라 클래스가 자연스럽게 50:50에 가깝게 균형을 이룸

가설 4개
--------
[H1, t-test] 지정 피크 시간대(08~09시, 18~20시) vs 기타 시간대의 평균 마일당 비용
             H0: 차이 없다 / H1: 지정 피크가 더 높다 (one-sided)
             * 요일 구분 없이 시각(hour)만으로 판정 -> 주말도 포함됨

[H2, t-test] 부대비용(공항수수료·혼잡통행료·CBD혼잡료) 부과 여부에 따른 평균 마일당 비용
             H0: 차이 없다 / H1: 부대비용이 있는 운행이 더 높다 (one-sided)
             * extra(심야/러시아워 시간대 할증)는 H1과 성격이 겹쳐 H2에서는 제외

[H3, 진단]   이동 거리와 가성비의 비선형 관계
             - 거리 5분위 구간별 평균 비용·가성비 비율을 표/차트로 확인

[H4, 진단]   요일·심야 등 탑승 패턴이 가성비에 영향을 미치는지
             - 주말 x 심야 조합별 가성비 비율을 표로 확인

실습 요구사항 대응표
--------------------
  1) 데이터 준비 : Pandas + Polars 비교 로딩, 결측치(컬럼별)·중복·이상치 처리, 기본 EDA
  2) 시각화      : Seaborn 정적 차트(분포/박스플롯/히트맵) + Plotly 인터랙티브 차트(그룹비교)
  3) 통계 분석    : 기술통계, 상관계수(+해석), H1·H2 t-test(one-sided), H3·H4 그룹별 진단
  4) ML Pipeline : ColumnTransformer + Pipeline(전처리 + RandomForest 분류),
                   Accuracy/F1/Feature Importance, joblib 저장
  5) 자동화       : 위 모든 결과를 report.md 한 파일로 자동 생성

산출물 (실행 위치 기준 ./output/)
----------------------------------
  - yellow_tripdata_2026-05.parquet   원본 캐시 (재다운로드 방지)
  - eda_descriptive_stats_table.png   핵심 변수 기술통계표
  - dist_seaborn.png                  마일당 비용 분포
  - eda_distance_vs_cost.png          거리 vs 비용 산점도 + 5분위 평균선
  - eda_peak_boxplot.png              지정 피크/기타 시간대 박스플롯
  - box_surcharge_seaborn.png         부대비용 유무별 박스플롯
  - h3_distance_bucket.png            거리 구간별 가성비 비율 막대그래프
  - eda_weekday_hour_heatmap.png      요일 x 시간대 평균 비용 히트맵
  - eda_correlation_heatmap.png       상관계수 히트맵
  - group_plotly.html                 시간대별 평균 비용 (인터랙티브)
  - cost_effective_model.joblib       학습된 분류 모델
  - ml_performance_table.png          모델 성능 결과표
  - report.md                         전체 분석 결과 자동 요약 리포트

주의
----
이 스크립트는 실습용 필수 라이브러리(polars/seaborn/plotly/scipy/scikit-learn/joblib/
requests)가 모두 설치되어 있다고 가정한다. 하나라도 없으면 import 단계에서 바로
ImportError로 실패하며, 이는 "일부만 실행되고 완료로 표시되는" 상황을 막기 위한
의도적인 설계다.
"""

import logging          # matplotlib이 찍는 폰트 경고 로그 레벨을 낮추기 위해 사용
import os                # 폴더 생성, 경로 조합(join)에 사용
import sys               # main()에서 치명적 오류 발생 시 종료 코드를 지정하기 위해 사용(sys.exit)
import time              # Pandas/Polars 로딩 시간을 측정하기 위한 타이머
from datetime import datetime  # report.md에 생성 시각을 기록하기 위해 사용

import pandas as pd
import matplotlib

matplotlib.use("Agg")  # 화면 출력 환경이 없어도 파일로 저장 가능하도록 (서버/CI 환경 대응)
import matplotlib.pyplot as plt
from matplotlib import font_manager

# 대부분의 한글 폰트는 별도 Bold 서체가 없어서 fontweight="bold" 지정 시 matplotlib이
# "findfont: Failed to find font weight bold..." 경고를 매번 찍는다. 동작에는 영향
# 없는 로그 노이즈라 숨긴다.
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)


def _set_korean_font() -> None:
    """
    OS별로 설치돼 있을 법한 한글 지원 폰트 후보를 순서대로 찾아 matplotlib 전역 폰트로 지정한다.
    후보를 하나도 못 찾아도 예외를 던지지 않고 경고만 출력한 뒤 기본 폰트로 계속 진행한다
    (그래프의 한글이 깨질 수 있지만 실행 자체는 막지 않기 위함). 모듈 로드 시 한 번만 호출된다.
    """
    # 폰트 이름 우선순위: Windows(Malgun Gothic) -> macOS(AppleGothic) -> Linux(나눔 계열/Noto)
    candidates = ["Malgun Gothic", "AppleGothic", "NanumGothic", "NanumBarunGothic", "Noto Sans CJK KR"]
    # 현재 시스템에 실제로 설치된 폰트 이름 목록을 집합으로 만들어 빠르게 조회
    available = {f.name for f in font_manager.fontManager.ttflist}
    for name in candidates:
        if name in available:
            plt.rcParams["font.family"] = name  # 찾은 첫 번째 폰트를 matplotlib 기본 폰트로 설정
            break
    else:
        # for-else: break 없이 루프가 끝났다는 뜻 = 후보 폰트를 하나도 못 찾음
        print("[경고] 한글 지원 폰트를 찾지 못했습니다. 그래프의 한글이 깨져 보일 수 있습니다 (실행에는 영향 없음).")
    plt.rcParams["axes.unicode_minus"] = False  # 한글 폰트 사용 시 마이너스(-) 기호가 깨지는 문제 방지


_set_korean_font()

# 실습 필수 라이브러리는 누락 시 즉시 ImportError를 내서, 일부 단계만 돌고 나머지는
# 조용히 건너뛴 "불완전한 결과"가 정상 완료처럼 보이지 않도록 한다.
import joblib                       # 학습된 sklearn 모델을 파일로 저장/로드
import plotly.express as px         # 인터랙티브(그룹비교) 차트 생성
import polars as pl                 # Pandas와 로딩 성능을 비교하기 위한 고속 데이터프레임 라이브러리
import requests                     # 원본 parquet 파일을 HTTP로 다운로드
import seaborn as sns               # matplotlib 기반 정적 통계 시각화
from scipy import stats as scipy_stats          # t-test(가설검정)
from sklearn.compose import ColumnTransformer   # 수치형/범주형 컬럼별로 다른 전처리를 적용하는 도구
from sklearn.ensemble import RandomForestClassifier  # 분류 모델
from sklearn.metrics import accuracy_score, classification_report, f1_score  # 모델 성능 지표
from sklearn.model_selection import train_test_split  # 학습/테스트 데이터 분리
from sklearn.pipeline import Pipeline                  # 전처리+모델을 하나의 흐름으로 묶음
from sklearn.preprocessing import OneHotEncoder         # 범주형 변수를 0/1 벡터로 변환


# ================================================================================================
# 설정값
# ================================================================================================
DATA_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2026-05.parquet"
OUTPUT_DIR = "output"
RAW_PATH = os.path.join(OUTPUT_DIR, "yellow_tripdata_2026-05.parquet")  # 다운로드 캐시(재실행 시 재다운로드 방지)

# 월간 전체 데이터는 수백만 행이라 노트북 환경에서 돌리기엔 과함 -> 랜덤 샘플링으로 규모 축소.
# None으로 두면 전체 데이터를 그대로 사용 (메모리/속도에 유의)
SAMPLE_N = 300_000
RANDOM_STATE = 42  # 샘플링/학습-테스트 분리/모델 학습 전 과정에서 재현성을 위해 동일한 시드를 사용

# 요금 세부 항목까지 전부 포함 -> EDA·상관계수에서 임의로 컬럼을 빼지 않는다.
# (cost_per_mile은 파생 컬럼이라 clean_data() 단계 이후에 추가됨)
NUMERIC_COLS = [
    "trip_distance", "passenger_count", "fare_amount", "extra", "mta_tax", "tip_amount",
    "tolls_amount", "improvement_surcharge", "congestion_surcharge", "Airport_fee",
    "cbd_congestion_fee", "total_amount", "trip_duration_min", "cost_per_mile",
]

# PULocationID(약 260개 구역)를 그대로 원-핫 인코딩하면 차원이 과도하게 커지므로,
# 등장 빈도 상위 N개만 개별 범주로 남기고 나머지는 'OTHER'로 묶는다.
TOP_N_ZONES = 20

# RatecodeID -> 사람이 읽을 수 있는 라벨 (TLC 데이터 딕셔너리 기준). ML 범주형 피처로 사용.
RATECODE_LABELS = {
    1: "표준요금", 2: "JFK공항", 3: "뉴어크공항", 4: "나소/웨체스터", 5: "협상요금", 6: "그룹라이드",
}

# H1에서 말하는 "지정 피크 시간대": 아침 8~9시, 저녁 18~20시.
# 요일 조건 없이 시각(hour)만으로 판정하므로 주말도 포함된다.
PEAK_HOURS = {8, 9, 18, 19, 20}

# H4에서 말하는 "심야 시간대": 22시 ~ 다음 날 05시.
# 근거: NYC TLC의 심야 할증(overnight surcharge)이 20시~다음날 06시에 부과되는 것을 참고하되,
# 20~21시는 저녁 활동 시간대와 겹쳐 "심야"로 보기 어려워 22시부터로 정의했다.
LATE_NIGHT_HOURS = {22, 23, 0, 1, 2, 3, 4, 5}


# ================================================================================================
# 유틸리티
# ================================================================================================
def _present_cols(df: pd.DataFrame, cols: list) -> list:
    """
    원하는 컬럼 목록(cols) 중 df에 실제로 존재하는 것만 걸러서 반환한다.
    스키마 차이 등으로 일부 컬럼이 없어도 KeyError 없이 나머지 로직이 계속 진행되도록 하는
    방어용 헬퍼로, 여러 함수(clean_data, categorical_summary 등)에서 공통으로 사용한다.
    """
    return [c for c in cols if c in df.columns]


def _numeric_cols_present(df: pd.DataFrame, cols: list) -> list:
    """
    컬럼이 존재하는지뿐 아니라 실제로 숫자형(dtype)인지도 검증해서 반환한다.
    이름만 보고 "당연히 숫자겠지"라고 가정하면, 스키마가 예상과 달라 특정 컬럼이
    문자열/object로 로딩된 경우 describe()/corr()에서 엉뚱한 에러가 나거나
    조용히 이상한 결과가 나올 수 있어 dtype을 직접 검사해서 방어한다.
    """
    result, skipped = [], []
    for c in cols:
        if c not in df.columns:
            continue
        if pd.api.types.is_numeric_dtype(df[c]):
            result.append(c)
        else:
            skipped.append((c, str(df[c].dtype)))
    if skipped:
        print(f"[경고] 숫자형이 아니어서 통계 대상에서 제외: {skipped}")
    return result


def _df_to_md(df: pd.DataFrame) -> str:
    """
    DataFrame을 report.md에 바로 붙여넣을 수 있는 마크다운 표 문자열로 변환한다.
    내부적으로 to_markdown()이 tabulate 패키지에 의존하는데, 그게 미설치돼 있으면
    ImportError로 리포트 생성 전체가 죽는 대신 고정폭 텍스트 코드블록으로 대체해 계속 진행한다.
    generate_report()의 모든 표 출력이 이 함수를 거친다.
    """
    try:
        return df.to_markdown()  # 내부적으로 tabulate 패키지를 사용해 마크다운 표를 생성
    except ImportError:
        # tabulate가 없으면 마크다운 표 대신 고정폭 텍스트를 코드블록으로 감싸서 대체
        return "```\n" + df.to_string() + "\n```"


def ensure_output_dir(path: str = OUTPUT_DIR) -> str:
    """
    산출물을 저장할 output 폴더가 없으면 생성한다 (있으면 아무 것도 하지 않고 통과).
    main()이 가장 먼저 호출해서, 이후 모든 저장 함수가 폴더 존재를 신경 쓰지 않게 한다.
    """
    os.makedirs(path, exist_ok=True)
    return path


# ================================================================================================
# 1) 데이터 다운로드 & 로딩 (Pandas vs Polars 비교)
# ================================================================================================
def download_raw_data(url: str = DATA_URL, dest: str = RAW_PATH) -> str:
    """
    원본 parquet을 로컬에 스트리밍 다운로드해서 캐시한다.
    이미 받아둔 파일이 있으면 그대로 재사용해서, 실행할 때마다 수백MB짜리 파일을
    다시 받지 않도록 한다.
    """
    if os.path.exists(dest):
        # 캐시 파일이 이미 있으면 네트워크 요청 자체를 하지 않고 바로 경로만 반환
        print(f"[안내] 캐시된 원본 파일 재사용: {dest}")
        return dest

    print(f"[안내] 원본 다운로드 시작: {url}")
    try:
        # stream=True: 응답 전체를 메모리에 한 번에 올리지 않고 조금씩(chunk) 받는다 (대용량 파일 대응)
        with requests.get(url, stream=True, timeout=120) as r:
            r.raise_for_status()  # 4xx/5xx 응답이면 예외를 발생시켜 아래 except에서 처리
            total = int(r.headers.get("content-length", 0))  # 서버가 전체 크기를 알려주면 진행률 표시에 사용
            downloaded = 0
            with open(dest, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        # \r로 커서를 줄 맨 앞으로 되돌려 같은 줄에 진행률을 갱신하며 출력
                        print(f"\r  {downloaded / total:.1%} ({downloaded / 1e6:.0f}MB/{total / 1e6:.0f}MB)", end="")
        print(f"\n[안내] 다운로드 완료: {dest}")
        return dest
    except Exception as e:
        # 실패 시 부분적으로 받다 만 파일이 남아, 다음 실행에서 "완료된 캐시"로
        # 오인되지 않도록 정리한다.
        if os.path.exists(dest):
            os.remove(dest)
        raise RuntimeError(f"다운로드 실패: {e}")


def load_with_pandas_and_polars(path: str):
    """
    같은 parquet 파일을 Pandas / Polars 양쪽으로 로딩해서 결과(행수·로딩시간·메모리)를
    비교한다. 두 라이브러리가 같은 데이터를 읽었는지(shape 일치)도 함께 확인한다.

    비교가 끝난 뒤에는 Polars DataFrame을 반환하지 않는다 -> 이후 분석 단계 동안
    대용량 메모리를 이중으로 점유하지 않기 위함.

    Args:
        path: 로딩할 parquet 파일 경로.
    Returns:
        (pdf, result) 튜플. pdf는 이후 모든 분석에 쓰이는 Pandas DataFrame,
        result는 report.md 1절(로딩 비교)에 그대로 들어가는 딕셔너리
        ({"pandas": {...}, "polars": {...}, "shapes_match": bool}).
    """
    print("\n=== 1) 데이터 로딩 비교: Pandas vs Polars ===")
    result = {"pandas": None, "polars": None}

    # --- Pandas로 로딩하며 시간/메모리 측정 ---
    t0 = time.perf_counter()
    pdf = pd.read_parquet(path)
    pandas_sec = time.perf_counter() - t0
    pandas_mem_mb = pdf.memory_usage(deep=True).sum() / 1e6  # deep=True: 문자열 등 객체 컬럼의 실제 메모리까지 포함
    print(f"[Pandas] shape={pdf.shape}, 로딩 {pandas_sec:.2f}s, 메모리 {pandas_mem_mb:.1f}MB")
    result["pandas"] = {"shape": pdf.shape, "seconds": pandas_sec, "memory_mb": pandas_mem_mb}

    # --- Polars로 동일 파일을 로딩하며 시간/메모리 측정 (비교용) ---
    t0 = time.perf_counter()
    pldf = pl.read_parquet(path)
    polars_sec = time.perf_counter() - t0
    polars_mem_mb = pldf.estimated_size("mb")
    print(f"[Polars] shape={pldf.shape}, 로딩 {polars_sec:.2f}s, 메모리 {polars_mem_mb:.1f}MB")
    result["polars"] = {"shape": pldf.shape, "seconds": polars_sec, "memory_mb": polars_mem_mb}
    result["shapes_match"] = pdf.shape == pldf.shape  # 두 라이브러리가 같은 행/열 수를 읽었는지 검증
    print(f"[비교] 두 라이브러리 결과 shape 일치 여부: {result['shapes_match']}")

    return pdf, result  # 이후 분석은 Pandas DataFrame(pdf)만 사용


# ================================================================================================
# 2) 데이터 정제 & 파생 컬럼 생성
# ================================================================================================
def clean_data(df: pd.DataFrame):
    """
    결측치/중복/비정상값을 처리하고, 4개 가설 검증에 필요한 파생 컬럼을 전부 만든다.
    (운행시간·시간대·요일·피크여부·심야여부·부대비용여부·마일당비용·가성비여부)

    Args:
        df: download_raw_data()로 받은 원본을 로딩한 Pandas DataFrame (정제 전).
    Returns:
        (df, summary) 튜플. df는 정제 + 파생 컬럼이 추가된 DataFrame으로 이후 모든 EDA/
        시각화/검정/ML 단계가 이 df를 그대로 사용한다. summary는 raw_rows/na_counts/
        duplicates_removed/invalid_rows_removed/cost_per_mile_outliers_removed/
        median_cost_per_mile/clean_rows 등 report.md 2절에 들어가는 처리 통계 딕셔너리.
    """
    print("\n=== 2) 결측치·중복 처리 & 파생 컬럼 생성 ===")
    summary = {"raw_rows": len(df)}  # report.md에 남길 처리 단계별 통계를 이 딕셔너리에 누적

    # --- 2-1) 컬럼 선별 -------------------------------------------------------------------
    # TLC 공식 스키마의 컬럼을 전부 로딩한다. 일부는 분석에 직접 쓰이지 않지만
    # 임의로 빼지 않고 그대로 둔다.
    needed = [
        "VendorID", "tpep_pickup_datetime", "tpep_dropoff_datetime", "passenger_count",
        "trip_distance", "RatecodeID", "store_and_fwd_flag", "PULocationID", "DOLocationID",
        "payment_type", "fare_amount", "extra", "mta_tax", "tip_amount", "tolls_amount",
        "improvement_surcharge", "total_amount", "congestion_surcharge", "Airport_fee",
        "cbd_congestion_fee",
    ]
    missing_cols = [c for c in needed if c not in df.columns]
    if missing_cols:
        print(f"[경고] 없는 컬럼 발견(스키마 차이로 추정): {missing_cols}")
    # 필요한 컬럼만 남기고 .copy()로 원본과 메모리를 분리 (이후 df에 컬럼을 추가/수정해도 원본 안전)
    df = df[_present_cols(df, needed)].copy()

    # --- 2-2) 결측치 확인 -------------------------------------------------------------------
    # 컬럼 수가 많지 않으므로 결측치가 0건인 컬럼도 걸러내지 않고 전체를 다 보여준다.
    na_counts = df.isna().sum()  # == df.isnull().sum(), pandas에서 isna/isnull은 완전히 동일한 메서드
    print("[컬럼별 결측치 개수 (isnull().sum())]")
    print(na_counts.to_string())
    summary["na_counts"] = na_counts.to_dict()  # report.md 표로 남기기 위해 dict로 저장

    # --- 2-3) 중복 제거 -------------------------------------------------------------------
    dup_count = int(df.duplicated().sum())
    print(f"[중복 행] {dup_count:,}건 제거")
    summary["duplicates_removed"] = dup_count
    df = df.drop_duplicates()

    # --- 2-4) 필수 컬럼 결측 제거 -------------------------------------------------------------------
    # cost_per_mile(= total_amount / trip_distance)을 계산하려면 이 컬럼들에 결측이 없어야 한다.
    df = df.dropna(subset=["tpep_pickup_datetime", "tpep_dropoff_datetime", "trip_distance", "fare_amount", "total_amount"])
    # passenger_count는 결측을 1명으로 확정해서 채운다. (필터링 단계에서 fillna(1)로
    # "임시로만" 채우면 실제 컬럼에는 NaN이 남는 문제가 있어, 필터링과 실제값 처리를 분리하지 않는다.)
    df["passenger_count"] = df["passenger_count"].fillna(1)

    # --- 2-5) 시간 관련 파생 컬럼 -------------------------------------------------------------------
    # 하차시각-승차시각의 차이(Timedelta)를 초 단위로 변환한 뒤 60으로 나눠 "분" 단위 운행시간 계산
    df["trip_duration_min"] = (df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]).dt.total_seconds() / 60
    df["pickup_hour"] = df["tpep_pickup_datetime"].dt.hour       # 승차 시각(0~23시) 추출 -> 피크/심야 판정에 사용
    df["pickup_dow"] = df["tpep_pickup_datetime"].dt.dayofweek   # 요일 추출: 0=월요일 ... 6=일요일
    df["is_weekend"] = df["pickup_dow"].isin([5, 6])             # 토(5)/일(6)이면 주말

    # --- 2-6) 도메인 지식 기반 이상치 필터 -------------------------------------------------------------------
    # (IQR 방식 대신, 택시 데이터 특성에 맞는 상식적인 범위를 사용)
    # - 뉴욕 택시 최소요금은 $3.00 수준이므로 2.5달러 미만은 데이터 오류로 간주
    # - 거리 0 또는 100마일 초과, 운행시간 1분 미만/3시간 초과, 승객수 0명/7명 이상은 비정상 기록으로 간주
    before = len(df)
    df = df[
        df["trip_distance"].between(0.1, 100)
        & df["fare_amount"].between(2.5, 300)
        & df["trip_duration_min"].between(1, 180)
        & df["passenger_count"].between(1, 6)
    ]
    removed = before - len(df)
    print(f"[비정상값 필터] {removed:,}건 제외 (거리/운임/운행시간/승객수 범위 밖)")
    # 참고: extra/mta_tax/tolls_amount/improvement_surcharge/congestion_surcharge/Airport_fee/
    # cbd_congestion_fee는 0이 "요금 미부과"라는 정상값이므로 여기서 이상치로 걸러내지 않는다.
    summary["invalid_rows_removed"] = removed

    # --- 2-7) 가설 검증용 핵심 파생 컬럼 -------------------------------------------------------------------
    # H1: 요일과 무관하게 지정한 피크 시간대 여부
    df["is_peak_hour"] = df["pickup_hour"].isin(PEAK_HOURS)

    # H2: 부대비용(공항수수료·혼잡통행료·CBD혼잡료) 부과 여부
    # extra는 시간대(심야/러시아워) 할증이라 H1(시간대 가설)과 겹치므로,
    # H2의 "장소성 부대비용"에서는 의도적으로 제외한다.
    has_airport = df["Airport_fee"] > 0 if "Airport_fee" in df.columns else False
    has_congestion = df["congestion_surcharge"] > 0 if "congestion_surcharge" in df.columns else False
    has_cbd = df["cbd_congestion_fee"] > 0 if "cbd_congestion_fee" in df.columns else False
    df["has_surcharge"] = has_airport | has_congestion | has_cbd

    # H4: 심야 시간대 여부
    df["is_late_night"] = df["pickup_hour"].isin(LATE_NIGHT_HOURS)

    # 핵심 지표: 마일당 실질 비용
    # (trip_distance가 이미 0.1~100 범위로 필터링돼서 0으로 나눌 위험은 없음)
    df["cost_per_mile"] = df["total_amount"] / df["trip_distance"]

    # --- 2-8) cost_per_mile IQR 극단치 정리 -------------------------------------------------------------------
    # 아주 짧은 거리에 비정상적으로 비싼 요금이 찍힌 행이 마일당 비용을 왜곡하는 것을 방지하기 위해
    # cost_per_mile 자체도 IQR 기준으로 한 번 더 정리한다.
    before_cpm = len(df)
    q1, q3 = df["cost_per_mile"].quantile(0.25), df["cost_per_mile"].quantile(0.75)  # 1사분위/3사분위
    iqr = q3 - q1  # 사분위 범위
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr  # 통계학에서 흔히 쓰는 이상치 경계 공식(1.5*IQR)
    # 1.5xIQR 공식상 하한이 음수로 계산될 수 있는데, 마일당 비용은 음수가 될 수 없는 값이므로
    # 하한을 0으로 보정한다. -> 실질적으로는 상한(upper) 초과 극단치만 제거되는 효과.
    lower = max(lower, 0.0)
    df = df[df["cost_per_mile"].between(lower, upper)]
    cpm_removed = before_cpm - len(df)
    print(f"[cost_per_mile IQR 필터] {cpm_removed:,}건 제외 (정상범위: {lower:.2f} ~ {upper:.2f} $/mile, 하한은 음수라 0으로 보정)")
    summary["cost_per_mile_outliers_removed"] = cpm_removed
    summary["cpm_bounds"] = (float(lower), float(upper))

    # 부대비용 판정에 쓰인 요금 컬럼에 결측이 있었던 규모를 별도로 기록해둔다.
    # (판정 로직 자체는 결측을 "부대비용 없음"으로 취급하므로, 그 규모를 리포트에 명시하기 위함)
    surcharge_cols = _present_cols(df, ["Airport_fee", "congestion_surcharge", "cbd_congestion_fee"])
    surcharge_missing = df[surcharge_cols].isna().any(axis=1)
    summary["surcharge_missing_rows"] = int(surcharge_missing.sum())
    # 결측이었는데도 has_surcharge가 False(부대비용 없음)로 판정된 행 수 = 잠재적 왜곡 규모
    summary["surcharge_missing_as_no_rows"] = int((surcharge_missing & ~df["has_surcharge"]).sum())

    # --- 2-9) 가성비 라벨 생성 -------------------------------------------------------------------
    # is_cost_effective: cost_per_mile이 중앙값 이하면 "가성비 좋음"(1).
    # median split을 쓰는 이유: 임의의 절대 임계값을 피할 수 있고, 클래스가 자동으로
    # 50:50에 가깝게 균형을 이뤄 이후 분류 모델 학습에도 유리하기 때문.
    median_cost_per_mile = df["cost_per_mile"].median()
    df["is_cost_effective"] = (df["cost_per_mile"] <= median_cost_per_mile).astype(int)
    summary["median_cost_per_mile"] = float(median_cost_per_mile)

    summary["clean_rows"] = len(df)
    print(f"[결과] {summary['raw_rows']:,}행 -> {summary['clean_rows']:,}행 "
          f"(마일당 중앙값: ${median_cost_per_mile:.2f})")
    return df, summary


# ================================================================================================
# 3) 기본 EDA
# ================================================================================================
def basic_eda(df: pd.DataFrame) -> pd.DataFrame:
    """
    NUMERIC_COLS 중 실제로 존재하는 숫자형 컬럼에 대해 describe() 기반 기술통계표
    (평균·표준편차·최소·사분위·최대)를 콘솔에 출력하고, 그대로 반환한다.

    Args:
        df: clean_data()를 거친 정제 완료 DataFrame.
    Returns:
        기술통계 DataFrame. plot_descriptive_stats_table()과 generate_report()가
        그대로 이어받아 표 이미지/report.md에 사용한다.
    """
    print("\n=== 3) 기본 EDA: 기술통계 ===")
    cols = _numeric_cols_present(df, NUMERIC_COLS)
    # describe(): 개수/평균/표준편차/최소/사분위/최대를 한 번에 계산 -> .T로 컬럼이 행이 되도록 전치
    desc = df[cols].describe().T[["mean", "std", "min", "25%", "50%", "75%", "max"]].round(2)
    print(desc.to_string())
    return desc


def plot_descriptive_stats_table(
    desc_stats: pd.DataFrame,
    out_path: str = os.path.join(OUTPUT_DIR, "eda_descriptive_stats_table.png"),
) -> None:
    """
    basic_eda()가 계산한 기술통계 중 핵심 변수 4개(거리/운행시간/총결제금액/마일당비용)만
    골라 발표용 표 이미지(PNG)로 저장한다. 반환값은 없고 파일 저장이 유일한 목적.

    Args:
        desc_stats: basic_eda()의 반환값.
        out_path: 저장할 PNG 경로.
    """
    print("\n=== 3-1) 핵심 변수 기술통계표 ===")
    # 표에 넣을 4개 변수만 선정 (전체 14개 변수를 다 넣으면 표가 너무 커짐)
    rows = ["trip_distance", "trip_duration_min", "total_amount", "cost_per_mile"]
    labels = {
        "trip_distance": "이동 거리 (mile)",
        "trip_duration_min": "운행 시간 (분)",
        "total_amount": "총결제금액 ($)",
        "cost_per_mile": "마일당 비용 ($/mile)",
    }
    available = [row for row in rows if row in desc_stats.index]
    if not available:
        print("표에 표시할 변수가 없어 건너뜀")
        return

    # 필요한 열(평균/중앙값/표준편차/최소/최대)만 뽑고 한글 라벨로 행/열 이름 변경
    table_data = desc_stats.loc[available, ["mean", "50%", "std", "min", "max"]].copy()
    table_data.index = [labels[row] for row in available]
    table_data.columns = ["평균", "중앙값", "표준편차", "최솟값", "최댓값"]

    try:
        fig, ax = plt.subplots(figsize=(12, 4.2))
        ax.axis("off")
        table = ax.table(
            cellText=table_data.values,
            rowLabels=table_data.index,
            colLabels=table_data.columns,
            cellLoc="center",
            rowLoc="center",
            loc="center",
        )
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1, 1.8)

        # 머리글·행 이름·본문을 구분해 발표 화면에서도 표 구조가 바로 보이게 한다.
        for (row, col), cell in table.get_celld().items():
            cell.set_edgecolor("#D9E2E7")
            if row == 0:                        # 맨 위 헤더 행
                cell.set_facecolor("#264653")
                cell.get_text().set_color("white")
                cell.get_text().set_weight("bold")
            elif col == -1:                      # 왼쪽 행 이름(변수명) 열
                cell.set_facecolor("#E8F3F1")
                cell.get_text().set_weight("bold")
            elif row % 2 == 0:                   # 짝수 행은 옅은 색으로 줄무늬 효과(가독성)
                cell.set_facecolor("#F6FAF9")

        ax.set_title("핵심 연속형 변수 기술통계", fontsize=15, color="#264653", pad=18)
        fig.tight_layout()
        fig.savefig(out_path, dpi=160, bbox_inches="tight", facecolor="white")
        plt.close(fig)  # 그림 객체를 닫아 메모리 누수를 방지 (반복 호출 시 중요)
        print(f"저장 완료: {out_path}")
    except Exception as e:
        raise RuntimeError("기술통계표 이미지 생성 실패") from e


def categorical_summary(df: pd.DataFrame) -> dict:
    """
    범주형 원본 컬럼(VendorID/RatecodeID/store_and_fwd_flag/payment_type)과
    가설용 파생 플래그(is_peak_hour/has_surcharge/is_late_night/is_cost_effective)의
    값 분포(value_counts)를 각각 콘솔에 출력하고 딕셔너리로 모아 반환한다.

    Args:
        df: clean_data()를 거친 정제 완료 DataFrame.
    Returns:
        {컬럼명: value_counts 결과(Series)} 딕셔너리. generate_report()의 4절에서
        각 컬럼을 표로 변환해 report.md에 삽입한다.
    """
    print("\n=== 3-2) 범주형/메타데이터 컬럼 요약 ===")
    cat_cols = [
        "VendorID", "RatecodeID", "store_and_fwd_flag", "payment_type",
        "is_peak_hour", "has_surcharge", "is_late_night", "is_cost_effective",
    ]
    summaries = {}
    for col in _present_cols(df, cat_cols):
        vc = df[col].value_counts(dropna=False)  # dropna=False: 결측치(NaN)도 하나의 값처럼 개수를 센다
        print(f"[{col}]")
        print(vc.to_string())
        summaries[col] = vc
    if not summaries:
        print("  해당 컬럼 없음")
    return summaries


# ================================================================================================
# 4) 시각화 - Seaborn(정적) & Plotly(인터랙티브)
# ================================================================================================
def plot_seaborn_distribution(df: pd.DataFrame, out_path: str = os.path.join(OUTPUT_DIR, "dist_seaborn.png")) -> None:
    """
    [분포] cost_per_mile(마일당 실질 비용) 분포를 히스토그램 + KDE 곡선으로 그리고,
    중앙값 위치를 세로선으로 표시해 PNG로 저장한다. 반환값 없음(파일 저장이 목적).

    Args:
        df: clean_data()를 거친 정제 완료 DataFrame.
        out_path: 저장할 PNG 경로.
    """
    print("\n=== 4-1) Seaborn 정적 차트 (분포) ===")
    try:
        fig, ax = plt.subplots(figsize=(9, 6))
        # histplot: 히스토그램(막대) + kde=True로 부드러운 밀도 곡선을 함께 표시
        sns.histplot(df["cost_per_mile"], bins=60, kde=True, color="#2A9D8F", ax=ax)
        median = df["cost_per_mile"].median()
        ax.axvline(median, color="#E76F51", linestyle="--", linewidth=1.5, label=f"중앙값 ${median:.2f}/mile")
        ax.set_title("마일당 실질 비용(cost_per_mile) 분포", fontsize=13, color="#264653", fontweight="bold")
        ax.set_xlabel("마일당 비용 ($/mile)")
        ax.set_ylabel("건수")
        ax.legend()
        fig.tight_layout()
        fig.savefig(out_path, dpi=120)
        plt.close(fig)
        print(f"저장 완료: {out_path}")
    except Exception as e:
        raise RuntimeError("Seaborn 분포 차트 생성 실패") from e


def plot_distance_vs_cost(
    df: pd.DataFrame,
    h3_table: pd.DataFrame,
    out_path: str = os.path.join(OUTPUT_DIR, "eda_distance_vs_cost.png"),
) -> None:
    """
    [관계 탐색] 이동 거리 vs 마일당 비용 산점도(표본 2만 건)에, H3에서 이미 계산한
    거리 5분위 구간 평균을 추세선으로 겹쳐 그려 PNG로 저장한다.

    Args:
        df: clean_data()를 거친 정제 완료 DataFrame.
        h3_table: analyze_h3_distance_buckets()의 반환값 (반드시 시각화보다 먼저 계산돼야 함).
        out_path: 저장할 PNG 경로.
    """
    print("\n=== 4-2) 이동 거리 vs 마일당 비용 ===")
    if h3_table is None or h3_table.empty:
        raise RuntimeError("거리-비용 차트에 필요한 가설 3 테이블이 비어 있음")
    try:
        # 전체 30만 점은 겹침만 늘리므로, 재현 가능한 표본 2만 건으로 시각적 추세만 확인한다.
        sample = df.sample(n=min(20_000, len(df)), random_state=RANDOM_STATE)
        fig, ax = plt.subplots(figsize=(9, 6))
        # alpha=0.12: 점을 반투명하게 그려 점이 몰린 밀집 구간을 눈으로 파악할 수 있게 함
        sns.scatterplot(
            data=sample, x="trip_distance", y="cost_per_mile",
            alpha=0.12, s=10, color="#2A9D8F", ax=ax,
        )
        # 희박한 장거리 데이터에 끌리는 다항 회귀 대신, H3에서 실제로 계산한 5분위 평균을 연결한다.
        ax.plot(
            h3_table["평균거리"], h3_table["평균마일당비용"],
            color="#E76F51", linewidth=2.5, marker="o", label="거리 5분위 평균",
        )
        ax.set_title("이동 거리와 마일당 비용의 관계", fontsize=13, color="#264653", fontweight="bold")
        ax.set_xlabel("이동 거리 (mile)")
        ax.set_ylabel("마일당 비용 ($/mile)")
        ax.legend()
        fig.tight_layout()
        fig.savefig(out_path, dpi=120)
        plt.close(fig)
        print(f"저장 완료: {out_path}")
    except Exception as e:
        raise RuntimeError("거리-비용 EDA 생성 실패") from e


def plot_peak_boxplot(
    df: pd.DataFrame,
    out_path: str = os.path.join(OUTPUT_DIR, "eda_peak_boxplot.png"),
) -> None:
    """
    [그룹비교] H1의 지정 피크 vs 기타 시간대, 두 그룹의 마일당 비용 분포를
    박스플롯으로 비교해 PNG로 저장한다.

    Args:
        df: clean_data()를 거친 정제 완료 DataFrame (is_peak_hour 컬럼 필요).
        out_path: 저장할 PNG 경로.
    """
    print("\n=== 4-3) 지정 피크 vs 기타 시간대 박스플롯 ===")
    try:
        plot_df = df[["is_peak_hour", "cost_per_mile"]].copy()
        plot_df["시간대"] = plot_df["is_peak_hour"].map({True: "지정 피크", False: "기타"})
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.boxplot(
            data=plot_df, x="시간대", y="cost_per_mile",
            order=["기타", "지정 피크"], hue="시간대",
            palette={"기타": "#2A9D8F", "지정 피크": "#E76F51"}, legend=False,
            showfliers=False,  # 극단점보다 두 집단의 중심과 범위 비교에 집중
            ax=ax,
        )
        ax.set_title("지정 피크·기타 시간대의 마일당 비용 비교", fontsize=13, color="#264653", fontweight="bold")
        ax.set_xlabel("시간대 구분")
        ax.set_ylabel("마일당 비용 ($/mile)")
        fig.tight_layout()
        fig.savefig(out_path, dpi=120)
        plt.close(fig)
        print(f"저장 완료: {out_path}")
    except Exception as e:
        raise RuntimeError("지정 피크 시간대 boxplot 생성 실패") from e


def plot_seaborn_boxplot_surcharge(df: pd.DataFrame, out_path: str = os.path.join(OUTPUT_DIR, "box_surcharge_seaborn.png")) -> None:
    """
    [그룹비교] H2의 부대비용 유무별 cost_per_mile 박스플롯.
    t-test는 "평균의 차이"만 말해주므로, 두 그룹의 분포 전체(중앙값·사분위·퍼짐)가
    실제로 벌어져 있는지를 눈으로 확인시켜주는 보조 시각화.

    Args:
        df: clean_data()를 거친 정제 완료 DataFrame (has_surcharge 컬럼 필요).
        out_path: 저장할 PNG 경로.
    """
    print("\n=== 4-4) 부대비용 유무별 분포 박스플롯 ===")
    try:
        plot_df = df[["has_surcharge", "cost_per_mile"]].copy()
        plot_df["부대비용"] = plot_df["has_surcharge"].map({True: "있음", False: "없음"})
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.boxplot(
            data=plot_df, x="부대비용", y="cost_per_mile", hue="부대비용",
            order=["없음", "있음"], palette={"없음": "#2A9D8F", "있음": "#E76F51"}, legend=False, ax=ax,
        )
        ax.set_title("부대비용 유무별 마일당 비용 분포 (가설 2)", fontsize=13, color="#264653", fontweight="bold")
        ax.set_xlabel("부대비용(공항수수료·혼잡통행료·CBD혼잡료) 부과 여부")
        ax.set_ylabel("마일당 비용 ($/mile)")
        fig.tight_layout()
        fig.savefig(out_path, dpi=120)
        plt.close(fig)
        print(f"저장 완료: {out_path}")
    except Exception as e:
        raise RuntimeError("부대비용 boxplot 생성 실패") from e


def plot_distance_bucket_ratio(h3_table: pd.DataFrame, out_path: str = os.path.join(OUTPUT_DIR, "h3_distance_bucket.png")) -> None:
    """
    [가설 3] 거리 5분위 구간별 가성비 비율을 막대그래프로 표시한다.
    표의 숫자 나열보다, 짧은 거리에서 급격히 낮고 거리가 늘수록 완만하게 높아지는
    비선형 패턴이 한눈에 보이도록 하기 위한 시각화.

    Args:
        h3_table: analyze_h3_distance_buckets()의 반환값.
        out_path: 저장할 PNG 경로.
    """
    print("\n=== 4-5) 거리 구간별 가성비 비율 (가설 3) ===")
    if h3_table is None or h3_table.empty:
        raise RuntimeError("거리 구간 차트에 필요한 가설 3 테이블이 비어 있음")
    try:
        # 각 구간(pd.Interval)을 "0.2~1.1mi" 같은 읽기 쉬운 문자열 라벨로 변환
        labels = [f"{iv.left:.1f}~{iv.right:.1f}mi" for iv in h3_table.index]
        ratios = h3_table["가성비비율"] * 100
        fig, ax = plt.subplots(figsize=(9, 6))
        bars = ax.bar(labels, ratios, color="#2A9D8F")
        for bar, v in zip(bars, ratios):
            ax.text(bar.get_x() + bar.get_width() / 2, v + 1, f"{v:.1f}%", ha="center", fontsize=10)
        ax.set_title("거리 구간(5분위)별 가성비 좋은 운행 비율 (가설 3)", fontsize=13, color="#264653", fontweight="bold")
        ax.set_xlabel("이동 거리 구간 (mile)")
        ax.set_ylabel("가성비 좋은 운행 비율 (%)")
        ax.set_ylim(0, 105)  # 0~105%로 y축을 고정해 막대 위 텍스트가 잘리지 않게 함
        fig.tight_layout()
        fig.savefig(out_path, dpi=120)
        plt.close(fig)
        print(f"저장 완료: {out_path}")
    except Exception as e:
        raise RuntimeError("거리 구간 차트 생성 실패") from e


def plot_weekday_hour_heatmap(
    df: pd.DataFrame,
    out_path: str = os.path.join(OUTPUT_DIR, "eda_weekday_hour_heatmap.png"),
) -> None:
    """
    [그룹비교] 요일(7) x 승차 시각(24) 조합별 평균 마일당 비용을 히트맵 한 장으로
    비교한다. 특정 요일-시간대 조합에 비용이 몰리는 패턴이 있는지 눈으로 확인하기 위함.

    Args:
        df: clean_data()를 거친 정제 완료 DataFrame.
        out_path: 저장할 PNG 경로.
    """
    print("\n=== 4-6) 요일 x 시간대 비용 히트맵 ===")
    try:
        weekday_names = {0: "월", 1: "화", 2: "수", 3: "목", 4: "금", 5: "토", 6: "일"}
        # pivot_table: 행=요일, 열=시각, 값=cost_per_mile 평균으로 2차원 표 생성
        heatmap_data = df.pivot_table(
            index="pickup_dow", columns="pickup_hour", values="cost_per_mile", aggfunc="mean",
        ).reindex(index=range(7), columns=range(24)).rename(index=weekday_names)  # 0~6, 0~23 전체를 항상 포함하도록 정렬
        fig, ax = plt.subplots(figsize=(14, 6))
        sns.heatmap(
            heatmap_data, cmap="YlOrRd", linewidths=0.2,  # 노랑->빨강 색상으로 값이 클수록 진하게 표시
            cbar_kws={"label": "평균 $/mile"}, ax=ax,
        )
        ax.set_title("요일·시간대별 평균 마일당 비용", fontsize=13, color="#264653", fontweight="bold")
        ax.set_xlabel("승차 시각 (시)")
        ax.set_ylabel("요일")
        fig.tight_layout()
        fig.savefig(out_path, dpi=120)
        plt.close(fig)
        print(f"저장 완료: {out_path}")
    except Exception as e:
        raise RuntimeError("요일-시간 히트맵 생성 실패") from e


def plot_plotly_group_comparison(df: pd.DataFrame, out_path: str = os.path.join(OUTPUT_DIR, "group_plotly.html")) -> None:
    """
    [인터랙티브 그룹비교] 승차 시각(0~23시)별 평균 마일당 비용을 막대그래프로 그리고,
    지정 피크/기타로 색을 구분해 가설 1을 시각적으로 보여준다. 확대/축소가 가능한
    HTML로 저장하며(정적 이미지가 아님), 반환값은 없다.

    Args:
        df: clean_data()를 거친 정제 완료 DataFrame.
        out_path: 저장할 HTML 경로.
    """
    print("\n=== 4-7) Plotly 인터랙티브 차트 (그룹비교) ===")
    try:
        hourly = df.groupby("pickup_hour", as_index=False)["cost_per_mile"].mean()
        hourly["구간"] = hourly["pickup_hour"].apply(lambda h: "지정 피크" if h in PEAK_HOURS else "기타")
        fig = px.bar(
            hourly, x="pickup_hour", y="cost_per_mile", color="구간",
            title="시간대별 평균 마일당 비용 (가설 1: 지정 피크 vs 기타)",
            labels={"pickup_hour": "승차 시각(시)", "cost_per_mile": "평균 마일당 비용($/mile)"},
            color_discrete_map={"지정 피크": "#E76F51", "기타": "#2A9D8F"},
            template="plotly_white",
        )
        fig.write_html(out_path)  # 브라우저에서 열어 확대/축소 등 상호작용이 가능한 HTML로 저장
        print(f"저장 완료: {out_path}")
    except Exception as e:
        raise RuntimeError("Plotly 차트 생성 실패") from e


# ================================================================================================
# 5) 상관계수
# ================================================================================================
def compute_correlation(df: pd.DataFrame):
    """
    주요 수치형 컬럼 간 상관계수 행렬을 계산한다.
    행렬만 덤프하면 "그래서 뭐가 중요한데?"가 안 보이므로, 핵심 지표(cost_per_mile)와
    상관이 강한 상위 변수를 뽑아 방향(양/음)까지 읽어주는 자동 해석 문장도 함께 생성한다.

    Args:
        df: clean_data()를 거친 정제 완료 DataFrame.
    Returns:
        (corr, highlights) 튜플. corr은 상관계수 DataFrame(plot_correlation_heatmap()
        입력), highlights는 "cost_per_mile ↔ X: +0.xx -> ..." 형식의 해석 문장 리스트
        (최대 3개, generate_report()의 5절에 그대로 삽입됨).
    """
    print("\n=== 5-1) 상관계수 ===")
    cols = _numeric_cols_present(df, NUMERIC_COLS)
    corr = df[cols].corr().round(2)  # 모든 숫자형 컬럼 쌍의 피어슨 상관계수 행렬
    print(corr.to_string())

    highlights = []
    if "cost_per_mile" in corr.columns:
        # cost_per_mile과의 상관계수만 뽑고, 자기 자신(상관계수=1)은 제외한 뒤
        # 절댓값 기준 상위 3개(양/음 관계없이 관련성이 강한 순) 변수를 선정
        top = corr["cost_per_mile"].drop("cost_per_mile").abs().nlargest(3)
        for col in top.index:
            v = corr.loc[col, "cost_per_mile"]  # 실제 부호가 있는 상관계수 값
            direction = "높아지는(양의 상관)" if v > 0 else "낮아지는(음의 상관)"
            highlights.append(f"cost_per_mile ↔ {col}: {v:+.2f} -> {col}이(가) 클수록 마일당 비용이 {direction} 경향")
        print("[핵심 상관관계 해석]")
        for h in highlights:
            print(f"  - {h}")
    return corr, highlights


def plot_correlation_heatmap(
    corr: pd.DataFrame,
    out_path: str = os.path.join(OUTPUT_DIR, "eda_correlation_heatmap.png"),
) -> None:
    """
    수치형 변수들의 상관계수와 방향을 색상(파랑=음, 빨강=양) + 숫자로 함께 표시한
    히트맵을 PNG로 저장한다. 반환값은 없다.

    Args:
        corr: compute_correlation()의 첫 번째 반환값(상관계수 DataFrame).
        out_path: 저장할 PNG 경로.
    """
    print("\n=== 5-2) 상관계수 히트맵 ===")
    if corr.empty:
        raise RuntimeError("상관계수 히트맵에 필요한 데이터가 비어 있음")
    try:
        fig, ax = plt.subplots(figsize=(15, 12))
        sns.heatmap(
            corr, annot=True, fmt=".2f", cmap="RdBu_r", vmin=-1, vmax=1, center=0,  # 파랑(음)~빨강(양), 0을 흰색 중심으로
            square=True, linewidths=0.4, cbar_kws={"label": "상관계수", "shrink": 0.8},
            annot_kws={"size": 7}, ax=ax,
        )
        ax.set_title("주요 수치형 변수 상관계수 히트맵", fontsize=14, color="#264653", fontweight="bold")
        ax.tick_params(axis="x", rotation=55, labelsize=8)  # 컬럼명이 길어서 45도 이상 회전시켜 겹침 방지
        ax.tick_params(axis="y", rotation=0, labelsize=8)
        fig.tight_layout()
        fig.savefig(out_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"저장 완료: {out_path}")
    except Exception as e:
        raise RuntimeError("상관계수 히트맵 생성 실패") from e


# ================================================================================================
# 6) 가설 검정 (H1·H2 t-test / H3·H4 그룹별 진단)
# ================================================================================================
def run_ttest_h1_peak_hours(df: pd.DataFrame) -> dict:
    """
    [가설 1] 지정 피크 시간대의 평균 비용이 기타 시간대보다 높은지 검정한다.
    "피크가 더 비싸다"는 방향성 있는 주장이므로, 양측검정이 아니라
    alternative="greater"로 단측검정을 수행한다.

    Args:
        df: clean_data()를 거친 정제 완료 DataFrame (is_peak_hour 컬럼 필요).
    Returns:
        peak_mean/offpeak_mean/t_stat/p_value/verdict를 담은 딕셔너리.
        generate_report()의 7절과 12절(최종 결론)에서 사용한다.
    """
    print("\n=== 6-1) t-test (H1): 지정 피크 vs 기타 시간대 마일당 비용 ===")
    try:
        peak = df.loc[df["is_peak_hour"], "cost_per_mile"]
        offpeak = df.loc[~df["is_peak_hour"], "cost_per_mile"]
        # equal_var=False: 두 그룹의 분산이 같다고 가정하지 않는 Welch's t-test (더 안전한 기본값)
        t_stat, p_value = scipy_stats.ttest_ind(peak, offpeak, equal_var=False, alternative="greater")
        verdict = ("귀무가설 기각 (지정 피크 시간대가 유의미하게 높음)" if p_value < 0.05
                   else "귀무가설을 기각하지 못함 (유의미한 차이를 확인하지 못함)")
        print(f"지정 피크 평균: ${peak.mean():.3f}/mile (n={len(peak):,}) / 기타 시간대 평균: ${offpeak.mean():.3f}/mile (n={len(offpeak):,})")
        print(f"t-statistic: {t_stat:.4f}, p-value(one-sided): {p_value:.4g}")
        print(f"해석 (α=0.05): {verdict}")
        return {
            "peak_mean": float(peak.mean()), "offpeak_mean": float(offpeak.mean()),
            "t_stat": float(t_stat), "p_value": float(p_value), "verdict": verdict,
        }
    except Exception as e:
        raise RuntimeError("t-test(H1) 수행 실패") from e


def run_ttest_h2_surcharge(df: pd.DataFrame) -> dict:
    """
    [가설 2] 부대비용(공항수수료·혼잡통행료·CBD혼잡료) 부과 여부에 따른 평균 비용 차이를 검정한다.
    "부대비용이 있으면 더 비싸다"는 방향성 있는 주장이므로 H1과 동일하게 단측검정.

    Args:
        df: clean_data()를 거친 정제 완료 DataFrame (has_surcharge 컬럼 필요).
    Returns:
        with_surcharge_mean/without_surcharge_mean/t_stat/p_value/verdict를 담은 딕셔너리.
        generate_report()의 8절과 12절(최종 결론)에서 사용한다.
    """
    print("\n=== 6-2) t-test (H2): 부대비용 유무별 마일당 비용 ===")
    try:
        with_sur = df.loc[df["has_surcharge"], "cost_per_mile"]
        without_sur = df.loc[~df["has_surcharge"], "cost_per_mile"]
        t_stat, p_value = scipy_stats.ttest_ind(with_sur, without_sur, equal_var=False, alternative="greater")
        verdict = ("귀무가설 기각 (부대비용 있는 운행이 유의미하게 높음)" if p_value < 0.05
                   else "귀무가설을 기각하지 못함 (유의미한 차이를 확인하지 못함)")
        print(f"부대비용 있음 평균: ${with_sur.mean():.3f}/mile (n={len(with_sur):,}) / "
              f"부대비용 없음 평균: ${without_sur.mean():.3f}/mile (n={len(without_sur):,})")
        print(f"t-statistic: {t_stat:.4f}, p-value(one-sided): {p_value:.4g}")
        print(f"해석 (α=0.05): {verdict}")
        return {
            "with_surcharge_mean": float(with_sur.mean()), "without_surcharge_mean": float(without_sur.mean()),
            "t_stat": float(t_stat), "p_value": float(p_value), "verdict": verdict,
        }
    except Exception as e:
        raise RuntimeError("t-test(H2) 수행 실패") from e


def analyze_h3_distance_buckets(df: pd.DataFrame, n_buckets: int = 5) -> pd.DataFrame:
    """
    [가설 3] 이동 거리와 가성비의 비선형 관계를 진단한다.
    trip_distance를 5분위(quintile)로 나눠 구간별 평균 비용·"가성비 좋음" 비율을 확인한다.
    -> 거리가 늘수록 비율이 선형이 아니라(예: 초단거리 구간에서 급격히 낮았다가
    중장거리에서 완만해지는 식으로) 변하는지를 표 하나로 직접 확인하는 방법.

    Args:
        df: clean_data()를 거친 정제 완료 DataFrame.
        n_buckets: 나눌 구간(분위) 수. 기본 5(quintile).
    Returns:
        구간별 평균거리/평균마일당비용/가성비비율/건수를 담은 DataFrame.
        plot_distance_vs_cost(), plot_distance_bucket_ratio(), generate_report()가
        모두 이 반환값을 그대로 사용하므로 main()에서 시각화보다 먼저 호출된다.
    """
    print("\n=== 6-3) 가설 3 진단: 거리 구간별 가성비 비율 ===")
    try:
        bucketed = df.copy()
        # pd.qcut: 데이터를 개수가 균등한(quantile 기준) n_buckets개 구간으로 나눔 (5분위 = quintile)
        bucketed["distance_bucket"] = pd.qcut(bucketed["trip_distance"], q=n_buckets, duplicates="drop")
        result = (
            bucketed.groupby("distance_bucket", observed=True)
            .agg(
                평균거리=("trip_distance", "mean"),
                평균마일당비용=("cost_per_mile", "mean"),
                가성비비율=("is_cost_effective", "mean"),  # 0/1 평균 = 가성비 좋은 운행의 비율
                건수=("is_cost_effective", "size"),
            )
            .round(3)
        )
        print(result.to_string())
        return result
    except Exception as e:
        raise RuntimeError("가설 3 진단 실패") from e


def analyze_h4_time_patterns(df: pd.DataFrame) -> pd.DataFrame:
    """
    [가설 4] 요일/심야 등 탑승 패턴이 가성비에 영향을 주는지 진단한다.
    is_weekend x is_late_night 조합별 "가성비 좋음" 비율을 비교한다.
    -> 특정 조합(예: 주말+심야)의 비율이 다른 조합보다 뚜렷하게 높으면
    해당 패턴이 가성비와 관련 있다고 해석한다.

    Args:
        df: clean_data()를 거친 정제 완료 DataFrame.
    Returns:
        (is_weekend, is_late_night) MultiIndex를 갖는, 조합별 가성비비율/건수 DataFrame.
        generate_report()의 10절·12절에서 idxmax()로 가장 비율이 높은 조합을 찾는 데 쓴다.
    """
    print("\n=== 6-4) 가설 4 진단: 주말/심야 조합별 가성비 비율 ===")
    try:
        # 두 개의 True/False 컬럼으로 동시에 그룹화 -> (주말여부, 심야여부) 4개 조합별 결과 생성
        result = (
            df.groupby(["is_weekend", "is_late_night"], observed=True)
            .agg(가성비비율=("is_cost_effective", "mean"), 건수=("is_cost_effective", "size"))
            .round(3)
        )
        print(result.to_string())
        return result
    except Exception as e:
        raise RuntimeError("가설 4 진단 실패") from e


# ================================================================================================
# 7) ML Pipeline
# ================================================================================================
def build_ml_pipeline(df: pd.DataFrame, model_path: str = os.path.join(OUTPUT_DIR, "cost_effective_model.joblib")) -> dict:
    """
    "가성비 좋은 탑승(is_cost_effective)"을 예측하는 이진분류 파이프라인.
    ColumnTransformer로 전처리를 구성하고 RandomForestClassifier를 사용한다.
    (트리 기반 모델이 가설 3이 다루는 "거리와 가성비의 비선형 관계"를 선형모델보다
    자연스럽게 학습할 수 있기 때문. 가설 3·4 자체의 검증은 위의
    analyze_h3_distance_buckets()/analyze_h4_time_patterns() 그룹별 비율 테이블로 하고,
    여기서는 Accuracy/F1 등 분류 성능 지표만 확인한다.)

    주의: trip_distance/trip_duration_min은 "운행 완료 후" 확정되는 값이므로,
    이 모델은 탑승 전 예측이 아니라 운행 기록 기반의 사후 분류다.

    Args:
        df: clean_data()를 거친 정제 완료 DataFrame.
        model_path: 학습된 Pipeline을 joblib으로 저장할 경로.
    Returns:
        accuracy/f1/n_train/n_test/zone_coverage/n_zones_total/top_importance
        (피처 중요도 상위 10, Series)/classification_df(클래스별 precision/recall/f1/support,
        DataFrame)를 담은 딕셔너리. plot_ml_performance_table()과 generate_report()가 사용한다.
    """
    print("\n=== 7) ML Pipeline: 가성비 좋은 탑승 여부 분류 ===")
    try:
        data = df.copy()

        # PULocationID(약 260개 구역)를 그대로 원-핫하면 차원이 과도하게 커지므로
        # 등장 빈도 상위 TOP_N_ZONES개만 개별 범주로 남기고 나머지는 'OTHER'로 묶는다.
        zone_counts = data["PULocationID"].value_counts()
        top_n_zones = zone_counts.nlargest(TOP_N_ZONES)  # 동일 계산을 두 번 하지 않도록 한 번만 수행해서 재사용
        top_zones = top_n_zones.index
        coverage = top_n_zones.sum() / zone_counts.sum()
        print(f"[안내] 상위 {TOP_N_ZONES}개 pickup 구역이 전체 트립의 {coverage:.1%}를 커버 "
              f"(전체 구역 수: {zone_counts.shape[0]}개, 나머지는 'OTHER'로 묶임)")
        # 상위 구역이면 원래 ID, 아니면 'OTHER' 문자열로 치환 (차원 축소)
        data["pickup_zone"] = data["PULocationID"].where(data["PULocationID"].isin(top_zones), "OTHER").astype(str)

        if "RatecodeID" in data.columns:
            # 숫자 코드를 사람이 읽을 수 있는 한글 라벨로 변환, 매핑에 없는 값은 "기타"로 처리
            data["ratecode_label"] = data["RatecodeID"].map(RATECODE_LABELS).fillna("기타")

        num_features = ["trip_distance", "trip_duration_min", "passenger_count", "pickup_hour"]
        cat_features = _present_cols(data, ["pickup_zone", "ratecode_label", "is_weekend", "is_late_night", "is_peak_hour", "has_surcharge"])

        X = data[num_features + cat_features]
        y = data["is_cost_effective"]

        # stratify=y로 학습/테스트 세트의 클래스 비율을 원본과 동일하게 유지한다.
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
        )

        preprocessor = ColumnTransformer(transformers=[
            ("num", "passthrough", num_features),  # 트리 기반 모델은 스케일 차이에 영향받지 않아 별도 스케일링 불필요 -> 그대로 통과
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_features),  # 범주형을 0/1 벡터로 변환, 테스트에만 나오는 범주가 있어도 에러 없이 처리
        ])
        model = Pipeline([
            ("preprocessor", preprocessor),
            ("classifier", RandomForestClassifier(  # 여러 결정 트리를 앙상블하는 랜덤포레스트 분류기
                n_estimators=200, max_depth=8, random_state=RANDOM_STATE, n_jobs=-1  # n_jobs=-1: 가능한 모든 CPU 코어 사용
            )),
        ])

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        target_names = ["가성비 나쁨", "가성비 좋음"]
        print(f"정확도(Accuracy): {acc:.4f}")
        print(f"F1-score: {f1:.4f}")
        print(classification_report(y_test, y_pred, target_names=target_names))

        # report.md에도 클래스별 precision/recall/f1/support를 표로 남기기 위해
        # output_dict=True로 한 번 더 계산해 DataFrame으로 변환해둔다.
        # (콘솔 출력용 텍스트와 별개로, 리포트에 넣을 수치 데이터를 따로 확보하는 용도)
        report_dict = classification_report(
            y_test, y_pred, target_names=target_names, output_dict=True
        )
        classification_df = pd.DataFrame(report_dict).T.round(4)

        # Feature Importance로 분류 결과와 관련성이 큰 입력 특성을 확인한다.
        importances = model.named_steps["classifier"].feature_importances_
        feat_names = model.named_steps["preprocessor"].get_feature_names_out()  # 전처리 후 실제 피처 이름들(원-핫 후 이름 포함)
        # ColumnTransformer가 붙이는 "num__"/"cat__" 접두어는 가독성을 해치므로 제거
        feat_names = [n.split("__", 1)[-1] for n in feat_names]
        top_importance = pd.Series(importances, index=feat_names).nlargest(10).round(4)
        print("[Feature Importance 상위 10] (가성비 예측에 많이 기여한 피처 순)")
        print(top_importance.to_string())

        joblib.dump(model, model_path)
        print(f"모델 저장 완료: {model_path}")

        return {
            "accuracy": float(acc), "f1": float(f1),
            "n_train": len(X_train), "n_test": len(X_test),
            "zone_coverage": float(coverage), "n_zones_total": int(zone_counts.shape[0]),
            "top_importance": top_importance,
            "classification_df": classification_df,
        }
    except Exception as e:
        raise RuntimeError("ML Pipeline 실행 실패") from e


def plot_ml_performance_table(
    ml_result: dict,
    out_path: str = os.path.join(OUTPUT_DIR, "ml_performance_table.png"),
) -> None:
    """
    분류 모델의 핵심 성능 지표(Accuracy/F1)와 학습·평가 데이터 건수를 발표용
    표 이미지(PNG)로 저장한다. 반환값은 없다.

    Args:
        ml_result: build_ml_pipeline()의 반환값.
        out_path: 저장할 PNG 경로.
    """
    print("\n=== 7-1) ML 성능 결과표 ===")
    if not ml_result:
        raise RuntimeError("ML 성능표에 필요한 결과가 비어 있음")

    # 표에 넣을 4개 행(지표명, 값, 설명)을 미리 정의
    rows = [
        ["Accuracy", f"{ml_result['accuracy']:.4f}", "전체 예측 중 올바르게 분류한 비율"],
        ["F1-score", f"{ml_result['f1']:.4f}", "정밀도와 재현율의 조화평균"],
        ["학습 데이터", f"{ml_result['n_train']:,}건", "모델 학습에 사용한 데이터"],
        ["테스트 데이터", f"{ml_result['n_test']:,}건", "성능 평가에 사용한 데이터"],
    ]

    try:
        fig, ax = plt.subplots(figsize=(11, 4.4))
        ax.axis("off")
        table = ax.table(
            cellText=rows, colLabels=["성능 지표", "결과", "의미"],
            cellLoc="center", loc="center", colWidths=[0.22, 0.20, 0.58],
        )
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1, 1.9)

        # 결과 열을 강조해 발표 중 Accuracy와 F1을 빠르게 확인할 수 있게 한다.
        for (row, col), cell in table.get_celld().items():
            cell.set_edgecolor("#D9E2E7")
            if row == 0:                     # 헤더 행
                cell.set_facecolor("#264653")
                cell.get_text().set_color("white")
                cell.get_text().set_weight("bold")
            elif row % 2 == 0:                # 짝수 행 줄무늬
                cell.set_facecolor("#F1F7F6")
            if row > 0 and col == 1:          # "결과" 열(숫자 값)만 강조 색상 적용
                cell.get_text().set_weight("bold")
                cell.get_text().set_color("#E76F51")

        ax.set_title("Random Forest 분류모델 성능 결과", fontsize=15, color="#264653", pad=18)
        fig.tight_layout()
        fig.savefig(out_path, dpi=160, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        print(f"저장 완료: {out_path}")
    except Exception as e:
        raise RuntimeError("ML 성능표 이미지 생성 실패") from e


# ================================================================================================
# 8) report.md 자동 생성
# ================================================================================================
def generate_report(load_result: dict, clean_summary: dict, desc_stats: pd.DataFrame,
                     cat_summaries: dict, corr: pd.DataFrame, corr_highlights: list,
                     h1_result: dict, h2_result: dict,
                     h3_table: pd.DataFrame, h4_table: pd.DataFrame, ml_result: dict,
                     out_path: str = os.path.join(OUTPUT_DIR, "report.md")) -> None:
    """
    앞선 모든 단계(로딩 비교, 정제, EDA, 시각화, 상관계수, H1~H4, ML)의 결과를 받아
    report.md 한 파일로 자동 정리한다 (자동화 요구사항 대응). 콘솔에는 출력하지 않고
    바로 파일로 저장하며, 12개 섹션(로딩 비교 -> 정제 -> 기술통계 -> 범주형 요약 ->
    상관계수 -> 시각화 모음 -> H1 -> H2 -> H3 -> H4 -> ML -> 최종 결론) 순서로 구성된다.
    이 함수 자체는 새로운 계산을 하지 않고, 각 단계 함수가 반환한 결과를 마크다운
    문자열로 옮겨 적는 역할만 한다.

    Args:
        load_result, clean_summary, desc_stats, cat_summaries, corr, corr_highlights,
        h1_result, h2_result, h3_table, h4_table, ml_result: 각각 load_with_pandas_and_polars(),
        clean_data(), basic_eda(), categorical_summary(), compute_correlation(),
        run_ttest_h1_peak_hours(), run_ttest_h2_surcharge(), analyze_h3_distance_buckets(),
        analyze_h4_time_patterns(), build_ml_pipeline()의 반환값을 그대로 전달받는다.
        out_path: 저장할 report.md 경로.
    """
    print("\n=== 8) report.md 자동 생성 ===")

    # 마크다운 문자열을 한 줄씩 리스트에 쌓았다가, 마지막에 "\n"으로 합쳐 파일로 저장하는 방식
    lines = ["# NYC Yellow Taxi (2026-05) - 가성비 좋은 택시 탑승 조건 분석 리포트", ""]
    lines.append(f"- 생성 시각: {datetime.now():%Y-%m-%d %H:%M:%S}")
    lines.append(f"- 원본 데이터: {DATA_URL}")
    lines.append("- 핵심 지표: cost_per_mile = total_amount / trip_distance")
    lines.append("")

    # --- 1. 로딩 비교 ---
    lines.append("## 1. 데이터 로딩 비교 (Pandas vs Polars)")
    p = load_result.get("pandas") or {}
    lines.append(f"- Pandas: shape={p.get('shape')}, 로딩 {p.get('seconds', 0):.2f}s, 메모리 {p.get('memory_mb', 0):.1f}MB")
    pol = load_result["polars"]
    lines.append(f"- Polars: shape={pol.get('shape')}, 로딩 {pol.get('seconds', 0):.2f}s, 메모리 {pol.get('memory_mb', 0):.1f}MB")
    lines.append(f"- 두 결과 shape 일치 여부: {load_result.get('shapes_match')}")
    lines.append("")

    # --- 2. 정제 요약 ---
    lines.append("## 2. 결측치·중복·이상치 처리")
    lines.append(f"- 원본 행 수: {clean_summary.get('raw_rows', 0):,}")
    na_counts = clean_summary.get("na_counts") or {}
    if na_counts:
        na_df = pd.DataFrame.from_dict(na_counts, orient="index", columns=["결측치 개수"])
        na_df.index.name = "컬럼"
        lines.append("- 컬럼별 결측치 개수 (isnull().sum()):")
        lines.append(_df_to_md(na_df))
    else:
        lines.append("- 컬럼별 결측치: 없음")
    lines.append(f"- 중복 제거: {clean_summary.get('duplicates_removed', 0):,}건")
    lines.append(f"- 비정상값 제외: {clean_summary.get('invalid_rows_removed', 0):,}건")
    lower, upper = clean_summary.get("cpm_bounds", (0, 0))
    lines.append(f"- cost_per_mile IQR 이상치 제외: {clean_summary.get('cost_per_mile_outliers_removed', 0):,}건 "
                  f"(정상범위 {lower:.2f} ~ {upper:.2f} $/mile)")
    lines.append("  - 1.5xIQR 공식상 하한이 음수로 계산되지만 마일당 비용은 음수가 될 수 없어 하한을 0으로 보정 "
                  "-> 실질적으로는 상한 초과 극단치(초단거리 고액 운행 등)만 제거됨")
    lines.append(f"- 마일당 비용 중앙값(is_cost_effective 기준): ${clean_summary.get('median_cost_per_mile', 0):.2f}/mile")
    lines.append("  - 가성비 라벨을 중앙값 분할(median split)로 정한 이유: 임의의 절대 임계값을 피하고, "
                  "클래스가 자동으로 50:50 균형을 이뤄 분류 모델 학습에 유리하기 때문")
    lines.append(f"- 최종 행 수: {clean_summary.get('clean_rows', 0):,}")
    lines.append("")

    # --- 3. 기술통계 ---
    lines.append("## 3. 기술통계")
    lines.append(_df_to_md(desc_stats))
    lines.append("")

    # --- 4. 범주형 요약 ---
    lines.append("## 4. 범주형/메타데이터 컬럼 요약")
    if cat_summaries:
        for col, vc in cat_summaries.items():
            vc_df = vc.rename_axis(col).reset_index(name="건수")
            lines.append(f"- **{col}**")
            lines.append(_df_to_md(vc_df))
    else:
        lines.append("- 해당 컬럼 없음")
    lines.append("")

    # --- 5. 상관계수 ---
    lines.append("## 5. 상관계수")
    lines.append(_df_to_md(corr))
    if corr_highlights:
        lines.append("")
        lines.append("핵심 해석:")
        for h in corr_highlights:
            lines.append(f"- {h}")
    lines.append("")

    # --- 6. 시각화 모음 (각 이미지 파일을 마크다운 이미지 문법으로 삽입) ---
    lines.append("## 6. 시각화")
    lines.append("### 6-1. 핵심 변수 기술통계표")
    lines.append("콘솔과 보고서에 사용한 기술통계를 발표용 표 이미지로 정리.")
    lines.append("")
    lines.append("![핵심 변수 기술통계표](eda_descriptive_stats_table.png)")
    lines.append("")
    lines.append("### 6-2. 마일당 비용 분포 (Seaborn)")
    lines.append("핵심 지표 cost_per_mile의 분포 형태와 중앙값(가성비 기준선) 위치를 확인.")
    lines.append("")
    lines.append("![마일당 비용 분포](dist_seaborn.png)")
    lines.append("")
    lines.append("### 6-3. 이동 거리와 마일당 비용 관계 (Seaborn)")
    lines.append("고정 표본 2만 건 산점도와 H3 거리 5분위별 실제 평균선으로 관계를 탐색.")
    lines.append("")
    lines.append("![이동 거리와 마일당 비용 관계](eda_distance_vs_cost.png)")
    lines.append("")
    lines.append("### 6-4. 지정 피크·기타 시간대 분포 박스플롯 (Seaborn)")
    lines.append("가설 1의 두 집단에서 중앙값과 사분위 범위가 어떻게 다른지 확인.")
    lines.append("")
    lines.append("![지정 피크·기타 시간대 박스플롯](eda_peak_boxplot.png)")
    lines.append("")
    lines.append("### 6-5. 부대비용 유무별 분포 박스플롯 (Seaborn)")
    lines.append("가설 2의 t-test는 평균 차이만 보여주므로, 두 그룹의 분포 전체가 실제로 벌어져 있는지를 박스플롯으로 확인.")
    lines.append("")
    lines.append("![부대비용 유무별 박스플롯](box_surcharge_seaborn.png)")
    lines.append("")
    lines.append("### 6-6. 거리 구간별 가성비 비율 (가설 3)")
    lines.append("거리 5분위 구간별 가성비 좋은 운행 비율 -> 거리에 따라 비율이 비선형적으로 변하는 패턴을 확인.")
    lines.append("")
    lines.append("![거리 구간별 가성비 비율](h3_distance_bucket.png)")
    lines.append("")
    lines.append("### 6-7. 요일·시간대별 평균 마일당 비용")
    lines.append("요일과 24시간 조합의 평균 비용 패턴을 한 화면에서 비교.")
    lines.append("")
    lines.append("![요일·시간대별 평균 비용](eda_weekday_hour_heatmap.png)")
    lines.append("")
    lines.append("### 6-8. 주요 수치형 변수 상관계수")
    lines.append("상관계수의 크기와 방향을 색상과 숫자로 함께 비교.")
    lines.append("")
    lines.append("![상관계수 히트맵](eda_correlation_heatmap.png)")
    lines.append("")
    lines.append("### 6-9. 시간대별 평균 마일당 비용 (Plotly 인터랙티브)")
    lines.append("- `group_plotly.html`에서 지정 피크·기타 시간대의 평균 마일당 비용을 비교")
    lines.append("")

    # --- 7. H1 ---
    lines.append("## 7. 가설 1 - t-test (지정 피크 vs 기타 시간대 마일당 비용)")
    lines.append("- 집단 정의: 요일 구분 없이 08~09시와 18~20시를 지정 피크 시간대로 분류하므로 주말도 포함")
    lines.append(f"- 지정 피크 평균: ${h1_result['peak_mean']:.3f}/mile / 기타 시간대 평균: ${h1_result['offpeak_mean']:.3f}/mile")
    lines.append(f"- t={h1_result['t_stat']:.4f}, p={h1_result['p_value']:.4g} (one-sided)")
    lines.append(f"- 결론: {h1_result['verdict']}")
    lines.append("")

    # --- 8. H2 ---
    lines.append("## 8. 가설 2 - t-test (부대비용 유무별 마일당 비용)")
    lines.append(f"- 부대비용 있음 평균: ${h2_result['with_surcharge_mean']:.3f}/mile / "
                  f"부대비용 없음 평균: ${h2_result['without_surcharge_mean']:.3f}/mile")
    lines.append(f"- t={h2_result['t_stat']:.4f}, p={h2_result['p_value']:.4g} (one-sided)")
    lines.append(f"- 결론: {h2_result['verdict']}")
    lines.append(f"- 해석 한계: 요금 컬럼 결측 {clean_summary.get('surcharge_missing_rows', 0):,}건 중 "
                  f"{clean_summary.get('surcharge_missing_as_no_rows', 0):,}건은 현재 비교식에서 '부대비용 없음'으로 분류됨")
    lines.append("")

    # --- 9. H3 ---
    lines.append("## 9. 가설 3 - 거리 구간별 가성비 비율")
    lines.append(_df_to_md(h3_table))
    lines.append("- 비율이 구간마다 일정하게 증가/감소하지 않고 특정 구간에서 꺾이면 비선형 관계로 해석")
    lines.append("- **해석의 한계**: 장거리일수록 고정비가 분산되어 마일당 비용이 낮아질 수 있지만 총지출은 더 크며, "
                  "100마일 초과 운행을 제외했으므로 모든 장거리 운행으로 일반화할 수 없음")
    lines.append("")

    # --- 10. H4 ---
    lines.append("## 10. 가설 4 - 주말/심야 조합별 가성비 비율")
    lines.append(_df_to_md(h4_table))
    lines.append("- 집단별 관련성을 비교한 관찰 결과이며 혼잡 감소 같은 원인을 직접 검증한 것은 아님")
    lines.append("")

    # --- 11. ML ---
    lines.append("## 11. ML Pipeline (가성비 좋은 탑승 여부 분류)")
    lines.append(f"- 학습/테스트 데이터 수: {ml_result['n_train']:,} / {ml_result['n_test']:,}")
    lines.append(
        f"- pickup_zone 커버리지: 상위 {TOP_N_ZONES}개 구역이 전체 {ml_result['n_zones_total']}개 구역 중 "
        f"트립의 {ml_result['zone_coverage']:.1%}를 차지 (나머지는 OTHER로 통합)"
    )
    lines.append(f"- Accuracy: {ml_result['accuracy']:.4f}")
    lines.append(f"- F1-score: {ml_result['f1']:.4f}")
    lines.append("- 저장된 모델: `cost_effective_model.joblib`")
    lines.append("- 실제 운행거리와 운행시간을 포함한 운행 완료 후 기록 기반 분류이며, 탑승 전 예측 성능을 뜻하지 않음")
    lines.append("")
    lines.append("![Random Forest 성능 결과표](ml_performance_table.png)")
    classification_df = ml_result.get("classification_df")
    if classification_df is not None and not classification_df.empty:
        lines.append("")
        lines.append("### 클래스별 성능 (Precision / Recall / F1 / Support)")
        lines.append("`classification_report()`의 결과를 표로 남긴 것 -> Accuracy/F1 두 숫자만으로는 "
                      "안 보이는 클래스별(가성비 좋음/나쁨) 세부 성능을 확인할 수 있다.")
        cls_df = classification_df.rename_axis("구분").reset_index()
        lines.append(_df_to_md(cls_df))
    top_imp = ml_result.get("top_importance")
    if top_imp is not None and len(top_imp) > 0:
        lines.append("")
        lines.append("### Feature Importance 상위 10 (분류 결과와 관련성이 큰 피처 순)")
        imp_df = top_imp.rename_axis("피처").reset_index(name="중요도")
        lines.append(_df_to_md(imp_df))
    lines.append("")

    # --- 12. 최종 결론 (자동 요약) ---
    lines.append("## 12. 최종 결론 (자동 생성)")
    diff1 = h1_result["peak_mean"] - h1_result["offpeak_mean"]
    lines.append(f"- **[H1 지정 피크 시간대]** 지정 피크가 기타 시간대보다 마일당 평균 ${diff1:.2f} 높게 관찰됨 "
                  f"(p={h1_result['p_value']:.3g}) -> {h1_result['verdict']}")
    diff2 = h2_result["with_surcharge_mean"] - h2_result["without_surcharge_mean"]
    lines.append(f"- **[H2 부대비용]** 부대비용 있는 운행이 마일당 평균 ${diff2:.2f} 높게 관찰됨 "
                  f"(p={h2_result['p_value']:.3g}) -> {h2_result['verdict']}")
    first_ratio = h3_table["가성비비율"].iloc[0]
    last_ratio = h3_table["가성비비율"].iloc[-1]
    lines.append(f"- **[H3 이동거리]** 최단거리 구간의 가성비 비율 {first_ratio:.1%} vs "
                  f"최장거리 구간 {last_ratio:.1%}로 거리 구간과 가성비의 관련성이 관찰됨")
    best_idx = h4_table["가성비비율"].idxmax()  # 4개 조합 중 가성비 비율이 가장 높은 조합의 (주말?, 심야?) 인덱스
    best_ratio = h4_table["가성비비율"].max()
    weekend_label = "주말" if best_idx[0] else "평일"
    night_label = "심야" if best_idx[1] else "주간"
    lines.append(f"- **[H4 탑승 패턴]** 표본에서 가성비 비율이 가장 높은 조합은 {weekend_label}x{night_label} "
                  f"({best_ratio:.1%})였으나 원인이나 인과관계는 검증하지 않음")
    lines.append(f"- **[ML]** 운행 완료 후 기록 특성으로 가성비 여부를 Accuracy {ml_result['accuracy']:.1%} / "
                  f"F1 {ml_result['f1']:.1%}로 분류함")
    lines.append("")
    lines.append("**종합**: 이 표본에서는 지정 피크 여부, 부대비용, 이동 거리와 마일당 비용 간 관련성이 관찰됐다. "
                  "관찰 자료의 비교 결과이므로 특정 조건의 이용을 권고하거나 인과관계로 해석할 수는 없다.")
    lines.append("")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"저장 완료: {out_path}")


# ================================================================================================
# 9) 메인 실행 흐름
# ================================================================================================
def main() -> None:
    """
    1) 다운로드/로딩 비교 -> 2) 정제 -> 3) EDA -> 4) 시각화 -> 5) 상관계수 ->
    6) 가설 검정(H1~H4) -> 7) ML Pipeline -> 8) report.md 생성 순서로 전체 파이프라인을 실행한다.
    어느 단계에서든 예외가 발생하면 한 곳(아래 except)에서 잡아 사용자 친화적 메시지만
    출력하고 종료 코드 1로 종료한다 (스택트레이스 대신 원인 요약만 보여주기 위함).
    """
    try:
        ensure_output_dir()

        # 1) 다운로드 & 로딩 비교
        raw_path = download_raw_data()
        pdf, load_result = load_with_pandas_and_polars(raw_path)

        # 월간 전체 데이터는 규모가 크므로 실습 편의를 위해 일부만 랜덤 샘플링해서 이후 단계에 사용
        if SAMPLE_N and len(pdf) > SAMPLE_N:
            pdf = pdf.sample(n=SAMPLE_N, random_state=RANDOM_STATE)
            print(f"[안내] 실습 편의를 위해 {SAMPLE_N:,}행으로 랜덤 샘플링")

        # 2) 정제 & 파생 컬럼
        clean_df, clean_summary = clean_data(pdf)

        # 3) 기본 EDA
        desc_stats = basic_eda(clean_df)
        plot_descriptive_stats_table(desc_stats)
        cat_summaries = categorical_summary(clean_df)

        # H3 표는 여러 차트(6-3 거리-비용 관계, 6-6 거리 구간 막대)가 함께 쓰므로 시각화보다 먼저 계산
        h3_table = analyze_h3_distance_buckets(clean_df)

        # 4) 시각화
        plot_seaborn_distribution(clean_df)
        plot_distance_vs_cost(clean_df, h3_table)
        plot_peak_boxplot(clean_df)
        plot_seaborn_boxplot_surcharge(clean_df)
        plot_distance_bucket_ratio(h3_table)
        plot_weekday_hour_heatmap(clean_df)
        plot_plotly_group_comparison(clean_df)

        # 5) 상관계수
        corr, corr_highlights = compute_correlation(clean_df)
        plot_correlation_heatmap(corr)

        # 6) 가설 검정
        h1_result = run_ttest_h1_peak_hours(clean_df)
        h2_result = run_ttest_h2_surcharge(clean_df)
        h4_table = analyze_h4_time_patterns(clean_df)

        # 7) ML Pipeline
        ml_result = build_ml_pipeline(clean_df)
        plot_ml_performance_table(ml_result)

        # 8) 리포트 자동 생성
        generate_report(load_result, clean_summary, desc_stats, cat_summaries, corr, corr_highlights,
                         h1_result, h2_result, h3_table, h4_table, ml_result)

        print("\n모든 단계 완료. output/ 폴더를 확인하세요.")
    except Exception as e:
        # 어느 단계에서 터지든 여기서 한 번에 잡아 메시지 출력 후 종료
        # -> 스택트레이스 대신 사용자 친화적 메시지만 노출
        print(f"[치명적 오류] 프로그램 실행 중단: {e}")
        sys.exit(1)  # 종료 코드 1로 비정상 종료 처리 (셸 스크립트/CI에서 실패로 감지 가능)


if __name__ == "__main__":
    main()
