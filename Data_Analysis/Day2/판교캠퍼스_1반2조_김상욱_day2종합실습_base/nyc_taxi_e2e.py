"""
[Day 2 종합 실습] End2End 데이터 분석 프로젝트 - NYC Yellow Taxi (2026-05)
=========================================================================

팀 선택 데이터셋: NYC Yellow Taxi Trip Data (2026-05, parquet)
원본 URL: https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2026-05.parquet

< 실습 요구사항 대응표 >
  1) 데이터 준비 : Pandas + Polars 양쪽으로 로딩해서 결과 비교, 결측치(컬럼별 개수 포함)·중복 처리, 기본 EDA
  2) 시각화      : Seaborn 정적 차트(분포) 1개 + Plotly 인터랙티브 차트(그룹비교) 1개, 제목·축 레이블 포함
  3) 통계 분석    : 기술통계(평균·표준편차·분위수), 상관계수, t-test(주중 vs 주말 운임) + p-value 해석,
                    + 카이제곱 검정(러시아워 여부 vs 고액 팁 여부) - ML Pipeline이 쓰는 피처의 타당성 검증용으로 추가
  4) ML Pipeline : ColumnTransformer + Pipeline(전처리 + 분류모델), 평가지표(정확도·F1) 출력, joblib 저장
  5) 자동화       : 위 모든 결과를 report.md 한 파일로 자동 생성

< ML 타겟 선정 이유 >
- 뉴욕 택시 데이터는 "현금 결제"의 경우 tip_amount가 항상 0으로 기록되어(과세 시스템 특성상
  미터기에 기록이 안 됨) 팁 유무 자체를 예측하는 건 의미가 없음
- 그래서 "신용카드 결제 건"으로 한정하고, 운임 대비 팁 비율(tip_pct)이 중앙값 이상인지
  (= 평소보다 팁을 후하게 준 승객인지)를 이진분류 타겟으로 사용 -> 클래스 균형도 자연스럽게 맞음

산출물은 스크립트 실행 위치 기준 ./output/ 폴더에 저장
(원본 캐시 parquet, dist_seaborn.png, group_plotly.html, tip_model.joblib, report.md)
"""

import logging
import os
import sys
import time
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")  # 화면 출력 환경이 없어도 파일로 저장 가능하도록
import matplotlib.pyplot as plt
from matplotlib import font_manager

# 대부분의 한글 폰트는 별도 Bold 서체가 없어서 fontweight="bold" 지정 시 matplotlib이
# "findfont: Failed to find font weight bold..." 경고를 매번 찍는다. 동작에는 영향 없는 로그 노이즈라 숨김.
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)


def _set_korean_font() -> None:
    """OS별 한글 지원 폰트를 찾아 matplotlib/seaborn에 적용한다. 없으면 기본 폰트로 계속 진행."""
    candidates = ["Malgun Gothic", "AppleGothic", "NanumGothic", "NanumBarunGothic", "Noto Sans CJK KR"]
    available = {f.name for f in font_manager.fontManager.ttflist}
    for name in candidates:
        if name in available:
            plt.rcParams["font.family"] = name
            break
    else:
        print("[경고] 한글 지원 폰트를 찾지 못했습니다. 그래프의 한글이 깨져 보일 수 있습니다 (실행에는 영향 없음).")
    plt.rcParams["axes.unicode_minus"] = False


_set_korean_font()

# 무거운/선택적 의존성은 import 시점에 예외처리 -> 미설치 환경에서도 해당 단계만 건너뛰고 나머지는 계속 실행
try:
    import polars as pl
except ImportError as e:
    print(f"[경고] polars 불러오기 실패 ({e}). `pip install polars` 필요. Polars 비교 로딩을 건너뜁니다.")
    pl = None

try:
    import seaborn as sns
