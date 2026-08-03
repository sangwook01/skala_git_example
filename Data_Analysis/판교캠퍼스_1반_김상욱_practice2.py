"""
[Practice 2] 파일 I/O, 예외 처리, Pydantic 검증 파이프라인
--------------------------------------------------------------
  Python_Practice2_Data_Error.json 임의로 생성한 데이터로 읽어 Pydantic v2
  스키마(SalesRecord)로 각 행을 검증

  1) safe_load_json() - 예외 처리를 포함한 원본 JSON 로딩 (파일 없으면 None)
     safe_load_csv() - 예외 처리를 포함한 CSV 로딩. valid 결과 재로딩에 사용
     (checkpoint가 지정하는 함수명이 safe_load_csv이므로, 파일 없음 -> None
     동작은 이 함수로 직접 검증)
  2) SalesRecord - month/region 필수(빈 값 불가), amount>0, category는 선택
  3) validate_records() - raw_data를 순회하며 valid/errors로 분리
  4) save_results() - valid는 CSV, errors는 JSON(ensure_ascii=False)으로 저장 후
     valid CSV를 safe_load_csv()로 재로딩하여 건수를 검증한다.
"""

import csv
import json
import logging
import os
from typing import Optional

from pydantic import BaseModel, Field, ValidationError, field_validator

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

RAW_DATA_PATH = "Python_Practice2_Data_Error.json"
VALID_OUTPUT_PATH = "valid_sales.csv"
ERRORS_OUTPUT_PATH = "invalid_sales.json"




# ---------- 2) Pydantic v2 스키마 ----------
class SalesRecord(BaseModel):
    """판매 레코드 스키마. month/region은 필수(빈 값 불가), amount는 0 초과,
    category는 없어도 되는 선택 필드."""

    month: str
    region: str
    category: Optional[str] = None
    amount: float = Field(gt=0)

    @field_validator("month", "region")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("빈 값은 허용되지 않습니다.")
        return v

    @field_validator("category", mode="before")
    @classmethod
    def blank_to_none(cls, v):
        """빈 문자열로 들어오는 category를 None으로 정규화."""
        return None if v in ("", None) else v


# ---------- 1) 예외 처리 + 파일 읽기 ----------
def safe_load_json(path):
    """원본 JSON 파일을 읽어 dict 리스트로 반환. 파일이 없거나 파싱에
    실패하면 None을 반환한다."""
    result = None
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("JSON 최상위 구조가 리스트가 아닙니다.")
        result = data
        logger.info(f"'{path}' 로딩 성공: {len(result)}건")
    except FileNotFoundError:
        logger.error(f"파일을 찾을 수 없습니다: {path}")
        result = None
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"JSON 파싱 오류: {e}")
        result = None
    finally:
        print("로딩 종료")
    return result


def safe_load_csv(path):
    """CSV 파일을 읽어 dict 리스트로 반환. 파일이 없으면 None 반환.
    valid 결과 저장 후 재로딩 검증에 사용된다."""
    result = None
    try:
        with open(path, newline="", encoding="utf-8") as f:
            result = list(csv.DictReader(f))
        logger.info(f"'{path}' 로딩 성공: {len(result)}건")
    except FileNotFoundError:
        logger.error(f"파일을 찾을 수 없습니다: {path}")
        result = None
    except csv.Error as e:
        logger.error(f"CSV 파싱 오류: {e}")
        result = None
    finally:
        print("로딩 종료")
    return result


# ---------- 3) 검증 파이프라인 (valid / errors 분리) ----------
def validate_records(raw_data):
    """raw_data를 순회하며 SalesRecord로 변환. 성공→valid, 실패→errors."""
    valid, errors = [], []
    for row in raw_data:
        try:
            valid.append(SalesRecord(**row))
        except ValidationError as e:
            logger.error(f"검증 실패: {row} -> {e}")
            errors.append({"row": row, "error": str(e)})
    return valid, errors


# ---------- 4) 결과 파일 저장 + 재로딩 확인 ----------
def save_results(valid, errors, valid_path=VALID_OUTPUT_PATH, errors_path=ERRORS_OUTPUT_PATH):
    """
    valid 레코드는 CSV로, errors는 JSON(ensure_ascii=False)으로 저장.
    valid가 0건이어도 SalesRecord 필드로 헤더만 있는 CSV를 생성해
    재로딩 시 safe_load_csv가 파일 없음(None)으로 오판하지 않도록 한다.
    """
    try:
        fieldnames = list(SalesRecord.model_fields.keys())
        valid_dicts = [record.model_dump() for record in valid]
        with open(valid_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(valid_dicts)

        with open(errors_path, "w", encoding="utf-8") as f:
            json.dump(errors, f, ensure_ascii=False, indent=2)

        logger.info(f"저장 완료: valid={len(valid_dicts)}건 -> {valid_path}, "
                    f"errors={len(errors)}건 -> {errors_path}")
    except OSError as e:
        logger.error(f"파일 저장 실패: {e}")


if __name__ == "__main__":

    # 1) 실제 운영 데이터(JSON) 로딩 (건수는 원본 데이터에 따라 달라짐 -> 하드코딩 금지)
    raw_data = safe_load_json(RAW_DATA_PATH)

    if raw_data is None:
        print("[경고] 원본 데이터를 로딩하지 못해 종료합니다.")
    else:
        # 3) 검증 파이프라인
        valid, errors = validate_records(raw_data)
        print(f"valid: {len(valid)}건 / errors: {len(errors)}건")
        assert len(valid) + len(errors) == len(raw_data), "valid+errors 합이 원본 건수와 다릅니다."

        # 4) 저장 + safe_load_csv로 재로딩 확인 (건수는 valid와 동적으로 비교)
        save_results(valid, errors)
        reloaded = safe_load_csv(VALID_OUTPUT_PATH)
        assert reloaded is not None and len(reloaded) == len(valid), "재로딩 건수가 valid 건수와 일치하지 않습니다."

        print("모든 assert 검증 통과")
