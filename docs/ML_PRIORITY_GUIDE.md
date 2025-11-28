# ML 우선순위 모델 가이드

## 개요

XGBoost 기반 ML 모델을 사용하여 취약점의 우선순위를 자동으로 계산합니다.

## 우선순위 시스템

### 우선순위 레벨 (1-5)
- **1 (최우선)**: Critical 심각도 + 높은 신뢰도 또는 PoC 성공
- **2**: Critical 심각도 또는 High + PoC 성공
- **3**: High 심각도 또는 Medium + 높은 신뢰도
- **4**: Medium 심각도 또는 Low + PoC 존재
- **5 (낮음)**: 그 외

### 우선순위 점수 (0-100)
- 우선순위 1 = 100점
- 우선순위 2 = 80점
- 우선순위 3 = 60점
- 우선순위 4 = 40점
- 우선순위 5 = 20점

## 특징 (Features)

1. **심각도 점수** (0-4): Critical=4, High=3, Medium=2, Low=1, Info=0
2. **신뢰도 점수** (0-1): 0-100 범위를 0-1로 정규화
3. **CVE 개수** (0-1): 최대 10개로 제한 후 정규화
4. **PoC 존재 여부** (0 or 1)
5. **PoC 재현 성공 여부** (0 or 1)
6. **발견 후 경과 일수** (0-1): 최대 365일로 제한 후 정규화

## 사용 방법

### 1. 파이프라인에서 자동 계산

```python
from src.pipeline.priority_pipeline import PriorityPipeline

pipeline = PriorityPipeline()
result = pipeline.calculate_priorities_for_scans([scan_result_id])
```

### 2. 개별 취약점 우선순위 계산

```python
from src.ml import PriorityModel

model = PriorityModel()
vulnerability = {
    "severity": "Critical",
    "cve_list": ["CVE-2024-0001"],
    "reliability_score": 85,
    "has_poc": True,
    "poc_status": "success"
}
result = model.predict_priority(vulnerability)
print(f"우선순위: {result['priority']}, 점수: {result['priority_score']}")
```

### 3. 대시보드에서 확인

1. 대시보드 실행: `streamlit run src/dashboard/app.py`
2. "취약점 리스트" 페이지에서 우선순위 열 확인
3. 우선순위 필터로 필터링 가능

## 모델 학습 (선택)

기본적으로 규칙 기반 모델을 사용하지만, 학습 데이터가 있으면 XGBoost 모델을 학습할 수 있습니다:

```python
from src.ml import PriorityModel

model = PriorityModel()

# 학습 데이터 준비
training_data = [
    {"severity": "Critical", "reliability_score": 90, ...},
    # ...
]
labels = [1, 2, 3, ...]  # 우선순위 레이블 (1-5)

# 모델 학습
model.train(training_data, labels)
```

## Fallback 모드

XGBoost가 설치되지 않았거나 모델이 없을 경우, 규칙 기반 모델로 자동 전환됩니다:

- Critical + 신뢰도 80+ 또는 PoC 성공 → 우선순위 1
- Critical 또는 High + PoC 성공 → 우선순위 2
- High 또는 Medium + 신뢰도 60+ → 우선순위 3
- Medium 또는 Low + PoC 존재 → 우선순위 4
- 그 외 → 우선순위 5

## 데이터베이스 저장

우선순위 정보는 `scan_results.normalized_result.metadata`에 저장됩니다:

```json
{
  "metadata": {
    "priority": 1,
    "priority_score": 100,
    "priority_confidence": 85.5
  }
}
```

## 통합 테스트

```bash
python scripts/test/test_integration.py
```

테스트에서 우선순위 계산 단계가 포함됩니다.

