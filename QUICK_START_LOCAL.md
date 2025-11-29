# 로컬 PC 빠른 시작 가이드

## 개요

로컬 PC에서 V2R Docker 서비스를 실행하고, EC2에서 접속하여 사용하는 방식입니다.

## 빠른 시작 (3단계)

### 1단계: 로컬 PC에서 Docker 실행

```bash
# 프로젝트 디렉토리로 이동
cd V2R

# Docker 서비스 시작
docker-compose up -d

# 또는 스크립트 사용 (Windows: Git Bash 또는 WSL)
bash scripts/local/start_local.sh
```

### 2단계: 공인 IP 확인

```bash
# Windows PowerShell
curl ifconfig.me

# 또는 브라우저에서
# https://whatismyipaddress.com/
```

### 3단계: EC2에서 접속

```bash
# EC2에서
export LOCAL_PC_IP=<1단계에서-확인한-공인IP>

# 연결 테스트
bash scripts/local/connect_from_ec2.sh

# 환경 변수 설정
export DB_HOST=$LOCAL_PC_IP
export DB_PORT=5432
export DB_NAME=v2r
export DB_USER=v2r
export DB_PASSWORD=v2r_password
```

## 서비스 접속 정보

로컬 PC에서 실행된 서비스:

- **PostgreSQL**: `localhost:5432` (로컬) / `<공인IP>:5432` (EC2에서)
- **API 서버**: `http://localhost:8000` (로컬) / `http://<공인IP>:8000` (EC2에서)
- **대시보드**: `http://localhost:8501` (로컬) / `http://<공인IP>:8501` (EC2에서)
- **DVWA**: `http://localhost:80` (로컬) / `http://<공인IP>:80` (EC2에서, `--profile test` 사용 시)

## 테스트 실행

### 로컬 PC에서

```bash
# 기본 테스트
docker-compose exec app python scripts/test/run_full_test.py

# 취약 환경 대상 스캔
docker-compose exec app python scripts/test/run_full_test.py \
  --scan-target http://localhost:80
```

### EC2에서

```bash
# 환경 변수 설정 후
python scripts/test/run_full_test.py \
  --scan-target http://<공인IP>:80
```

## 문제 해결

### 포트 충돌

```bash
# 포트 사용 확인
# Windows
netstat -ano | findstr :5432

# 포트 변경: docker-compose.yml에서 수정
ports:
  - "0.0.0.0:15432:5432"
```

### 방화벽 설정

Windows 방화벽에서 다음 포트 허용:
- 5432 (PostgreSQL)
- 8000 (API)
- 8501 (대시보드)
- 80 (DVWA)

```powershell
# PowerShell (관리자 권한)
New-NetFirewallRule -DisplayName "V2R PostgreSQL" -Direction Inbound -LocalPort 5432 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "V2R API" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "V2R Dashboard" -Direction Inbound -LocalPort 8501 -Protocol TCP -Action Allow
```

## 상세 가이드

더 자세한 내용은 [로컬 Docker 설정 가이드](docs/LOCAL_DOCKER_SETUP.md)를 참고하세요.

