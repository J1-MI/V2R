# Docker 환경에서 테스트 실행 가이드

## 사전 준비

### 1. Docker Compose 실행

```bash
# 프로젝트 루트에서
docker-compose up -d

# 컨테이너 상태 확인
docker-compose ps
```

### 2. 컨테이너 접속

```bash
# app 컨테이너 접속
docker-compose exec app bash
```

## 테스트 실행 방법

### 방법 1: 통합 테스트 (전체 파이프라인)

```bash
# 컨테이너 내부에서
python scripts/test/test_integration.py
```

**테스트 내용:**
- 데이터베이스 초기화
- 스캔 실행 (Nmap)
- PoC 재현 (target_host 자동 추출)
- 신뢰도 점수 계산
- 리포트 생성
- 대시보드 확인

### 방법 2: 취약 웹 서버 배포 테스트

```bash
# 외부 취약 웹 서버 IP 필요
python scripts/test/test_vulnerable_web_deployment.py --target <web_server_ip>
```

**예시:**
```bash
# 로컬 테스트 (127.0.0.1)
python scripts/test/test_vulnerable_web_deployment.py --target 127.0.0.1

# 실제 웹 서버 IP
python scripts/test/test_vulnerable_web_deployment.py --target 54.123.45.67
```

### 방법 3: CCE 서버 점검 테스트

```bash
# SSH 접속 정보 필요
python scripts/test/test_cce_checker.py \
  --host <server_ip> \
  --username ubuntu \
  --key-file /path/to/key.pem

# 또는 비밀번호 사용
python scripts/test/test_cce_checker.py \
  --host <server_ip> \
  --username root \
  --password your_password
```

### 방법 4: 개별 모듈 테스트

#### 스캔 테스트
```bash
python -c "
from src.pipeline.scanner_pipeline import ScannerPipeline
scanner = ScannerPipeline()
result = scanner.run_nmap_scan(target='127.0.0.1', ports='22,80,443')
print(result)
"
```

#### PoC 재현 테스트
```bash
python -c "
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

#### CCE 점검 테스트
```bash
python -c "
from src.compliance import CCEChecker
checker = CCEChecker()
result = checker.check_server(host='127.0.0.1', username='root', password='test')
print(result)
"
```

## 환경 변수 확인

```bash
# 컨테이너 내부에서
env | grep -E "DB_|AWS_|OPENAI"

# 또는 Python에서
python -c "
from src.config import *
print(f'DB_HOST: {DB_HOST}')
print(f'DB_NAME: {DB_NAME}')
print(f'DB_USER: {DB_USER}')
"
```

## 데이터베이스 연결 확인

```bash
# Python에서 직접 확인
python -c "
from src.database import get_db
db = get_db()
if db.test_connection():
    print('✓ 데이터베이스 연결 성공')
else:
    print('✗ 데이터베이스 연결 실패')
"
```

## 대시보드 실행

```bash
# 컨테이너 내부에서
streamlit run src/dashboard/app.py --server.port 8501 --server.address 0.0.0.0

# 브라우저에서 접속
# http://localhost:8501
```

## 문제 해결

### 데이터베이스 연결 실패

```bash
# PostgreSQL 컨테이너 상태 확인
docker-compose ps postgres

# 로그 확인
docker-compose logs postgres

# .env 파일 확인
cat .env
```

### Docker 권한 오류

```bash
# 컨테이너 내부에서 Docker 사용 불가 (정상)
# PoC 격리 재현은 mock 모드로 동작
```

### 모듈 import 오류

```bash
# PYTHONPATH 확인
echo $PYTHONPATH

# 프로젝트 루트에서 실행
cd /app
python scripts/test/test_integration.py
```

## 빠른 테스트 체크리스트

```bash
# 1. 컨테이너 접속
docker-compose exec app bash

# 2. 데이터베이스 연결 확인
python -c "from src.database import get_db; db = get_db(); print('OK' if db.test_connection() else 'FAIL')"

# 3. 통합 테스트 실행
python scripts/test/test_integration.py

# 4. 결과 확인
# - 로그에서 성공/실패 확인
# - 대시보드에서 결과 확인
```

## 테스트 결과 확인

### 로그 확인
```bash
# 컨테이너 로그
docker-compose logs app

# 실시간 로그
docker-compose logs -f app
```

### 리포트 파일 확인
```bash
# 리포트 디렉토리
ls -la reports/

# 리포트 내용 확인
cat reports/*.docx  # 바이너리 파일이므로 직접 읽기 어려움
```

### 데이터베이스 확인
```bash
# PostgreSQL 접속
docker-compose exec postgres psql -U v2r -d v2r

# 쿼리 실행
SELECT * FROM scan_results ORDER BY created_at DESC LIMIT 5;
SELECT * FROM poc_reproductions ORDER BY created_at DESC LIMIT 5;
```

