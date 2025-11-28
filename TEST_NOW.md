# 지금 바로 테스트 실행하기

## 방법 1: 컨테이너 접속 후 실행 (권장)

### 1단계: 컨테이너 접속
```bash
docker-compose exec app bash
```

### 2단계: 통합 테스트 실행
```bash
python scripts/test/test_integration.py
```

### 3단계: 결과 확인
테스트가 완료되면 다음 단계들이 실행됩니다:
- [1/7] 데이터베이스 초기화
- [2/7] 스캔 실행
- [3/7] PoC 재현
- [4/7] 신뢰도 점수 계산
- [5/7] 우선순위 계산 ⭐ (새로 추가됨)
- [6/7] 리포트 생성
- [7/7] 대시보드 확인

---

## 방법 2: 컨테이너 외부에서 실행 (Windows PowerShell)

```powershell
# PowerShell에서 실행
docker-compose exec app python scripts/test/test_integration.py
```

---

## 예상 출력

성공 시 다음과 같은 출력이 나옵니다:

```
INFO:__main__:============================================================
INFO:__main__:전체 파이프라인 통합 테스트 시작
INFO:__main__:============================================================

[1/7] 데이터베이스 초기화
INFO:src.database.connection:Database connected: postgres:5432/v2r
INFO:__main__:✓ 데이터베이스 연결 성공

[2/7] 스캔 실행
INFO:__main__:✓ 스캔 완료 (ID: X)

[3/7] PoC 재현
INFO:__main__:✓ PoC 재현 완료

[4/7] 신뢰도 점수 계산
INFO:__main__:✓ 신뢰도 점수: 60/100

[5/7] 우선순위 계산
INFO:__main__:✓ 우선순위 계산 완료: 1개 처리
INFO:__main__:  - scan_id: 우선순위 X (점수: XX)

[6/7] 리포트 생성
INFO:__main__:✓ 리포트 생성 완료

[7/7] 대시보드 확인
INFO:__main__:✓ 대시보드 모듈 로드 확인
```

---

## 문제 해결

### 컨테이너가 실행 중이 아닌 경우
```bash
docker-compose up -d
```

### 데이터베이스 연결 실패
```bash
docker-compose restart postgres
docker-compose exec app python scripts/test/test_integration.py
```

### 모듈 import 오류
```bash
# 컨테이너 내부에서
cd /app
python scripts/test/test_integration.py
```

---

## 테스트 후 확인 사항

### 1. 대시보드에서 확인
```bash
# 컨테이너 내부에서
streamlit run src/dashboard/app.py --server.port 8501 --server.address 0.0.0.0
```

브라우저에서 `http://localhost:8501` 접속하여:
- 취약점 리스트에서 우선순위 확인
- CCE 점검 결과 페이지 확인

### 2. 데이터베이스 확인
```bash
docker-compose exec postgres psql -U v2r -d v2r

# 쿼리 실행
SELECT id, scan_id, target_host, severity FROM scan_results ORDER BY created_at DESC LIMIT 5;
SELECT id, reproduction_id, status, reliability_score FROM poc_reproductions ORDER BY created_at DESC LIMIT 5;
```

---

## 새로 추가된 기능 테스트

### 우선순위 계산 테스트
```bash
# 컨테이너 내부에서
python -c "
from src.pipeline.priority_pipeline import PriorityPipeline
pipeline = PriorityPipeline()
result = pipeline.calculate_priorities_for_scans()
print(result)
"
```

### CCE 점검 테스트
```bash
# 컨테이너 내부에서
python scripts/test/test_cce_checker.py --host 127.0.0.1 --username root
```

---

지금 바로 실행해보세요! 🚀