except ImportError as e:
    print(f"[경고] seaborn 불러오기 실패 ({e}). `pip install seaborn` 필요. Seaborn 정적 차트를 건너뜁니다.")
    sns = None

try:
    import plotly.express as px
except ImportError as e:
    print(f"[경고] plotly 불러오기 실패 ({e}). `pip install plotly` 필요. Plotly 인터랙티브 차트를 건너뜁니다.")
    px = None

try:
    from scipy import stats as scipy_stats
except ImportError as e:
    print(f"[경고] scipy 불러오기 실패 ({e}). `pip install scipy` 필요. t-test를 건너뜁니다.")
    scipy_stats = None

try:
    from sklearn.compose import ColumnTransformer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler, OneHotEncoder
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score, f1_score, classification_report
except ImportError as e:
    print(f"[경고] scikit-learn 불러오기 실패 ({e}). `pip install scikit-learn` 필요. ML Pipeline을 건너뜁니다.")
    ColumnTransformer = Pipeline = StandardScaler = OneHotEncoder = None
    train_test_split = LogisticRegression = None
    accuracy_score = f1_score = classification_report = None

try:
    import joblib
except ImportError as e:
    print(f"[경고] joblib 불러오기 실패 ({e}). `pip install joblib` 필요. 모델 저장을 건너뜁니다.")
    joblib = None

try:
    import requests
except ImportError as e:
    print(f"[경고] requests 불러오기 실패 ({e}). `pip install requests` 필요. 원본 다운로드를 건너뜁니다.")
    requests = None


# ── 설정 ──────────────────────────────────────────────────────────────────
DATA_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2026-05.parquet"
OUTPUT_DIR = "output"
RAW_PATH = os.path.join(OUTPUT_DIR, "yellow_tripdata_2026-05.parquet")  # 다운로드 캐시(재실행 시 재다운로드 방지)

# 월간 전체 데이터는 수백만 행이라 노트북 환경에서 돌리기엔 과함 -> 랜덤 샘플링으로 규모 축소
# None으로 두면 전체 데이터를 그대로 사용 (메모리/속도에 유의)
SAMPLE_N = 300_000
RANDOM_STATE = 42

NUMERIC_COLS = ["trip_distance", "passenger_count", "fare_amount", "tip_amount", "total_amount", "trip_duration_min"]
TOP_N_ZONES = 20  # PULocationID(약 260개 구역) 원-핫 시 차원 폭발 방지용 -> 상위 N개만 개별 범주로 사용


def ensure_output_dir(path: str = OUTPUT_DIR) -> str:
    """산출물을 저장할 output 폴더가 없으면 생성 (처음 실행하는 환경에서는 없을 확률이 높음)."""
    try:
        os.makedirs(path, exist_ok=True)
    except OSError as e:
        print(f"[오류] output 폴더 생성 실패 ({path}): {e}")
    return path


