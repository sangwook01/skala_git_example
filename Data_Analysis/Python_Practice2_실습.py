"""
[Practice 2] 파일 I/O, 예외 처리, Pydantic 검증 파이프라인
--------------------------------------------------------------

  Python_Practice1_Data.csv(Sales)를 읽어 Pydantic v2 스키마(SalesRecord)로
  각 행을 검증

  1) safe_load_csv() - 예외 처리를 포함한 CSV 로딩 (파일 없으면 None)
  2) SalesRecord - month/region 필수, amount>0, category는 선택
  3) validate_records() - raw_data를 순회하며 valid/errors로 분리
  4) save_results() - valid는 CSV, errors는 JSON(ensure_ascii=False)으로 저장 후
     재로딩하여 건수를 검증
"""

import csv
import json
import logging
from typing import Optional

from pydantic import BaseModel, Field, ValidationError, field_validator

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

DATA_PATH = "Python_Practice1_Data.csv"
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
        """CSV에서 빈 문자열로 들어오는 category를 None으로 정규화."""
        return None if v in ("", None) else v


# ---------- 1) 예외 처리 + 파일 읽기 ----------
def safe_load_csv(path):
    """CSV 파일을 읽어 dict 리스트로 반환. 파일이 없으면 None 반환."""
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

    '''
    현재 교수님께서 주신 파일은 json형태의 파일이기 때문에 csv.DictReader로 읽으면 오류가 발생
    
    뒤의 결과들을 확인하기 위해서 임의로 json형태의 파일을 csv.DictReader로 읽어도 오류가 발생하지 않도록 아래에 json형태를 csv로 변경하는 함수 추가
    '''

# ---------- 1-1) json형태를 csv로 변경 ----------
def json_to_csv(json_path, csv_path):
    """JSON 파일을 읽어 CSV로 저장."""
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not data:
            logger.warning(f"'{json_path}' 파일이 비어 있습니다.")
            return

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

        logger.info(f"'{json_path}' -> '{csv_path}' 변환 완료: {len(data)}건")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"JSON 로딩 실패: {e}")
    except OSError as e:
        logger.error(f"CSV 저장 실패: {e}")

            
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
    """valid 레코드는 CSV로, errors는 JSON(ensure_ascii=False)으로 저장."""
    try:
        valid_dicts = [record.model_dump() for record in valid]
        if valid_dicts:
            with open(valid_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(valid_dicts[0].keys()))
                writer.writeheader()
                writer.writerows(valid_dicts)

        with open(errors_path, "w", encoding="utf-8") as f:
            json.dump(errors, f, ensure_ascii=False, indent=2)

        logger.info(f"저장 완료: valid={len(valid_dicts)}건 -> {valid_path}, "
                    f"errors={len(errors)}건 -> {errors_path}")
    except OSError as e:
        logger.error(f"파일 저장 실패: {e}")


if __name__ == "__main__":
    # 1) 존재하지 않는 파일 -> None 검증
    missing = safe_load_csv("no_such_file.csv")
    assert missing is None, "존재하지 않는 파일은 None을 반환해야 합니다."

    # 1-alpha) JSON 파일을 CSV로 변환
    json_to_csv("Python_Practice1_Data.json", "Python_Practice1_Data.csv")
    
    # 1) 정상 파일 로딩
    raw_data = safe_load_csv(DATA_PATH)

    if raw_data is None:
        print("[경고] 원본 데이터를 로딩하지 못해 종료합니다.")
    else:
        # 3) 검증 파이프라인
        valid, errors = validate_records(raw_data)
        print(f"valid: {len(valid)}건 / errors: {len(errors)}건")
        assert len(valid) == 4, "valid 건수가 예상과 다릅니다."
        assert len(errors) == 3, "errors 건수가 예상과 다릅니다."

        # 4) 저장 + 재로딩 확인
        save_results(valid, errors)
        reloaded = safe_load_csv(VALID_OUTPUT_PATH)
        assert reloaded is not None and len(reloaded) == 4, "재로딩 건수가 일치하지 않습니다."

        print("모든 assert 검증 통과")
