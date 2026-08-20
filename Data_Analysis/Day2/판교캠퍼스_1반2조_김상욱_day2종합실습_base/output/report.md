# NYC Yellow Taxi (2026-05) End2End 분석 리포트

- 생성 시각: 2026-08-04 16:17:21
- 원본 데이터: https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2026-05.parquet

## 1. 데이터 로딩 비교 (Pandas vs Polars)
- Pandas: shape=(4090836, 20), 로딩 0.70s, 메모리 608.8MB
- Polars: shape=(4090836, 20), 로딩 0.21s, 메모리 550.1MB
- 두 결과 shape 일치 여부: True

## 2. 결측치·중복·이상치 처리
- 원본 행 수: 300,000
- 컬럼별 결측치 개수 (isnull().sum()):
| 컬럼                  |   결측치 개수 |
|:----------------------|--------------:|
| tpep_pickup_datetime  |             0 |
| tpep_dropoff_datetime |             0 |
| passenger_count       |         70180 |
| trip_distance         |             0 |
| PULocationID          |             0 |
| DOLocationID          |             0 |
| payment_type          |             0 |
| fare_amount           |             0 |
| tip_amount            |             0 |
| total_amount          |             0 |
- 중복 제거: 0건
- 비정상값 제외: 16,319건
- 최종 행 수: 283,681

## 3. 기술통계
|                   |   mean |   std |   min |   25% |   50% |   75% |    max |
|:------------------|-------:|------:|------:|------:|------:|------:|-------:|
| trip_distance     |   3.55 |  4.24 |   0.1 |  1.11 |  1.96 |  4    |  96.5  |
| passenger_count   |   1.25 |  0.63 |   1   |  1    |  1    |  1    |   6    |
| fare_amount       |  21.44 | 17.04 |   3   | 10    | 16.3  | 26.41 | 300    |
| tip_amount        |   3.02 |  3.98 |   0   |  0    |  2.34 |  4.14 | 100    |
| total_amount      |  30.54 | 21.26 |   0   | 17.7  | 23.94 | 34.85 | 373.31 |
| trip_duration_min |  18.91 | 15.43 |   1   |  8.93 | 14.73 | 23.57 | 179.68 |

## 4. 상관계수
|                   |   trip_distance |   passenger_count |   fare_amount |   tip_amount |   total_amount |   trip_duration_min |
|:------------------|----------------:|------------------:|--------------:|-------------:|---------------:|--------------------:|
| trip_distance     |            1    |              0.03 |          0.88 |         0.44 |           0.86 |                0.77 |
| passenger_count   |            0.03 |              1    |          0.05 |         0.04 |           0.05 |                0.01 |
| fare_amount       |            0.88 |              0.05 |          1    |         0.46 |           0.96 |                0.78 |
| tip_amount        |            0.44 |              0.04 |          0.46 |         1    |           0.62 |                0.34 |
| total_amount      |            0.86 |              0.05 |          0.96 |         0.62 |           1    |                0.74 |
| trip_duration_min |            0.77 |              0.01 |          0.78 |         0.34 |           0.74 |                1    |

## 5. 시각화
- Seaborn 정적 차트: `dist_seaborn.png` (승차 거리 분포)
- Plotly 인터랙티브 차트: `group_plotly.html` (시간대별 평균 운임)

## 6. t-test (주중 vs 주말 평균 운임)
- 주중 평균: 21.66 / 주말 평균: 20.96
- t=10.4574, p=1.378e-25
- 해석: 유의미한 차이가 있다 (α=0.05)

## 7. 카이제곱 검정 (러시아워 여부 vs 고액 팁 여부)
- ML Pipeline이 피처로 쓰는 pickup_hour(시간대)가 실제로 팁 성향과 관계있는지 확인하기 위해 추가

| is_rush_hour   |     0 |     1 |
|:---------------|------:|------:|
| False          | 61864 | 58186 |
| True           | 34612 | 38933 |

- chi2=364.2457, dof=1, p=3.35e-81
- 해석: 서로 독립이 아니다 (연관이 있다) (α=0.05)

## 8. ML Pipeline (고액 팁 여부 분류)
- 학습/테스트 데이터 수: 154,876 / 38,719
- 고액 팁 기준 tip_pct 중앙값: 0.261
- Accuracy: 0.7212
- F1-score: 0.7470
- 저장된 모델: `tip_model.joblib`
