"""
[실습 4] 시각화 4종 / 통계 검정 / sklearn Pipeline / Plotly
=========================================================

sales_100k.csv 를 대상으로 아래 4가지 작업을 수행 (실습 3 연계)
  1) EDA 시각화 4종 (2x2 서브플롯 한 figure): 히스토그램+KDE / 박스플롯 / 월별 라인 / 상관 히트맵
  2) 통계 검정: 서울 vs 부산 평균 매출 t-test, 지역x카테고리 독립성 카이제곱 검정
  3) sklearn Pipeline: ColumnTransformer + Pipeline 구성, 훈련·평가(predict/score)·저장(joblib)·재로딩
  4) Plotly 인터랙티브 막대 차트(지역·카테고리별 총매출) 생성 후 .html로 저장

< 실습 3 연계 Point >
- IQR 이상치 제거된 DataFrame  -> 1),2) 시각화·통계 검정의 입력 데이터로 사용
- region/category groupby 결과 -> 2) 카이제곱 분할표, 4) Plotly 막대 차트에 활용
- sales_100k.csv(원본)         -> 3) sklearn Pipeline 학습 데이터 원본 (이상치 제거 없이 원본 사용)

산출물은 스크립트 실행 위치 기준 ./output/ 폴더에 저장
(eda_4plots.png, sales_amount_model.joblib, region_category_sales.html)
"""

import os
import sys

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")  # 화면 출력 환경이 없어도 파일로 저장 가능하도록
import matplotlib.pyplot as plt
from matplotlib import font_manager


def _set_korean_font() -> None:
    """OS별 한글 지원 폰트를 찾아 matplotlib에 적용한다. 없으면 기본 폰트를 유지(글자는 깨지되 실행은 계속)."""
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

# 무거운/선택적 의존성은 import 시점에 예외처리하여, 미설치 시 해당 실습만 건너뛰도록 함
try:
    from scipy import stats as scipy_stats
except ImportError as e:
    print(f"[경고] scipy 불러오기 실패 ({e}). `pip install scipy` 필요. 2번(통계 검정)을 건너뜁니다.")
    scipy_stats = None

try:
    from sklearn.compose import ColumnTransformer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler, OneHotEncoder
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import r2_score
except ImportError as e:
    print(f"[경고] scikit-learn 불러오기 실패 ({e}). `pip install scikit-learn` 필요. 3번(Pipeline)을 건너뜁니다.")
    ColumnTransformer = Pipeline = StandardScaler = OneHotEncoder = None
    SimpleImputer = LinearRegression = train_test_split = r2_score = None

try:
    import joblib
except ImportError as e:
    print(f"[경고] joblib 불러오기 실패 ({e}). `pip install joblib` 필요. 3번의 모델 저장/재로딩을 건너뜁니다.")
    joblib = None

try:
    import plotly.express as px
except ImportError as e:
    print(f"[경고] plotly 불러오기 실패 ({e}). `pip install plotly` 필요. 4번(인터랙티브 차트)을 건너뜁니다.")
    px = None


CSV_PATH = "sales_100k.csv"
VALUE_COL = "amount"
GROUP_COLS = ["region", "category"]
NUM_FEATURES = ["quantity", "unit_price", "customer_age"]
CAT_FEATURES = ["region", "category", "payment_method", "customer_gender"]
OUTPUT_DIR = "output"  # 그래프/모델/HTML 등 산출물을 모아 저장할 폴더


def ensure_output_dir(path: str = OUTPUT_DIR) -> str:
    """
    산출물을 저장할 output 폴더가 없으면 생성 (처음 실행하는 환경에서는 folder가 없을 확률이 높음)
    """
    try:
        os.makedirs(path, exist_ok=True)
    except OSError as e:
        print(f"[오류] output 폴더 생성 실패 ({path}): {e}")
    return path


def load_data(path: str) -> pd.DataFrame:
    """
    CSV 로딩 -> 파일이 없거나 파싱 오류가 나면 메시지를 출력하고 종료
    """
    try:
        return pd.read_csv(path)
    except FileNotFoundError:
        print(f"[오류] 파일을 찾을 수 없습니다: {path}")
        sys.exit(1)
    except pd.errors.ParserError as e:
        print(f"[오류] CSV 파싱 실패: {e}")
        sys.exit(1)


def filter_iqr(df: pd.DataFrame, col: str, lower: float, upper: float) -> pd.DataFrame:
    """
    결측치를 제거하고 IQR 정상 범위 [lower, upper] 기준을 만족하지 못하면 Drop
    (실습 3과 동일 로직)
    """
    clean = df.dropna(subset=[col])
    return clean[clean[col].between(lower, upper)]


def compute_iqr_bounds(df: pd.DataFrame, col: str) -> tuple[float, float]:
    """
    IQR 방법으로 정상 범위 [Q1-1.5*IQR, Q3+1.5*IQR]를 계산
    """
    try:
        q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
    except KeyError:
        raise KeyError(f"'{col}' 컬럼이 존재하지 않습니다.")
    iqr = q3 - q1
    return q1 - 1.5 * iqr, q3 + 1.5 * iqr


