# V2R 빠른 시작 가이드

## 필수 요구사항

- Docker 20.10 이상
- Docker Compose 2.0 이상
- Git

## 기본 명령어

### 1. 환경 시작

```bash
# Docker 서비스 시작
docker-compose up -d

# 서비스 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f
```

### 2. 데이터베이스 초기화

```bash
# 데이터베이스 스키마 초기화
docker-compose exec app python scripts/utils/init_db.py

# 데이터베이스 완전 리셋 (모든 데이터 삭제)
docker-compose exec app python scripts/utils/reset_db.py
```

### 3. CVE-Lab 스캔

```powershell
# PowerShell에서 실행 (Windows)
.\scripts\scan_cve_lab.ps1
```

또는 직접 실행:

```bash
# 통합 스캔 (CCE 점검 포함)
docker-compose exec app python scripts/test/scan_cve_lab_full.py

# CCE 점검 제외
docker-compose exec app python scripts/test/scan_cve_lab_full.py --no-cce

# 데이터베이스 초기화와 함께 실행
docker-compose exec app python scripts/test/scan_cve_lab_full.py --init-db
```

### 4. 대시보드 실행

```bash
# Streamlit 대시보드 시작
docker-compose exec app streamlit run src/dashboard/app.py

# 브라우저에서 접속: http://localhost:8501
```

### 5. 테스트 실행

```bash
# 스캐너 단위 테스트
docker-compose exec app python src/scanner/test_scanner.py

# 전체 시스템 통합 테스트
docker-compose exec app python scripts/test/run_full_test.py

# 파이프라인 테스트
docker-compose exec app python scripts/test/test_pipeline.py
```

### 6. 컨테이너 접속

```bash
# app 컨테이너에 접속
docker-compose exec app /bin/bash

# PostgreSQL에 접속
docker-compose exec postgres psql -U v2r -d v2r
```

### 7. 서비스 관리

```bash
# 서비스 중지
docker-compose down

# 서비스 재시작
docker-compose restart

# 이미지 재빌드
docker-compose build --no-cache
docker-compose up -d

# 컨테이너 및 볼륨 완전 삭제
docker-compose down -v
docker system prune -f
```

## Makefile 사용 (선택)

```bash
# 도움말 보기
make help

# 서비스 시작
make up

# 서비스 중지
make down

# 로그 보기
make logs

# 컨테이너 접속
make shell

# 데이터베이스 접속
make db-shell

# 테스트 실행
make test
make test-full

# 환경 초기화
make init

# 완전 정리
make clean
```

## 주요 서비스 포트

- **PostgreSQL**: `localhost:5432`
- **Streamlit 대시보드**: `http://localhost:8501`
- **API 서버**: `http://localhost:8000`
- **DVWA** (테스트용): `http://localhost:8080` (프로파일 필요)

## 환경 변수 설정

`.env` 파일을 생성하여 환경 변수를 설정할 수 있습니다:

```env
# 데이터베이스
DB_HOST=postgres
DB_PORT=5432
DB_NAME=v2r
DB_USER=v2r
DB_PASSWORD=v2r_password

# LLM (선택)
OPENAI_API_KEY=your_api_key_here
LLM_MODEL=gpt-4

# AWS (선택)
AWS_REGION=ap-northeast-2
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
S3_BUCKET_NAME=
```

## 문제 해결

### Docker 소켓 접근 오류

```bash
# Docker 소켓 권한 확인
docker ps

# Windows에서 Docker Desktop 실행 확인
```

### 데이터베이스 연결 오류

```bash
# PostgreSQL 컨테이너 상태 확인
docker-compose ps postgres

# PostgreSQL 로그 확인
docker-compose logs postgres

# PostgreSQL 재시작
docker-compose restart postgres
```

### Nuclei 템플릿 오류

```bash
# Nuclei 설치 확인
docker-compose exec app nuclei -version

# 템플릿 업데이트
docker-compose exec app nuclei -update-templates
```

## 추가 정보

- 프로젝트 구조: `docs/PROJECT_STRUCTURE.md`
- PoC 목록: `docs/POC_LIST.md`
- 프로젝트 진행 상황: `docs/PROJECT_KANBAN.md`