def download_raw_data(url: str = DATA_URL, dest: str = RAW_PATH) -> str:
    """
    원본 parquet을 로컬에 스트리밍 다운로드해서 캐시. 이미 받아둔 파일이 있으면 그대로 재사용해서
    실행할 때마다 수백MB짜리 파일을 다시 받지 않도록 함.
    """
    if os.path.exists(dest):
        print(f"[안내] 캐시된 원본 파일 재사용: {dest}")
        return dest
    if requests is None:
        raise RuntimeError("requests 미설치로 다운로드 불가")

    print(f"[안내] 원본 다운로드 시작: {url}")
    try:
        with requests.get(url, stream=True, timeout=120) as r:
            r.raise_for_status()
            total = int(r.headers.get("content-length", 0))
            downloaded = 0
            with open(dest, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        print(f"\r  {downloaded / total:.1%} ({downloaded / 1e6:.0f}MB/{total / 1e6:.0f}MB)", end="")
        print(f"\n[안내] 다운로드 완료: {dest}")
        return dest
    except Exception as e:
        # 실패 시 부분적으로 받다 만 파일이 남아 다음 실행에서 "완료된 캐시"로 오인되지 않도록 정리
        if os.path.exists(dest):
            os.remove(dest)
        raise RuntimeError(f"다운로드 실패: {e}")


def load_with_pandas_and_polars(path: str):
    """
    같은 parquet 파일을 Pandas / Polars 양쪽으로 로딩해서 결과(행수·로딩시간·메모리)를 비교.
    두 라이브러리가 같은 데이터를 읽었는지(shape 일치) 확인하는 용도도 겸함.
    """
    print("\n=== 1) 데이터 로딩 비교: Pandas vs Polars ===")
    result = {"pandas": None, "polars": None}

    t0 = time.perf_counter()
    pdf = pd.read_parquet(path)
    pandas_sec = time.perf_counter() - t0
    pandas_mem_mb = pdf.memory_usage(deep=True).sum() / 1e6
    print(f"[Pandas] shape={pdf.shape}, 로딩 {pandas_sec:.2f}s, 메모리 {pandas_mem_mb:.1f}MB")
    result["pandas"] = {"shape": pdf.shape, "seconds": pandas_sec, "memory_mb": pandas_mem_mb}

    pldf = None
    if pl is not None:
        try:
            t0 = time.perf_counter()
            pldf = pl.read_parquet(path)
            polars_sec = time.perf_counter() - t0
            polars_mem_mb = pldf.estimated_size("mb")
            print(f"[Polars] shape={pldf.shape}, 로딩 {polars_sec:.2f}s, 메모리 {polars_mem_mb:.1f}MB")
            result["polars"] = {"shape": pldf.shape, "seconds": polars_sec, "memory_mb": polars_mem_mb}
            result["shapes_match"] = pdf.shape == pldf.shape
            print(f"[비교] 두 라이브러리 결과 shape 일치 여부: {result['shapes_match']}")
        except Exception as e:
            print(f"[오류] Polars 로딩 실패: {e}")
    else:
        print("polars 미설치로 비교 생략, Pandas 결과만 사용")

    return pdf, pldf, result


def clean_data(df: pd.DataFrame):
    """
    결측치/중복/비정상값을 처리하고, 이후 분석에 쓸 파생 컬럼(운행시간·시간대·요일)을 추가.
    """
    print("\n=== 2) 결측치·중복 처리 & 파생 컬럼 생성 ===")
    summary = {"raw_rows": len(df)}

    # 연도별로 컬럼 스키마가 조금씩 달라지므로, 이번 분석에 필요한 핵심 컬럼만 존재 여부 확인 후 선택
    needed = ["tpep_pickup_datetime", "tpep_dropoff_datetime", "passenger_count",
              "trip_distance", "PULocationID", "DOLocationID", "payment_type",
              "fare_amount", "tip_amount", "total_amount"]
    missing_cols = [c for c in needed if c not in df.columns]
    if missing_cols:
        print(f"[경고] 없는 컬럼 발견(스키마 차이로 추정): {missing_cols}")
    df = df[[c for c in needed if c in df.columns]].copy()

    # 컬럼 수가 많지 않으므로 결측치가 0건인 컬럼도 걸러내지 않고 전체 컬럼을 다 보여줌
    na_counts = df.isna().sum()  # == df.isnull().sum(), pandas에서 isna/isnull은 완전히 동일한 메서드
    print("[컬럼별 결측치 개수 (isnull().sum())]")
    print(na_counts.to_string())
    summary["na_counts"] = na_counts.to_dict()

    dup_count = int(df.duplicated().sum())
    print(f"[중복 행] {dup_count:,}건 제거")
    summary["duplicates_removed"] = dup_count
    df = df.drop_duplicates()

    # 핵심 컬럼(승/하차 시각, 거리, 운임)에 결측이 있으면 파생 컬럼 계산 자체가 불가능하므로 제거
    df = df.dropna(subset=["tpep_pickup_datetime", "tpep_dropoff_datetime", "trip_distance", "fare_amount"])

    # 파생 컬럼: 운행시간(분), 승차 시각(시), 요일, 주말 여부
    df["trip_duration_min"] = (df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]).dt.total_seconds() / 60
    df["pickup_hour"] = df["tpep_pickup_datetime"].dt.hour
    df["pickup_dow"] = df["tpep_pickup_datetime"].dt.dayofweek  # 0=월요일 ... 6=일요일
    df["is_weekend"] = df["pickup_dow"].isin([5, 6])

    # 도메인 지식 기반 이상치 필터 (실습 3의 IQR 방식 대신, 택시 데이터 특성에 맞는 상식적 범위 사용)
    # - 뉴욕 택시 기본요금은 2.5달러이므로 그 미만은 데이터 오류로 간주
    # - 거리 0 또는 100마일 초과, 운행시간 1분 미만/3시간 초과, 승객수 0/7명 이상은 비정상 기록으로 간주
    before = len(df)
    df = df[
        df["trip_distance"].between(0.1, 100)
        & df["fare_amount"].between(2.5, 300)
        & df["trip_duration_min"].between(1, 180)
        & df["passenger_count"].fillna(1).between(1, 6)
    ]
    removed = before - len(df)
    print(f"[비정상값 필터] {removed:,}건 제외 (거리/운임/운행시간/승객수 범위 밖)")
    summary["invalid_rows_removed"] = removed
    summary["clean_rows"] = len(df)

    print(f"[결과] {summary['raw_rows']:,}행 -> {summary['clean_rows']:,}행")
    return df, summary


