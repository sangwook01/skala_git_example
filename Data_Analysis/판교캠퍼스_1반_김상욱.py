"""
[Practice 1 - 심화 실습] 자료구조 집계 / 컴프리헨션 / 제너레이터

재사용성을 위해 함수로 아래 내용에 대해서 작성
--------------------------------------------------------------
  1) 리스트/딕셔너리 컴프리헨션으로 amount>=1000 거래 필터링 및 지역별 총매출 집계
  2) Counter로 지역별 거래 건수, defaultdict로 카테고리별 amount 리스트 집계
  3) amount>1000 행만 yield하는 제너레이터를 작성하고 리스트 대비 메모리 크기 비교
  4) month·category 기준 그룹핑(컴프리헨션 + defaultdict)으로 월별 카테고리 매출 집계를 수행
  
  => 각 항목은 brute-force 방식으로 재계산한 결과와 assert 비교하여 검증
"""

import sys
import json
from collections import Counter, defaultdict

DATA_PATH = "Python_Practice1_Data.json"

# ---------- 0) JSON 데이터 로드 ----------
def load_sales(path=DATA_PATH):
    """
    JSON 파일에서 판매 데이터를 로드
    파일/형식 오류 시 빈 리스트 반환
    """
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"[오류] 데이터 파일을 찾을 수 없습니다: {path}")
        return []
    except json.JSONDecodeError as e:
        print(f"[오류] JSON 파싱 실패: {e}")
        return []

    if not isinstance(data, list):
        print("[오류] 데이터 형식이 리스트가 아닙니다.")
        return []
    return data


# ---------- 1) 리스트/딕셔너리 컴프리헨션 ----------
def filter_high_amount(sales, threshold=1000):
    """
    amount >= threshold 인 거래만 리스트 컴프리헨션으로 필터링
    """
    return [s for s in sales if s.get("amount", 0) >= threshold]


def region_totals(filtered_sales):
    """
    필터링된 거래를 지역별 총매출 dict로 집계 (딕셔너리 컴프리헨션)
    """
    regions = {s["region"] for s in filtered_sales}
    return {
        region: sum(s["amount"] for s in filtered_sales if s["region"] == region)
        for region in regions
    }


# ---------- 2) Counter + defaultdict ----------
def region_transaction_counts(sales):
    '''
    지역별 전체 거래 건수를 Counter로 집계
    '''
    return Counter(s["region"] for s in sales)


def category_amount_lists(sales):
    '''
    카테고리별 amount 리스트를 defaultdict(list)로 집계
    '''
    result = defaultdict(list)
    for s in sales:
        result[s["category"]].append(s["amount"])
    return result


# ---------- 3) 제너레이터 - 메모리 비교 ----------
def high_amount_generator(sales, threshold=1000):
    '''   
    amount > threshold 인 행만 yield하는 제너레이터
    '''
    for s in sales:
        if s.get("amount", 0) > threshold:
            yield s


def compare_generator_vs_list_size(sales, threshold=1000):
    '''
    제너레이터 객체와 리스트 컴프리헨션 객체의 메모리 크기(sys.getsizeof)를 비교.
    제너레이터를 리스트로 변환하지 않고 객체 자체 크기만 비교
    '''
    gen = high_amount_generator(sales, threshold)
    list_version = [s for s in sales if s.get("amount", 0) > threshold]
    gen_size = sys.getsizeof(gen)
    list_size = sys.getsizeof(list_version)
    return gen_size, list_size, list_version

'''
<비교 결과>

제너레이터의 경우는 호출할 때 생성을 하지만 리스트의 경우는 모두 생성해두고 필요할 때 호출하기 때문에 객체 자체의 크기는 제너레이트가 리스트보다 크기가 작은 것을 알 수 있음.
대용량 데이터를 다룰 때, 제너레이터가 용이함
'''

# ---------- 4) 종합 - 월별 카테고리 매출 집계 (컴프리헨션 + defaultdict) ----------
def monthly_category_totals(sales):
    """
    month·category 기준으로 그룹핑한 총매출 dict.
    defaultdict로 누적 후 dict 컴프리헨션으로 결과를 정리
    """
    raw = defaultdict(float)
    for s in sales:
        raw[(s["month"], s["category"])] += s["amount"]
    return {key: round(value, 2) for key, value in raw.items()}


# ---------- 검증(brute-force 재계산과 assert 비교) ----------
def verify(sales, filtered, r_totals, counts, gen_size, list_size, top3, m_totals):
    """핵심 결과를 단순 반복문(brute-force)으로 재계산해 assert로 검증."""
    # region_totals 검증
    bf_region_totals = {}
    for s in filtered:
        bf_region_totals[s["region"]] = bf_region_totals.get(s["region"], 0) + s["amount"]
    assert r_totals == bf_region_totals, "region_totals 값 불일치"

    # Counter.most_common() 순서 검증
    bf_counts = {}
    for s in sales:
        bf_counts[s["region"]] = bf_counts.get(s["region"], 0) + 1
    assert counts.most_common() == sorted(bf_counts.items(), key=lambda x: x[1], reverse=True) \
        or dict(counts) == bf_counts, "Counter 결과 불일치"

    # generator 메모리 크기 검증
    assert gen_size < list_size, "제너레이터가 리스트보다 크거나 같음"

    # top3 내림차순 검증
    assert [amt for _, amt in top3] == sorted((amt for _, amt in top3), reverse=True), "top3 정렬 오류"

    # monthly_category_totals 검증
    bf_monthly = {}
    for s in sales:
        key = (s["month"], s["category"])
        bf_monthly[key] = bf_monthly.get(key, 0) + s["amount"]
    bf_monthly = {k: round(v, 2) for k, v in bf_monthly.items()}
    assert m_totals == bf_monthly, "monthly_category_totals 값 불일치"

    print("모든 assert 검증 통과")


if __name__ == "__main__":
    sales = load_sales()

    if not sales:
        print("[경고] 처리할 데이터가 없어 종료합니다.")
    else:
        # 1) 필터링 + 지역별 총매출
        filtered = filter_high_amount(sales, threshold=1000)
        r_totals = region_totals(filtered)
        print("1) amount>=1000 필터링 건수:", len(filtered))
        print("1) 지역별 총매출:", r_totals)
        print()
        # 2) Counter + defaultdict
        counts = region_transaction_counts(sales)
        cat_amounts = category_amount_lists(sales)
        print("2) 지역별 거래 건수(Counter):", counts.most_common())
        print("2) 카테고리별 amount 리스트:", dict(cat_amounts))
        print()

        # 3) 제너레이터 메모리 비교
        gen_size, list_size, list_version = compare_generator_vs_list_size(sales, threshold=1000)
        print(f"3) 제너레이터 크기: {gen_size} bytes / 리스트 크기: {list_size} bytes")
        print()

        # 상위 3건 (금액 내림차순) - filtered 기준
        top3_sorted = sorted(filtered, key=lambda s: s["amount"], reverse=True)[:3]
        top3 = [(s["region"], s["amount"]) for s in top3_sorted]
        print("top3 금액 내림차순:", top3)
        print()

        # 4) 월별 카테고리 매출 집계
        m_totals = monthly_category_totals(sales)
        print("4) 월별 카테고리 총매출:", m_totals)
        print()

        # 검증
        verify(sales, filtered, r_totals, counts, gen_size, list_size, top3, m_totals)
