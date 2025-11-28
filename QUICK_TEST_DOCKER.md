# Docker 환경 빠른 테스트 가이드

## 🚀 빠른 시작 (3단계)

### 1단계: 컨테이너 접속

```bash
docker-compose exec app bash
```

### 2단계: 통합 테스트 실행

```bash
python scripts/test/test_integration.py
```

### 3단계: 결과 확인

```bash
# 대시보드 실행
streamlit run src/dashboard/app.py --server.port 8501 --server.address 0.0.0.0
```

브라우저에서 `http://localhost:8501` 접속

---

## 📋 상세 테스트 방법

### 방법 1: 통합 테스트 (권장)

```bash
# 컨테이너 접속
docker-compose exec app bash

# 통합 테스트 실행
python scripts/test/test_integration.py
```

**테스트 내용:**
- ✅ 데이터베이스 초기화
- ✅ 스캔 실행 (Nmap)
- ✅ PoC 재현 (target_host 자동 추출)
- ✅ 신뢰도 점수 계산
- ✅ 리포트 생성
- ✅ 대시보드 확인

### 방법 2: 빠른 테스트 스크립트 (컨테이너 외부에서)

```bash
# 프로젝트 루트에서 실행
bash scripts/test/quick_test.sh
```

### 방법 3: 개별 모듈 테스트

#### 데이터베이스 연결 확인
```bash
docker-compose exec app python -c "
from src.database import get_db
db = get_db()
print('✓ 연결 성공' if db.test_connection() else '✗ 연결 실패')
"
```

#### 스캔 테스트
```bash
docker-compose exec app python -c "
from src.pipeline.scanner_pipeline import ScannerPipeline
scanner = ScannerPipeline()
result = scanner.run_nmap_scan(target='127.0.0.1', ports='22,80,443')
print(result)
"
```

#### PoC 재현 테스트
```bash
docker-compose exec app python -c "
from src.pipeline.poc_pipeline import POCPipeline
poc = POCPipeline()
result = poc.run_poc_reproduction(
    scan_result_id=1,
    poc_script='print(\"test\")',
    poc_type='test',
    cve_id='CVE-TEST-2024-0001'
)
print(result)
"
```

---

## 🔍 결과 확인

### 로그 확인
```bash
# 실시간 로그
docker-compose logs -f app

# 최근 로그
docker-compose logs --tail=100 app
```

### 데이터베이스 확인
```bash
# PostgreSQL 접속
docker-compose exec postgres psql -U v2r -d v2r

# 쿼리 실행
SELECT * FROM scan_results ORDER BY created_at DESC LIMIT 5;
SELECT * FROM poc_reproductions ORDER BY created_at DESC LIMIT 5;
```

### 리포트 파일 확인
```bash
# 리포트 디렉토리
docker-compose exec app ls -la reports/

# 리포트 목록
docker-compose exec app find reports/ -name "*.docx" -o -name "*.xml" -o -name "*.json"
```

---

## ⚠️ 문제 해결

### 데이터베이스 연결 실패
```bash
# PostgreSQL 상태 확인
docker-compose ps postgres

# 로그 확인
docker-compose logs postgres

# 재시작
docker-compose restart postgres
```

### 모듈 import 오류
```bash
# PYTHONPATH 확인
docker-compose exec app echo $PYTHONPATH

# 프로젝트 루트 확인
docker-compose exec app pwd
```

### Docker 권한 오류 (PoC 격리)
- 정상 동작: 컨테이너 내부에서 Docker 사용 불가
- PoC 재현은 mock 모드로 동작 (테스트 환경에서는 정상)

---

## 📝 테스트 체크리스트

```bash
# 1. 컨테이너 실행 확인
docker-compose ps

# 2. 컨테이너 접속
docker-compose exec app bash

# 3. 데이터베이스 연결 확인
python -c "from src.database import get_db; db = get_db(); print('OK' if db.test_connection() else 'FAIL')"

# 4. 통합 테스트 실행
python scripts/test/test_integration.py

# 5. 대시보드 실행
streamlit run src/dashboard/app.py --server.port 8501 --server.address 0.0.0.0
```

---

## 🎯 예상 결과

### 성공 시 출력 예시
```
INFO:__main__:============================================================
INFO:__main__:전체 파이프라인 통합 테스트 시작
INFO:__main__:============================================================

[1/6] 데이터베이스 초기화
INFO:src.database.connection:Database connected: postgres:5432/v2r
INFO:__main__:✓ 데이터베이스 연결 성공

[2/6] 스캔 실행
INFO:__main__:✓ 스캔 완료 (ID: 1)

[3/6] PoC 재현
INFO:__main__:✓ PoC 재현 완료

[4/6] 신뢰도 점수 계산
INFO:__main__:✓ 신뢰도 점수: 60/100

[5/6] 리포트 생성
INFO:__main__:✓ 리포트 생성 완료

[6/6] 대시보드 확인
INFO:__main__:✓ 대시보드 모듈 로드 확인
```

---

## 💡 팁

1. **첫 실행 시**: 데이터베이스 초기화에 시간이 걸릴 수 있습니다
2. **Docker 경고**: `version: '3.8'` 경고는 무시해도 됩니다
3. **PoC 격리**: Docker 사용 불가 시 mock 모드로 동작 (정상)
4. **리포트**: `reports/` 디렉토리에 생성됩니다