def basic_eda(df: pd.DataFrame) -> pd.DataFrame:
    """describe() 기반 기술통계표(평균·표준편차·분위수)를 출력하고 report.md용으로 반환."""
    print("\n=== 3) 기본 EDA: 기술통계 ===")
    desc = df[NUMERIC_COLS].describe().T[["mean", "std", "min", "25%", "50%", "75%", "max"]].round(2)
    print(desc.to_string())
    return desc


def plot_seaborn_distribution(df: pd.DataFrame, out_path: str = os.path.join(OUTPUT_DIR, "dist_seaborn.png")) -> None:
    """Seaborn 정적 차트: trip_distance 분포 히스토그램(+KDE). 요구사항의 '분포' 유형을 담당."""
    print("\n=== 4-1) Seaborn 정적 차트 (분포) ===")
    if sns is None:
        print("seaborn 미설치로 건너뜀")
        return
    try:
        fig, ax = plt.subplots(figsize=(9, 6))
        sns.histplot(df["trip_distance"], bins=60, kde=True, color="#2A9D8F", ax=ax)
        ax.set_title("승차 거리(trip_distance) 분포", fontsize=13, color="#264653", fontweight="bold")
        ax.set_xlabel("거리 (mile)")
        ax.set_ylabel("건수")
        fig.tight_layout()
        fig.savefig(out_path, dpi=120)
        plt.close(fig)
        print(f"저장 완료: {out_path}")
    except Exception as e:
        print(f"[오류] Seaborn 차트 생성 실패: {e}")


def plot_plotly_group_comparison(df: pd.DataFrame, out_path: str = os.path.join(OUTPUT_DIR, "group_plotly.html")) -> None:
    """Plotly 인터랙티브 차트: 승차 시간대별 평균 운임. 요구사항의 '그룹비교' 유형을 담당."""
    print("\n=== 4-2) Plotly 인터랙티브 차트 (그룹비교) ===")
    if px is None:
        print("plotly 미설치로 건너뜀")
        return
    try:
        hourly = df.groupby("pickup_hour", as_index=False)["fare_amount"].mean()
        fig = px.bar(
            hourly, x="pickup_hour", y="fare_amount",
            title="시간대별 평균 운임(fare_amount)",
            labels={"pickup_hour": "승차 시각(시)", "fare_amount": "평균 운임($)"},
            template="plotly_white",
        )
        fig.write_html(out_path)
        print(f"저장 완료: {out_path}")
    except Exception as e:
        print(f"[오류] Plotly 차트 생성 실패: {e}")


