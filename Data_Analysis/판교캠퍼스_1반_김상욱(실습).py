"""
[Practice 1] 딕셔너리 리스트 필터링 실습
--------------------------------------------------
프로그램 개요:
  employees 리스트(딕셔너리 형태의 직원 데이터)를 대상으로
  1) 부서/급여 조건 필터링
  2) 나이 조건 필터링 후 (name, department) 튜플 리스트 생성
  3) 급여 내림차순 정렬 후 상위 N명 추출
  4) 부서별 평균 급여 계산
  네 가지 기능을 함수로 분리하여 구현
"""

from statistics import mean

employees = [
    {"name": "Alice", "department": "Engineering", "age": 30, "salary": 85000},
    {"name": "Bob", "department": "Marketing", "age": 25, "salary": 60000},
    {"name": "Charlie", "department": "Engineering", "age": 35, "salary": 95000},
    {"name": "David", "department": "HR", "age": 45, "salary": 70000},
    {"name": "Eve", "department": "Engineering", "age": 28, "salary": 78000},
]


def get_high_salary_engineers(data, department="Engineering", min_salary=80000):
    """부서==department 이고 salary>=min_salary 인 직원의 이름 리스트 반환."""
    try:
        return [
            emp["name"] for emp in data
            if emp.get("department") == department and emp.get("salary", 0) >= min_salary
        ]
    except (TypeError, AttributeError) as e:
        print(f"[오류] 직원 데이터 형식이 올바르지 않습니다: {e}")
        return []


def get_name_department_by_min_age(data, min_age=30):
    """age>=min_age 인 직원의 (name, department) 튜플 리스트 반환."""
    try:
        return [
            (emp["name"], emp["department"]) for emp in data
            if emp.get("age", 0) >= min_age
        ]
    except (TypeError, AttributeError) as e:
        print(f"[오류] 직원 데이터 형식이 올바르지 않습니다: {e}")
        return []


def get_top_n_by_salary(data, n=3):
    """salary 내림차순 정렬 후 상위 n명의 (name, salary) 튜플 리스트 반환."""
    if not data:
        print("[경고] 직원 데이터가 비어 있습니다.")
        return []
    try:
        sorted_emps = sorted(data, key=lambda emp: emp["salary"], reverse=True)
        return [(emp["name"], emp["salary"]) for emp in sorted_emps[:n]]
    except KeyError as e:
        print(f"[오류] salary 키가 없는 직원이 있습니다: {e}")
        return []


def get_average_salary_by_department(data):
    """부서별 평균 급여를 {department: avg_salary} 딕셔너리로 반환."""
    if not data:
        print("[경고] 직원 데이터가 비어 있습니다.")
        return {}
    try:
        departments = {emp["department"] for emp in data}
        return {
            dept: round(mean(emp["salary"] for emp in data if emp["department"] == dept), 2)
            for dept in departments
        }
    except (KeyError, ZeroDivisionError) as e:
        print(f"[오류] 평균 급여 계산 중 문제가 발생했습니다: {e}")
        return {}


if __name__ == "__main__":
    # 1. Engineering 부서 & salary >= 80000
    print("1) Engineering & 고소득(>=80000) 직원:", get_high_salary_engineers(employees))

    # 2. 30세 이상 직원의 (이름, 부서)
    print("2) 30세 이상 (이름, 부서):", get_name_department_by_min_age(employees))

    # 3. 급여 상위 3명
    print("3) 급여 상위 3명 (이름, 급여):", get_top_n_by_salary(employees, 3))

    # 4. 부서별 평균 급여
    print("4) 부서별 평균 급여:", get_average_salary_by_department(employees))
