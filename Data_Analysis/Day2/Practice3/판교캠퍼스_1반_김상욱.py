"""
[실습 3] Pandas EDA / Polars Lazy / DuckDB SQL 비교
====================================================

sales_100k.csv 를 대상으로 아래 4가지 작업을 수행
  1) Pandas를 활용하여 기초 EDA + IQR 방법 이상치 제거
  2) Pandas groupby + named aggregation (region/category 별 총매출/평균/건수, 총매출 내림차순)
  3) 2)와 동일한 집계를 Polars Lazy API(scan_csv → filter → group_by → agg → sort → collect)로 작성
  4) 동일 집계를 DuckDB SQL 로 작성하고, timeit 으로 세 도구의 실행 시간(동일 반복 횟수) 비교


IQR 이상치 기준: 정상 범위 = [Q1 - 1.5*IQR, Q3 + 1.5*IQR] (amount 컬럼 기준)
세 도구 모두 동일한 컬럼(amount) 결측 제거 + 동일한 IQR 경계값을 사용하여 공정하게 비교한다.
"""

import sys
import time
import timeit
from functools import partial

import pandas as pd

# import를 하는 과정에서 생길 수 있는 오류에 대한 예외처리 수행
try:
    import polars as pl
except ImportError as e:
    print(f"[경고] polars 모듈을 불러올 수 없습니다 ({e}). `pip install polars` 후 재실행하세요. 3번 실습은 건너뜁니다.")
    pl = None
 
try:
    import duckdb
except ImportError as e:
    print(f"[경고] duckdb 모듈을 불러올 수 없습니다 ({e}). `pip install duckdb` 후 재실행하세요. 4번 실습은 건너뜁니다.")
    duckdb = None

# 각 코드의 재사용성을 고려하여 함수형태로 정의할 예정
# 각 요구사항들에 대해서 해야될 작업들을 빼먹지 않기 위함도 있음

CSV_PATH = "sales_100k.csv"
GROUP_COLS = ["region", "category"]
VALUE_COL = "amount"
TIMEIT_NUMBER = 3  


def load_and_explore(path: str) -> pd.DataFrame:
    """
    CSV를 로딩하고 기본 EDA(shape, info, 결측치)를 출력한 뒤 DataFrame을 반환
    (일반적으로 오류가 잘 나지는 않지만 예외처리를 습관화하는 연습을 하기 위해 기본적인 예외처리 적용한 버전)
    """
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        print(f"[오류] 파일을 찾을 수 없습니다: {path}")
        sys.exit(1)
    except pd.errors.ParserError as e:
        print(f"[오류] CSV 파싱 실패: {e}")
        sys.exit(1)

    print(f"\n=== 1) 기초 EDA: {path} ===")
    print(f"shape: {df.shape}")
    df.info()
    print("\n결측치 수:")
    print(df.isnull().sum())
    return df


def compute_iqr_bounds(df: pd.DataFrame, col: str) -> tuple[float, float]:
    """
    IQR 방법으로 정상 범위 [Q1-1.5*IQR, Q3+1.5*IQR]를 계산해 반환
    """
    try:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
    except KeyError:
        raise KeyError(f"'{col}' 컬럼이 존재하지 않습니다.")
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return lower, upper


def remove_outliers_pandas(df: pd.DataFrame, col: str, lower: float, upper: float) -> pd.DataFrame:
    """
    결측치를 제거한 뒤 IQR 정상 범위를 벗어난 행을 제거하고, 제거 전/후 행 수를 출력
    """
    before = len(df)
    clean = df.dropna(subset=[col])
    clean = clean[clean[col].between(lower, upper)]
    after = len(clean)
    print(f"\n이상치 제거 전 행 수: {before:,} / 제거 후 행 수: {after:,} (제거된 행: {before - after:,})")
    return clean


def pandas_named_agg(df: pd.DataFrame) -> pd.DataFrame:
    """
    region/category별 총매출·평균·건수를 named aggregation으로 계산하고 총매출 내림차순 정렬
    """
    try:
        result = (
            df.groupby(GROUP_COLS, dropna=True)
            .agg(total=(VALUE_COL, "sum"), mean=(VALUE_COL, "mean"), count=(VALUE_COL, "count"))
            .reset_index()
            .sort_values("total", ascending=False)
            .reset_index(drop=True)
        )
    except Exception as e:
        raise RuntimeError(f"named aggregation 계산 중 오류 발생: {e}")
    return result


def pandas_pipeline(path: str, lower: float, upper: float) -> pd.DataFrame:
    """
    CSV 로딩부터 named aggregation까지의 전체 Pandas 파이프라인 (벤치마크용) 구축용 함수
    """
    df = pd.read_csv(path).dropna(subset=[VALUE_COL])
    df = df[df[VALUE_COL].between(lower, upper)]
    return pandas_named_agg(df)