def compute_correlation(df: pd.DataFrame) -> pd.DataFrame:
    """주요 수치형 컬럼 간 상관계수 행렬 계산."""
    print("\n=== 5-1) 상관계수 ===")
    corr = df[NUMERIC_COLS].corr().round(2)
    print(corr.to_string())
    return corr


def run_ttest_weekday_weekend(df: pd.DataFrame) -> dict:
    """주중 vs 주말 평균 운임(fare_amount) 차이를 독립표본 t-test로 검정하고 결과를 해석."""
    print("\n=== 5-2) t-test: 주중 vs 주말 평균 운임 ===")
    if scipy_stats is None:
        print("scipy 미설치로 건너뜀")
        return {}
    try:
        weekday = df.loc[~df["is_weekend"], "fare_amount"]
        weekend = df.loc[df["is_weekend"], "fare_amount"]
        # equal_var=False -> 두 그룹 분산이 같다고 가정하지 않는 Welch's t-test (더 안전한 기본 선택)
        t_stat, p_value = scipy_stats.ttest_ind(weekday, weekend, equal_var=False)
        verdict = "유의미한 차이가 있다" if p_value < 0.05 else "유의미한 차이가 없다"
        print(f"주중 평균: {weekday.mean():.2f} / 주말 평균: {weekend.mean():.2f}")
        print(f"t-statistic: {t_stat:.4f}, p-value: {p_value:.4g}")
        print(f"해석 (α=0.05): p-value {'<' if p_value < 0.05 else '>='} 0.05 이므로 주중과 주말 평균 운임은 {verdict}.")
        return {
            "weekday_mean": float(weekday.mean()), "weekend_mean": float(weekend.mean()),
            "t_stat": float(t_stat), "p_value": float(p_value), "verdict": verdict,
        }
    except Exception as e:
        print(f"[오류] t-test 수행 중 오류 발생: {e}")
        return {}


def _prepare_card_tip_data(df: pd.DataFrame):
    """
    신용카드 결제 건만 추려서 tip_pct(운임 대비 팁 비율)와 high_tipper(중앙값 이상 여부) 파생컬럼을 만든다.
    ML Pipeline과 아래 카이제곱 검정이 "고액 팁"을 똑같은 기준으로 정의해서 쓰도록 공용 함수로 분리.
    (현금 결제는 tip_amount가 항상 0으로 기록되므로 카드 결제 건만 대상으로 함)
    """
    if "payment_type" not in df.columns:
        return pd.DataFrame(), None
    card = df[df["payment_type"] == 1].copy()  # 1 = 신용카드 결제 (TLC 데이터 딕셔너리 기준)
    card = card[card["fare_amount"] > 0]
    card["tip_pct"] = card["tip_amount"] / card["fare_amount"]
    median_tip_pct = card["tip_pct"].median()
    # 중앙값을 기준으로 이진 타겟 생성 -> 자동으로 클래스가 50:50에 가깝게 균형을 이룸
    card["high_tipper"] = (card["tip_pct"] >= median_tip_pct).astype(int)
    return card, median_tip_pct