def plot_eda_grid(df: pd.DataFrame, out_path: str = os.path.join(OUTPUT_DIR, "eda_4plots.png")) -> None:
    """
    2x2 서브플롯(한 figure)에 히스토그램+KDE / 박스플롯 / 월별 라인 / 상관 히트맵을 그려 파일로 저장
    """
    try:
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # (1) 히스토그램 + KDE : amount 분포
        ax = axes[0, 0]
        amount = df[VALUE_COL].dropna()
        ax.hist(amount, bins=50, density=True, alpha=0.6, color="steelblue", label="히스토그램")
        if scipy_stats is not None and len(amount) > 1:
            kde = scipy_stats.gaussian_kde(amount)
            x_grid = np.linspace(amount.min(), amount.max(), 300)
            ax.plot(x_grid, kde(x_grid), color="darkred", label="KDE")
        ax.set_title("amount 분포 (히스토그램 + KDE)")
        ax.legend()

        # (2) 박스플롯 : region별 amount
        ax = axes[0, 1]
        region_df = df.dropna(subset=["region", VALUE_COL])
        regions = sorted(region_df["region"].unique())
        data_by_region = [region_df.loc[region_df["region"] == r, VALUE_COL] for r in regions]
        ax.boxplot(data_by_region, tick_labels=regions)
        ax.set_title("region별 amount 박스플롯")
        ax.tick_params(axis="x", rotation=45)

        # (3) 월별 라인 : 월별 총매출 추이
        ax = axes[1, 0]
        date_df = df.dropna(subset=["order_date", VALUE_COL]).copy()
        date_df["order_date"] = pd.to_datetime(date_df["order_date"], errors="coerce")
        monthly = date_df.dropna(subset=["order_date"]).groupby(
            date_df["order_date"].dt.to_period("M")
        )[VALUE_COL].sum().sort_index()
        ax.plot(monthly.index.astype(str), monthly.values, marker="o")
        ax.set_title("월별 총매출 추이")
        ax.tick_params(axis="x", rotation=90)

        # (4) 상관 히트맵 : 주요 수치형 컬럼
        ax = axes[1, 1]
        numeric_cols = ["quantity", "unit_price", "customer_age", VALUE_COL]
        corr = df[numeric_cols].corr()
        im = ax.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
        ax.set_xticks(range(len(numeric_cols)))
        ax.set_yticks(range(len(numeric_cols)))
        ax.set_xticklabels(numeric_cols, rotation=45, ha="right")
        ax.set_yticklabels(numeric_cols)
        for i in range(len(numeric_cols)):
            for j in range(len(numeric_cols)):
                ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=9)
        fig.colorbar(im, ax=ax)
        ax.set_title("수치형 컬럼 상관 히트맵")

        fig.tight_layout()
        fig.savefig(out_path, dpi=120)
        plt.close(fig)
        print(f"\n=== 1) EDA 시각화 4종 저장 완료: {out_path} ===")
    except Exception as e:
        print(f"[오류] 시각화 생성 중 오류 발생: {e}")


def run_ttest(df: pd.DataFrame, region_a: str = "서울", region_b: str = "부산") -> None:
    """
    region_a vs region_b 의 평균 amount 차이를 독립표본 t-test로 검정하고 결과를 해석
    """

    print(f"\n=== 2-1) t-test: {region_a} vs {region_b} 평균 매출 ===")

    if scipy_stats is None:
        print("scipy 미설치로 건너뜀")
        return
    try:
        g1 = df.loc[df["region"] == region_a, VALUE_COL].dropna()
        g2 = df.loc[df["region"] == region_b, VALUE_COL].dropna()
        if len(g1) < 2 or len(g2) < 2:
            raise ValueError(f"표본 수가 부족합니다 ({region_a}: {len(g1)}, {region_b}: {len(g2)})")
        t_stat, p_value = scipy_stats.ttest_ind(g1, g2, equal_var=False)  # Welch's t-test
        print(f"{region_a} 평균: {g1.mean():,.0f} / {region_b} 평균: {g2.mean():,.0f}")
        print(f"t-statistic: {t_stat:.4f}, p-value: {p_value:.4g}")
        verdict = "유의미한 차이가 있다" if p_value < 0.05 else "유의미한 차이가 없다"
        print(f"해석 (α=0.05): p-value {'<' if p_value < 0.05 else '>='} 0.05 이므로 두 지역 평균 매출은 {verdict}.")
    except Exception as e:
        print(f"[오류] t-test 수행 중 오류 발생: {e}")