def polars_pipeline(path: str, lower: float, upper: float):
    """
    Polars Lazy API로 동일 집계를 수행하기 위한 함수
    전체 과정 : scan_csv → filter → group_by → agg → sort → collect
    """
    if pl is None:
        raise ImportError("polars 패키지가 설치되어 있지 않습니다. `pip install polars` 후 재실행하세요.")
    try:
        result = (
            pl.scan_csv(path)
            .filter(pl.col(VALUE_COL).is_not_null() & pl.col(VALUE_COL).is_between(lower, upper))
            .group_by(GROUP_COLS)
            .agg(
                pl.sum(VALUE_COL).alias("total"),
                pl.mean(VALUE_COL).alias("mean"),
                pl.count(VALUE_COL).alias("count"),
            )
            .sort("total", descending=True)
            .collect()
        )
    except Exception as e:
        raise RuntimeError(f"Polars Lazy 집계 중 오류 발생: {e}")
    return result


def duckdb_pipeline(path: str, lower: float, upper: float):
    """
    DuckDB SQL로 동일 집계를 수행하기 위한 함수
    """
    if duckdb is None:
        raise ImportError("duckdb 패키지가 설치되어 있지 않습니다. `pip install duckdb` 후 재실행하세요.")

    query = f"""
        SELECT region, category,
               SUM(amount) AS total,
               AVG(amount) AS mean,
               COUNT(amount) AS count
        FROM read_csv_auto('{path}')
        WHERE amount IS NOT NULL
          AND amount BETWEEN {lower} AND {upper}
        GROUP BY region, category
        ORDER BY total DESC
    """
    try:
        result = duckdb.sql(query).df()
    except Exception as e:
        raise RuntimeError(f"DuckDB SQL 집계 중 오류 발생: {e}")
    return result


def benchmark(path: str, lower: float, upper: float) -> None:
    """
    세 도구의 전체 파이프라인 실행 시간을 동일 반복 횟수(timeit)로 비교하기 위한 함수
    """
    print(f"\n=== 4) 성능 비교 (timeit, number={TIMEIT_NUMBER}) ===")
    tools = {"Pandas": pandas_pipeline, "Polars Lazy": polars_pipeline, "DuckDB SQL": duckdb_pipeline}
    for name, fn in tools.items():
        if (name == "Polars Lazy" and pl is None) or (name == "DuckDB SQL" and duckdb is None):
            print(f"{name:<12}: 건너뜀 (패키지 미설치)")
            continue
        try:
            elapsed = timeit.timeit(partial(fn, path, lower, upper), number=TIMEIT_NUMBER)
            print(f"{name:<12}: 총 {elapsed:.3f}초 / 평균 {elapsed / TIMEIT_NUMBER:.3f}초")
        except Exception as e:
            print(f"{name:<12}: 실행 실패 - {e}")


def main() -> None:
    try:
        df = load_and_explore(CSV_PATH)
        lower, upper = compute_iqr_bounds(df, VALUE_COL)
        print(f"\nIQR 정상 범위: [{lower:,.2f}, {upper:,.2f}]")

        clean_df = remove_outliers_pandas(df, VALUE_COL, lower, upper)
        print()

        print("\n=== 2) Pandas groupby named aggregation (총매출 내림차순) ===")
        pandas_result = pandas_named_agg(clean_df)
        print(pandas_result.head(10))
        print()

        print("\n=== 3) Polars Lazy 동일 집계 ===")
        if pl is not None:
            polars_result = polars_pipeline(CSV_PATH, lower, upper)
            print(polars_result.head(10))
        else:
            print("polars 미설치로 건너뜀")
        print()

        print("\n=== DuckDB SQL 동일 집계 ===")
        if duckdb is not None:
            duckdb_result = duckdb_pipeline(CSV_PATH, lower, upper)
            print(duckdb_result.head(10))
        else:
            print("duckdb 미설치로 건너뜀")

        benchmark(CSV_PATH, lower, upper)

    except Exception as e:
        print(f"[치명적 오류] 프로그램 실행 중단: {e}")
        sys.exit(1)


if __name__ == "__main__":
    start = time.time()
    main()
    print(f"\n총 실행 시간: {time.time() - start:.2f}초")


"""
Data_analysis 라는 가상환경에는 polar, DuckDB 라이브러리를 설치한 적이 없기 때문에 초기 실행에서는 3,4번의 경우는 수행되지 않음
또한 예외처리를 해두었기 때문에 output 출력 값으로 관련 정보가 나옴

pip install 이후는 관련 정보가 잘 나오는 것을 알 수 있음
"""