def run_chi2_rushhour_tip(df: pd.DataFrame) -> dict:
    """
    [이 검정을 고른 이유]
    ML Pipeline에서 pickup_hour(승차 시각)를 피처로 쓰고 있는데, 정작 "시간대가 팁 성향과
    실제로 관계가 있는지"는 확인한 적이 없었다. 둘 다 범주형(러시아워 여부 / 고액 팁 여부)으로
    바꿀 수 있는 변수라 t-test보다 카이제곱 독립성 검정이 적합하고, 결과가 모델이 이 피처를
    쓰는 근거를 통계적으로 뒷받침(혹은 반박)해준다는 점에서 다른 변수쌍보다 의미가 있다고 판단했다.
    """
    print("\n=== 5-3) 카이제곱 검정: 러시아워 여부 vs 고액 팁 여부 ===")
    if scipy_stats is None:
        print("scipy 미설치로 건너뜀")
        return {}
    try:
        card, _ = _prepare_card_tip_data(df)
        if card.empty:
            print("[경고] payment_type 컬럼이 없어 카드 결제 필터링 불가, 건너뜀")
            return {}

        # 출퇴근 러시아워: 아침 7~9시, 저녁 16~19시 (뉴욕 TLC 통계에서 흔히 쓰는 구간)
        rush_hours = {7, 8, 9, 16, 17, 18, 19}
        card["is_rush_hour"] = card["pickup_hour"].isin(rush_hours)

        contingency = pd.crosstab(card["is_rush_hour"], card["high_tipper"])
        chi2, p_value, dof, _ = scipy_stats.chi2_contingency(contingency)
        verdict = "서로 독립이 아니다 (연관이 있다)" if p_value < 0.05 else "서로 독립이다 (연관이 없다)"
        print(contingency.to_string())
        print(f"chi2: {chi2:.4f}, dof: {dof}, p-value: {p_value:.4g}")
        print(f"해석 (α=0.05): p-value {'<' if p_value < 0.05 else '>='} 0.05 이므로 러시아워 여부와 고액 팁 여부는 {verdict}.")
        return {
            "chi2": float(chi2), "p_value": float(p_value), "dof": int(dof),
            "verdict": verdict, "contingency": contingency,
        }
    except Exception as e:
        print(f"[오류] 카이제곱 검정 수행 중 오류 발생: {e}")
        return {}


def build_ml_pipeline(df: pd.DataFrame, model_path: str = os.path.join(OUTPUT_DIR, "tip_model.joblib")) -> dict:
    """
    신용카드 결제 건에 한정해 '평소보다 팁을 후하게 준 승객(high tipper)'을 예측하는 이진분류 파이프라인.
    ColumnTransformer로 수치형(StandardScaler)/범주형(OneHotEncoder) 전처리를 나눠 구성하고,
    Pipeline으로 전처리+모델을 하나로 묶어 학습·평가·저장까지 수행.
    """
    print("\n=== 6) ML Pipeline: 고액 팁 여부 분류 ===")
    if ColumnTransformer is None:
        print("scikit-learn 미설치로 건너뜀")
        return {}

    try:
        card, median_tip_pct = _prepare_card_tip_data(df)
        if card.empty:
            print("[경고] payment_type 컬럼이 없어 카드 결제 필터링 불가, 건너뜀")
            return {}

        # PULocationID(약 260개 구역)를 그대로 원-핫하면 차원이 과도하게 커지므로
        # 등장 빈도 상위 TOP_N_ZONES개만 개별 범주로 남기고 나머지는 'OTHER'로 묶음
        top_zones = card["PULocationID"].value_counts().nlargest(TOP_N_ZONES).index
        card["pickup_zone"] = card["PULocationID"].where(card["PULocationID"].isin(top_zones), "OTHER").astype(str)

        num_features = ["trip_distance", "passenger_count", "trip_duration_min", "pickup_hour"]
        cat_features = ["pickup_zone", "is_weekend"]
        X = card[num_features + cat_features]
        y = card["high_tipper"]

        # stratify=y로 학습/테스트 세트의 클래스 비율을 원본과 동일하게 유지
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
        )

        preprocessor = ColumnTransformer(transformers=[
            ("num", StandardScaler(), num_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_features),  # 테스트에만 나오는 범주 있어도 에러 안 나게
        ])
        model = Pipeline([
            ("preprocessor", preprocessor),
            ("classifier", LogisticRegression(max_iter=1000)),
        ])

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        print(f"정확도(Accuracy): {acc:.4f}")
        print(f"F1-score: {f1:.4f}")
        print(classification_report(y_test, y_pred, target_names=["일반", "고액팁"]))

        if joblib is not None:
            joblib.dump(model, model_path)
            print(f"모델 저장 완료: {model_path}")
        else:
            print("joblib 미설치로 모델 저장 건너뜀")

        return {
            "accuracy": float(acc), "f1": float(f1),
            "n_train": len(X_train), "n_test": len(X_test),
            "median_tip_pct": float(median_tip_pct),
        }
    except Exception as e:
        print(f"[오류] ML Pipeline 실행 중 오류 발생: {e}")
        return {}


