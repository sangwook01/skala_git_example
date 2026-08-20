# End2End 데이터 분석 프로젝트 - NYC Yellow Taxi (2026-05)

[Day 2 종합 실습] 요구사항을 NYC Yellow Taxi Trip Data(2026년 5월, parquet)로 구현한 프로젝트입니다.

## 데이터셋 선택 이유

세 가지 후보(Adult Census Income, Stack Overflow Survey 2024, NYC Yellow Taxi) 중 택시 데이터를 선택했습니다.

- **Pandas vs Polars 비교**가 의미를 가지려면 데이터가 커야 하는데, 택시 데이터는 월간 수백만 행이라 로딩 속도·메모리 차이가 실제로 드러납니다. Adult(3.2만 행)나 Survey는 규모가 작아 차이가 거의 안 보입니다.
- **결측치·이상치 처리**도 실전 성격이 강합니다. 음수 운임, 거리 0인 트립, 몇 시간짜리 비정상 운행 기록처럼 현업에서 마주치는 지저분함을 그대로 다룰 수 있습니다.
- **ML 타겟**을 데이터셋이 미리 정해주지 않아서, 직접 파생 변수(운행시간·시간대·팁 비율)를 설계해야 했습니다. Adult의 "소득 50K 초과 여부"는 이미 정형화된 문제라 스스로 설계하는 경험이 덜합니다.
- **통계 검정**도 "주중 vs 주말 운임"처럼 민감한 속성(성별·인종 등) 없이 비즈니스적으로 자연스러운 비교가 가능합니다.

단점은 파일이 크고(다운로드·로딩 시간), PULocationID처럼 범주가 약 260개인 컬럼을 다뤄야 한다는 점인데, "End2End"라는 과제 취지에는 오히려 더 맞다고 판단했습니다.

## 요구사항 대응표

| 항목 | 구현 위치 | 비고 |
|---|---|---|
| Pandas/Polars 비교 로딩 | `load_with_pandas_and_polars()` | shape·로딩시간·메모리 비교, shape 일치 여부 검증 |
| 결측치·중복 처리 | `clean_data()` | `isnull().sum()`을 컬럼별로 출력/저장 |
| 기본 EDA | `basic_eda()` | 평균·표준편차·분위수 |
| Seaborn 정적 차트 | `plot_seaborn_distribution()` | 승차 거리 분포 (히스토그램+KDE) |
| Plotly 인터랙티브 차트 | `plot_plotly_group_comparison()` | 시간대별 평균 운임 (그룹비교) |
| 상관계수 | `compute_correlation()` | 주요 수치형 컬럼 |
| t-test | `run_ttest_weekday_weekend()` | 주중 vs 주말 평균 운임, Welch's t-test |
| 카이제곱 검정 (추가) | `run_chi2_rushhour_tip()` | 러시아워 여부 vs 고액 팁 여부 - ML 피처(pickup_hour)의 타당성 검증용 |
| ML Pipeline | `build_ml_pipeline()` | ColumnTransformer+Pipeline, 고액 팁 여부 이진분류, Accuracy/F1, joblib 저장 |
| 자동화 | `generate_report()` | 위 모든 결과를 `report.md`로 자동 생성 |

카이제곱 검정은 필수 항목은 아니지만, ML Pipeline이 `pickup_hour`를 피처로 쓰면서도 정작 "시간대가 팁 성향과 실제로 관계있는지"는 검증한 적이 없어서 추가했습니다. t-test는 연속형(운임) 비교, 카이제곱은 범주형(러시아워 여부·고액 팁 여부) 비교라 통계 기법도 겹치지 않게 구성했습니다.

## 실행 방법

```bash
pip install -r requirements.txt
python nyc_taxi_e2e.py
```

원본 parquet은 처음 실행 시 `output/` 폴더에 다운로드되어 캐시되며, 이후 재실행 시 재다운로드하지 않습니다.

## 주요 설정값 (`nyc_taxi_e2e.py` 상단)

- `SAMPLE_N = 300_000`: 월간 전체 데이터(수백만 행) 중 일부만 랜덤 샘플링해서 사용합니다. 전체 데이터로 돌리려면 `None`으로 변경하세요 (메모리/속도에 유의).
- `TOP_N_ZONES = 20`: `PULocationID`(약 260개 구역)를 그대로 원-핫 인코딩하면 차원이 과도하게 커지므로, 등장 빈도 상위 N개만 개별 범주로 쓰고 나머지는 `OTHER`로 묶습니다.

## 산출물 (`output/` 폴더)

- `yellow_tripdata_2026-05.parquet` - 다운로드 캐시
- `dist_seaborn.png` - Seaborn 정적 차트
- `group_plotly.html` - Plotly 인터랙티브 차트
- `tip_model.joblib` - 저장된 sklearn Pipeline 모델
- `report.md` - 데이터 로딩 비교/결측치 처리/EDA/시각화/통계 검정/ML 결과를 정리한 자동 생성 리포트

## 의존성 미설치 시 동작

각 라이브러리는 import 시점에 개별적으로 예외 처리되어 있어서, 하나가 없어도 나머지 단계는 계속 실행됩니다(해당 단계만 "미설치로 건너뜀" 메시지를 출력). 전체 기능을 쓰려면 `requirements.txt`의 패키지를 모두 설치하세요.

## 제출 관련 참고

- 코드 제출 시 이 폴더(`end2end_taxi/`)째로 `캠퍼스명_반_이름_실습명.zip` 형식으로 압축
- PDF 제출용 실행결과 캡처, 코드 분석에 대한 본인 의견(개선점 등)은 실제 실행 후 별도로 작성 필요