def run_chi2(df: pd.DataFrame) -> None:
    """
    region x category 분할표를 만들어 카이제곱 독립성 검정을 수행하고 결과를 해석
    """

    print("\n=== 2-2) 카이제곱 검정: region x category 독립성 ===")

    if scipy_stats is None:
        print("scipy 미설치로 건너뜀")
        return
    try:
        clean = df.dropna(subset=GROUP_COLS)
        contingency = pd.crosstab(clean["region"], clean["category"])
        chi2, p_value, dof, _ = scipy_stats.chi2_contingency(contingency)
        print(f"chi2: {chi2:.4f}, dof: {dof}, p-value: {p_value:.4g}")
        verdict = "서로 독립이 아니다 (연관이 있다)" if p_value < 0.05 else "서로 독립이다 (연관이 없다)"
        print(f"해석 (α=0.05): p-value {'<' if p_value < 0.05 else '>='} 0.05 이므로 region과 category는 {verdict}.")

    except Exception as e:
        print(f"[오류] 카이제곱 검정 수행 중 오류 발생: {e}")


def build_and_save_pipeline(path: str, model_path: str = os.path.join(OUTPUT_DIR, "sales_amount_model.joblib")):
    """
    원본 CSV로 ColumnTransformer+Pipeline(전처리+회귀모델)을 구성해 훈련·평가하고 joblib으로 저장/재로딩
    """

    print("\n=== 3) sklearn Pipeline: amount 예측 모델 ===")

    if ColumnTransformer is None or joblib is None:
        print("scikit-learn 또는 joblib 미설치로 건너뜀")
        return None

    try:
        df = pd.read_csv(path).dropna(subset=[VALUE_COL])  # 학습을 위해 target 결측만 제거 (원본 데이터 사용)
        X = df[NUM_FEATURES + CAT_FEATURES]
        y = df[VALUE_COL]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # 수치형 변수에 대해서 standardscaler적용
        # 범주형 변수에 대해서 결측지는 최빈값으로 대체해고 onehotencoder 사용 
        preprocessor = ColumnTransformer(
            transformers=[
                ("num", StandardScaler(), NUM_FEATURES),
                (
                    "cat",
                    Pipeline([
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore")),
                    ]),
                    CAT_FEATURES,
                ),
            ]
        )
        # 파이프라인을 통해 전처리를 수행하고 선형회귀분석 실행
        model = Pipeline([("preprocessor", preprocessor), ("regressor", LinearRegression())])

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        r2 = r2_score(y_test, y_pred)
        print(f"테스트 R²: {r2:.4f}")

        joblib.dump(model, model_path)
        print(f"모델 저장 완료: {model_path}")

        reloaded = joblib.load(model_path)
        reload_r2 = r2_score(y_test, reloaded.predict(X_test))
        print(f"재로딩된 모델 검증 R²: {reload_r2:.4f} (원본과 일치: {np.isclose(r2, reload_r2)})")
        return reloaded

    except Exception as e:
        print(f"[오류] Pipeline 학습/저장 중 오류 발생: {e}")
        return None


def build_plotly_chart(df: pd.DataFrame, out_path: str = os.path.join(OUTPUT_DIR, "region_category_sales.html")) -> None:
    """
    region/category별 총매출 막대 차트를 Plotly Express로 만들고 .html로 저장
    """

    print("\n=== 4) Plotly 인터랙티브 막대 차트 ===")

    if px is None:
        print("plotly 미설치로 건너뜀")
        return

    try:
        agg = (
            df.dropna(subset=GROUP_COLS)
            .groupby(GROUP_COLS)[VALUE_COL]
            .sum()
            .reset_index(name="total")
            .sort_values("total", ascending=False)
        )
        fig = px.bar(
            agg, x="region", y="total", color="category", barmode="group",
            title="지역·카테고리별 총매출", labels={"total": "총매출", "region": "지역", "category": "카테고리"},
        )
        fig.write_html(out_path)
        print(f"저장 완료: {out_path}")

    except Exception as e:
        print(f"[오류] Plotly 차트 생성 중 오류 발생: {e}")


def main() -> None:

    try:
        ensure_output_dir()  # 그래프/모델/HTML을 모아 저장할 output 폴더 준비

        raw_df = load_data(CSV_PATH)
        lower, upper = compute_iqr_bounds(raw_df, VALUE_COL)
        clean_df = filter_iqr(raw_df, VALUE_COL, lower, upper)  # 실습 3 산출물: 이상치 제거된 DataFrame

        print()
        plot_eda_grid(clean_df)          # 1) 시각화 4종 - 이상치 제거된 데이터 사용
        print()
        run_ttest(clean_df)              # 2-1) t-test - 이상치 제거된 데이터 사용
        print()
        run_chi2(clean_df)               # 2-2) 카이제곱 - 이상치 제거된 데이터 사용
        print()
        build_and_save_pipeline(CSV_PATH)  # 3) Pipeline - 원본 CSV 사용 -> 전처리를 수행해야되기 때문에 원본 데이터를 활용함
        print()
        build_plotly_chart(clean_df)     # 4) Plotly - 이상치 제거된 데이터 사용

    except Exception as e:
        print(f"[치명적 오류] 프로그램 실행 중단: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