def _df_to_md(df: pd.DataFrame) -> str:
    """DataFrame을 마크다운 표로 변환. tabulate 미설치 시 코드블록(to_string)으로 대체."""
    try:
        return df.to_markdown()
    except ImportError:
        return "```\n" + df.to_string() + "\n```"


def generate_report(load_result: dict, clean_summary: dict, desc_stats: pd.DataFrame,
                     corr: pd.DataFrame, ttest_result: dict, chi2_result: dict, ml_result: dict,
                     out_path: str = os.path.join(OUTPUT_DIR, "report.md")) -> None:
    """지금까지의 모든 분석 결과를 report.md 한 파일로 자동 정리 (자동화 요구사항 대응)."""
    print("\n=== 7) report.md 자동 생성 ===")

    lines = ["# NYC Yellow Taxi (2026-05) End2End 분석 리포트", ""]
    lines.append(f"- 생성 시각: {datetime.now():%Y-%m-%d %H:%M:%S}")
    lines.append(f"- 원본 데이터: {DATA_URL}")
    lines.append("")

    lines.append("## 1. 데이터 로딩 비교 (Pandas vs Polars)")
    p = load_result.get("pandas") or {}
    lines.append(f"- Pandas: shape={p.get('shape')}, 로딩 {p.get('seconds', 0):.2f}s, 메모리 {p.get('memory_mb', 0):.1f}MB")
    if load_result.get("polars"):
        pol = load_result["polars"]
        lines.append(f"- Polars: shape={pol.get('shape')}, 로딩 {pol.get('seconds', 0):.2f}s, 메모리 {pol.get('memory_mb', 0):.1f}MB")
        lines.append(f"- 두 결과 shape 일치 여부: {load_result.get('shapes_match')}")
    else:
        lines.append("- Polars: 미설치로 비교 생략")
    lines.append("")

    lines.append("## 2. 결측치·중복·이상치 처리")
    lines.append(f"- 원본 행 수: {clean_summary.get('raw_rows', 0):,}")
    na_counts = clean_summary.get("na_counts") or {}
    if na_counts:
        # isnull().sum() 결과를 컬럼별로 표로 정리 -> 어느 컬럼이 얼마나 비어있었는지 한눈에 확인 가능
        na_df = pd.DataFrame.from_dict(na_counts, orient="index", columns=["결측치 개수"])
        na_df.index.name = "컬럼"
        lines.append("- 컬럼별 결측치 개수 (isnull().sum()):")
        lines.append(_df_to_md(na_df))
    else:
        lines.append("- 컬럼별 결측치: 없음")
    lines.append(f"- 중복 제거: {clean_summary.get('duplicates_removed', 0):,}건")
    lines.append(f"- 비정상값 제외: {clean_summary.get('invalid_rows_removed', 0):,}건")
    lines.append(f"- 최종 행 수: {clean_summary.get('clean_rows', 0):,}")
    lines.append("")

    lines.append("## 3. 기술통계")
    lines.append(_df_to_md(desc_stats))
    lines.append("")

    lines.append("## 4. 상관계수")
    lines.append(_df_to_md(corr))
    lines.append("")

    lines.append("## 5. 시각화")
    lines.append("- Seaborn 정적 차트: `dist_seaborn.png` (승차 거리 분포)")
    lines.append("- Plotly 인터랙티브 차트: `group_plotly.html` (시간대별 평균 운임)")
    lines.append("")

    lines.append("## 6. t-test (주중 vs 주말 평균 운임)")
    if ttest_result:
        lines.append(f"- 주중 평균: {ttest_result['weekday_mean']:.2f} / 주말 평균: {ttest_result['weekend_mean']:.2f}")
        lines.append(f"- t={ttest_result['t_stat']:.4f}, p={ttest_result['p_value']:.4g}")
        lines.append(f"- 해석: {ttest_result['verdict']} (α=0.05)")
    else:
        lines.append("- 실행되지 않음 (scipy 미설치)")
    lines.append("")

    lines.append("## 7. 카이제곱 검정 (러시아워 여부 vs 고액 팁 여부)")
    lines.append("- ML Pipeline이 피처로 쓰는 pickup_hour(시간대)가 실제로 팁 성향과 관계있는지 확인하기 위해 추가")
    if chi2_result:
        lines.append("")
        lines.append(_df_to_md(chi2_result["contingency"]))
        lines.append("")
        lines.append(f"- chi2={chi2_result['chi2']:.4f}, dof={chi2_result['dof']}, p={chi2_result['p_value']:.4g}")
        lines.append(f"- 해석: {chi2_result['verdict']} (α=0.05)")
    else:
        lines.append("- 실행되지 않음 (scipy 미설치 또는 payment_type 컬럼 없음)")
    lines.append("")

    lines.append("## 8. ML Pipeline (고액 팁 여부 분류)")
    if ml_result:
        lines.append(f"- 학습/테스트 데이터 수: {ml_result['n_train']:,} / {ml_result['n_test']:,}")
        lines.append(f"- 고액 팁 기준 tip_pct 중앙값: {ml_result['median_tip_pct']:.3f}")
        lines.append(f"- Accuracy: {ml_result['accuracy']:.4f}")
        lines.append(f"- F1-score: {ml_result['f1']:.4f}")
        lines.append("- 저장된 모델: `tip_model.joblib`")
    else:
        lines.append("- 실행되지 않음")
    lines.append("")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"저장 완료: {out_path}")


