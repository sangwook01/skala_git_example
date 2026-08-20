"""
저장 및 성능 비교
--------------------------------------------------------------
검증을 통과한 DataFrame을 CSV/Parquet 두 형식으로 저장하고, 각각의
쓰기/읽기 소요 시간을 time.perf_counter()로 측정해 비교한다.

해당 내용은 순수 Claude code에 의존하여 생성
"""

import logging
import time
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def save_and_compare(df: pd.DataFrame, out_dir: str, name: str) -> dict:
    """df를 {name}.csv / {name}.parquet로 저장하고, 저장 직후 다시 읽어
    쓰기/읽기 시간을 각각 측정한다. 결과는 초 단위 dict로 반환."""
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    csv_path = out_path / f"{name}.csv"
    parquet_path = out_path / f"{name}.parquet"

    timings: dict = {}

    # CSV는 표준 라이브러리 기반이라 실패 가능성이 낮지만, Parquet은 pyarrow/
    # fastparquet 미설치 시 ImportError가 날 수 있어 단계별로 독립 처리한다.
    # 한쪽이 실패해도 다른 쪽 측정 결과는 남기기 위해 각각 try-except로 감싼다.
    try:
        t0 = time.perf_counter()
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        timings["csv_write_sec"] = time.perf_counter() - t0
        t0 = time.perf_counter()
        pd.read_csv(csv_path)
        timings["csv_read_sec"] = time.perf_counter() - t0
        timings["csv_size_bytes"] = csv_path.stat().st_size
    except (OSError, ValueError) as e:
        logger.error(f"'{name}' CSV 저장/읽기 실패: {e}")

    try:
        t0 = time.perf_counter()
        df.to_parquet(parquet_path, index=False)
        timings["parquet_write_sec"] = time.perf_counter() - t0
        t0 = time.perf_counter()
        pd.read_parquet(parquet_path)
        timings["parquet_read_sec"] = time.perf_counter() - t0
        timings["parquet_size_bytes"] = parquet_path.stat().st_size
    except (OSError, ValueError, ImportError) as e:
        logger.error(f"'{name}' Parquet 저장/읽기 실패: {e}")

    if timings:
        logger.info(f"'{name}' 저장/재로딩 완료 (csv={csv_path}, parquet={parquet_path})")
    return timings


def print_comparison(name: str, timings: dict) -> None:
    """CSV vs Parquet 성능 비교 결과를 표 형태로 출력.
    한쪽 포맷이 실패해 값이 없으면 'N/A'로 표시한다."""
    if not timings:
        print(f"[{name}] 저장 결과 없음 (오류로 인해 비교 불가)")
        return

    def fmt_ms(key: str) -> str:
        return f"{timings[key]*1000:.2f}ms" if key in timings else "N/A"

    def fmt_bytes(key: str) -> str:
        return f"{timings[key]:,}B" if key in timings else "N/A"

    print(f"\n[{name}] CSV vs Parquet 성능 비교")
    print(f"  쓰기 시간   : CSV {fmt_ms('csv_write_sec')} "
          f"/ Parquet {fmt_ms('parquet_write_sec')}")
    print(f"  읽기 시간   : CSV {fmt_ms('csv_read_sec')} "
          f"/ Parquet {fmt_ms('parquet_read_sec')}")
    print(f"  파일 크기   : CSV {fmt_bytes('csv_size_bytes')} "
          f"/ Parquet {fmt_bytes('parquet_size_bytes')}")
