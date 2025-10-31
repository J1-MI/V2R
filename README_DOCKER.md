# Docker 환경 가이드

## 빠른 시작

```bash
# 1. 환경 초기화
make init

# 2. 서비스 시작
make up

# 3. 로그 확인
make logs

# 4. 컨테이너 접속
make shell
```

## Docker Compose 서비스

### postgres
- PostgreSQL 15 데이터베이스
- 포트: 5432 (호스트에서 접근 가능)
- 데이터 볼륨: `postgres_data`

### app
- 메인 애플리케이션 컨테이너
- Python + Conda 환경
- 포트: 8501 (Streamlit), 8000 (API)
- 코드 볼륨 마운트 (실시간 반영)

### scanner
- 스캐너 전용 컨테이너 (선택)
- 프로파일 필요: `docker-compose --profile scanner up scanner`

## 환경 변수

`.env` 파일에 다음 변수들을 설정할 수 있습니다:

```env
# 데이터베이스
DB_HOST=postgres
DB_PORT=5432
DB_NAME=v2r
DB_USER=v2r
DB_PASSWORD=your_password

# AWS
AWS_REGION=ap-northeast-2
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret

# LLM
OPENAI_API_KEY=your_key
LLM_MODEL=gpt-4

# 스캐닝
SCAN_TIMEOUT=300
MAX_CONCURRENT_SCANS=5
```

## Makefile 명령어

| 명령어 | 설명 |
|--------|------|
| `make build` | Docker 이미지 빌드 |
| `make up` | 모든 서비스 시작 |
| `make down` | 모든 서비스 중지 |
| `make logs` | 로그 보기 |
| `make shell` | app 컨테이너 접속 |
| `make db-shell` | PostgreSQL 접속 |
| `make test` | 스캐너 테스트 |
| `make init` | 환경 초기화 |
| `make init-db` | DB 스키마 초기화 |
| `make clean` | 컨테이너 및 볼륨 정리 |
| `make restart` | 서비스 재시작 |

## 개발 워크플로우

### 1. 코드 수정
- 로컬에서 코드 수정
- Docker 컨테이너에 자동 반영 (볼륨 마운트)

### 2. 테스트 실행
```bash
# 컨테이너 내에서 테스트
make shell
python src/scanner/test_scanner.py
```

### 3. 데이터베이스 작업
```bash
# PostgreSQL 접속
make db-shell

# 또는 스크립트 실행
docker-compose exec app python scripts/utils/init_db.py
```

## 프로덕션 배포

프로덕션 환경에서는 `docker-compose.prod.yml`을 사용:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 문제 해결

### 컨테이너가 시작되지 않음
```bash
# 로그 확인
make logs

# 재빌드
make rebuild
```

### 데이터베이스 연결 실패
```bash
# PostgreSQL 상태 확인
docker-compose ps postgres

# 재시작
docker-compose restart postgres
```

### 포트 충돌
`.env` 파일에서 포트를 변경하거나, 실행 중인 서비스 확인:
```bash
# 포트 사용 확인 (Linux)
sudo lsof -i :5432
```

## 볼륨 관리

### 데이터 백업
```bash
# PostgreSQL 데이터 백업
docker-compose exec postgres pg_dump -U v2r v2r > backup.sql
```

### 볼륨 정리
```bash
# 모든 볼륨 삭제 (주의: 데이터 손실)
make clean
```

## 네트워크

모든 서비스는 `v2r-network` 브리지 네트워크에 연결됩니다.
서비스 이름으로 내부 통신이 가능합니다 (예: `postgres:5432`).