def main() -> None:
    try:
        ensure_output_dir()

        raw_path = download_raw_data()
        pdf, pldf, load_result = load_with_pandas_and_polars(raw_path)

        # 월간 전체 데이터는 규모가 크므로 실습 편의를 위해 일부만 랜덤 샘플링해서 이후 단계에 사용
        if SAMPLE_N and len(pdf) > SAMPLE_N:
            pdf = pdf.sample(n=SAMPLE_N, random_state=RANDOM_STATE)
            print(f"[안내] 실습 편의를 위해 {SAMPLE_N:,}행으로 랜덤 샘플링")

        clean_df, clean_summary = clean_data(pdf)
        desc_stats = basic_eda(clean_df)

        plot_seaborn_distribution(clean_df)
        plot_plotly_group_comparison(clean_df)

        corr = compute_correlation(clean_df)
        ttest_result = run_ttest_weekday_weekend(clean_df)
        chi2_result = run_chi2_rushhour_tip(clean_df)

        ml_result = build_ml_pipeline(clean_df)

        generate_report(load_result, clean_summary, desc_stats, corr, ttest_result, chi2_result, ml_result)

        print("\n모든 단계 완료. output/ 폴더를 확인하세요.")
    except Exception as e:
        # 어느 단계에서 터지든 여기서 한 번에 잡아 메시지 출력 후 종료 -> 스택트레이스 대신 사용자 친화적 메시지
        print(f"[치명적 오류] 프로그램 실행 중단: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()