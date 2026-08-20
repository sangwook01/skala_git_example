# End-to-End Data Analysis Project: Cost-Effective Taxi Ride Prediction

NYC Yellow Taxi Trip Data (2026-05)를 활용하여 **"어떤 조건에서 마일당 비용(cost per mile)이 저렴한 택시를 이용할 수 있는가?"**를 분석한 End-to-End 데이터 분석 프로젝트입니다.

데이터 전처리부터 EDA, 통계 분석, 머신러닝 모델링, 자동 보고서 생성까지 전체 분석 과정을 하나의 파이프라인으로 구현했습니다.

---

## Project Overview

### Dataset
- NYC Yellow Taxi Trip Data (2026-05)
- Format: Parquet
- Sample Size: 300,000 trips (default)

### Objective

실제 승객이 지불한 총 결제 금액을 기준으로 **가성비 좋은 택시 이용 조건**을 분석합니다.

핵심 지표는 다음과 같습니다.

```python
cost_per_mile = total_amount / trip_distance
```

`total_amount`를 사용하여 기본 요금뿐 아니라 공항 수수료, 혼잡 통행료 등 실제 결제 비용을 모두 반영했습니다.

---

## Hypotheses

| ID | Hypothesis | Method |
|----|------------|--------|
| H1 | Peak hours have higher cost per mile than non-peak hours | One-sided t-test |
| H2 | Trips with surcharges have higher cost per mile | One-sided t-test |
| H3 | Distance and cost-effectiveness have a non-linear relationship | Distance bucket analysis |
| H4 | Weekend and late-night patterns affect cost-effectiveness | Group comparison |

---

## Analysis Pipeline

```
Data Loading
        │
        ▼
Data Cleaning
        │
        ▼
Feature Engineering
        │
        ▼
Exploratory Data Analysis
        │
        ▼
Statistical Analysis
        │
        ▼
Machine Learning
        │
        ▼
Automatic Report Generation
```

---

## Machine Learning

Classification Target

```
is_cost_effective
```

Definition

- cost_per_mile ≤ Median → Cost-effective
- cost_per_mile > Median → Not Cost-effective

Model

- RandomForestClassifier

Evaluation Metrics

- Accuracy
- Precision
- Recall
- F1-score
- Feature Importance

---

## Project Structure

```
end2end_taxi/
│
├── output/
│   ├── report.md
│   ├── cost_effective_model.joblib
│   ├── *.png
│   ├── *.html
│   └── yellow_tripdata_2026-05.parquet
│
├── requirements.txt
├── nyc_taxi_e2e.py
└── README.md
```

---

## Visualizations

The project automatically generates:

- Distribution of cost per mile
- Distance vs Cost scatter plot
- Peak vs Non-Peak boxplot
- Surcharge comparison boxplot
- Distance bucket analysis
- Weekday × Hour heatmap
- Correlation heatmap
- Interactive Plotly visualization
- ML performance summary table

---

## Output

Running the project generates:

| File | Description |
|------|-------------|
| report.md | Automatically generated analysis report |
| cost_effective_model.joblib | Trained RandomForest pipeline |
| *.png | EDA visualizations |
| group_plotly.html | Interactive visualization |
| yellow_tripdata_2026-05.parquet | Cached dataset |

---

## Requirements

- Python 3.11+
- pandas
- polars
- numpy
- scipy
- scikit-learn
- matplotlib
- seaborn
- plotly
- joblib
- requests

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Run

```bash
python nyc_taxi_e2d.py
```

The dataset is automatically downloaded during the first execution and cached under the `output/` directory.

---

## Key Features

- End-to-End Data Analysis Pipeline
- Data Cleaning & Feature Engineering
- Statistical Hypothesis Testing
- Machine Learning Classification
- Automated Markdown Report Generation
- Publication-quality Visualizations

---

## Technologies

- Python
- Pandas
- Polars
- NumPy
- SciPy
- Scikit-learn
- Matplotlib
- Seaborn
- Plotly
- Joblib

---

## Notes

Detailed statistical interpretations, hypothesis testing results, and model evaluation are automatically documented in `output/report.md`.