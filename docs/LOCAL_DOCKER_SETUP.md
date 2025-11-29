# 로컬 PC Docker 실행 가이드

## 개요

V2R 프로젝트를 로컬 PC에서 Docker로 실행하고, EC2 서버에서 접속하여 사용하는 방식입니다.

## 아키텍처

```
로컬 PC (Docker 실행)
├── PostgreSQL (포트 5432)
├── V2R App (포트 8000, 8501)
└── 취약 환경 (DVWA 등, 포트 80)

EC2 서버 (클라이언트)
└── SSH를 통한 접속 및 테스트 실행
```

## 사전 준비

### 로컬 PC

1. **Docker Desktop 설치** (Windows/Mac) 또는 Docker Engine (Linux)
2. **Git 설치**
3. **포트 확인**: 5432, 8000, 8501, 80 포트가 사용 가능한지 확인

### EC2 서버

1. **SSH 접속 가능**
2. **Python 3.11+ 설치** (선택사항, 직접 테스트 시)

## 로컬 PC에서 Docker 실행

### 1. 프로젝트 클론 및 설정

```bash
# 프로젝트 디렉토리로 이동
cd /path/to/V2R

# 환경 변수 설정 (선택사항)
cp .env.example .env
# .env 파일 편집: DB 비밀번호, API 키 등
```

### 2. Docker 서비스 시작

```bash
# 기본 서비스 실행 (PostgreSQL + App)
docker-compose up -d

# 취약 환경 포함 실행
docker-compose --profile test up -d

# 로그 확인
docker-compose logs -f app
```

### 3. 서비스 확인

```bash
# 실행 중인 컨테이너 확인
docker-compose ps

# 서비스 상태 확인
docker-compose ps postgres app

# 로컬에서 접속 테스트
curl http://localhost:8501  # Streamlit 대시보드
curl http://localhost:8000  # API 서버
curl http://localhost:5432  # PostgreSQL (연결 테스트)
```

## EC2에서 접속 방법

### 방법 1: SSH 터널링 (권장)

로컬 PC의 Docker 서비스에 EC2에서 SSH 터널을 통해 접속:

```bash
# EC2에서 실행 (로컬 PC의 IP를 알고 있어야 함)
# 로컬 PC의 공인 IP 확인 필요

# SSH 터널 생성 (로컬 PC에서 실행)
ssh -R 5432:localhost:5432 ec2-user@<EC2-IP>
ssh -R 8000:localhost:8000 ec2-user@<EC2-IP>
ssh -R 8501:localhost:8501 ec2-user@<EC2-IP>
```

### 방법 2: 직접 네트워크 접속

로컬 PC의 방화벽을 열고 EC2에서 직접 접속:

#### 로컬 PC 설정

1. **방화벽 규칙 추가** (Windows)
   ```powershell
   # PowerShell (관리자 권한)
   New-NetFirewallRule -DisplayName "V2R PostgreSQL" -Direction Inbound -LocalPort 5432 -Protocol TCP -Action Allow
   New-NetFirewallRule -DisplayName "V2R API" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
   New-NetFirewallRule -DisplayName "V2R Dashboard" -Direction Inbound -LocalPort 8501 -Protocol TCP -Action Allow
   ```

2. **공인 IP 확인**
   ```bash
   # Windows
   curl ifconfig.me
   
   # 또는 브라우저에서
   # https://whatismyipaddress.com/
   ```

#### EC2에서 접속

```bash
# EC2에서 로컬 PC의 공인 IP로 접속
# 환경 변수 설정
export DB_HOST=<로컬PC-공인IP>
export DB_PORT=5432

# 또는 직접 테스트
curl http://<로컬PC-공인IP>:8501
```

### 방법 3: VPN/프록시 사용

로컬 PC와 EC2를 같은 네트워크에 연결 (VPN 사용)

## 테스트 실행

### 로컬 PC에서 직접 실행

```bash
# 컨테이너 내부에서 실행
docker-compose exec app python scripts/test/run_full_test.py

# 취약 환경 대상 스캔
docker-compose exec app python scripts/test/run_full_test.py \
  --scan-target http://localhost:80  # DVWA
```

### EC2에서 원격 실행

EC2에서 로컬 PC의 Docker 서비스에 접속하여 테스트:

```bash
# EC2에서
# 1. 로컬 PC의 공인 IP로 DB 연결 테스트
psql -h <로컬PC-공인IP> -p 5432 -U v2r -d v2r

# 2. API 테스트
curl http://<로컬PC-공인IP>:8000/health

# 3. 대시보드 접속
# 브라우저에서: http://<로컬PC-공인IP>:8501
```

## 환경 변수 설정

### 로컬 PC (.env 파일)

```env
# 데이터베이스 (로컬 Docker 내부)
DB_HOST=postgres
DB_PORT=5432
DB_NAME=v2r
DB_USER=v2r
DB_PASSWORD=v2r_password

# 외부 접근용 (EC2에서 사용)
DB_HOST_EXTERNAL=<로컬PC-공인IP>
DB_PORT_EXTERNAL=5432
```

### EC2에서 사용할 환경 변수

```bash
# EC2에서
export DB_HOST=<로컬PC-공인IP>
export DB_PORT=5432
export DB_NAME=v2r
export DB_USER=v2r
export DB_PASSWORD=v2r_password
```

## 네트워크 보안 고려사항

### 1. 방화벽 설정

로컬 PC의 방화벽에서 필요한 포트만 열기:
- 5432: PostgreSQL (가능하면 VPN/SSH 터널 사용 권장)
- 8000: API 서버
- 8501: 대시보드
- 80: 취약 환경 (테스트용)

### 2. 강력한 비밀번호 사용

```env
# .env 파일에서
DB_PASSWORD=<강력한-비밀번호>
POSTGRES_PASSWORD=<강력한-비밀번호>
```

### 3. IP 화이트리스트 (선택사항)

PostgreSQL의 `pg_hba.conf`에서 특정 IP만 허용:

```bash
# docker-compose.yml에서 postgres 서비스에 추가
command: postgres -c listen_addresses='*' -c host all all 0.0.0.0/0 md5
```

## 문제 해결

### 포트 충돌

```bash
# 포트 사용 중인 프로세스 확인
# Windows
netstat -ano | findstr :5432

# Linux/Mac
lsof -i :5432

# docker-compose.yml에서 포트 변경
ports:
  - "0.0.0.0:15432:5432"  # 15432로 변경
```

### 연결 실패

1. **방화벽 확인**: 로컬 PC 방화벽에서 포트 허용 확인
2. **공인 IP 확인**: 로컬 PC의 공인 IP가 변경되지 않았는지 확인
3. **Docker 네트워크 확인**: `docker-compose ps`로 서비스 실행 상태 확인

### EC2에서 접속 불가

```bash
# EC2에서 연결 테스트
telnet <로컬PC-공인IP> 5432
nc -zv <로컬PC-공인IP> 5432

# 실패 시 SSH 터널링 사용 권장
```

## 다음 단계

1. 로컬 PC에서 Docker 서비스 실행 확인
2. EC2에서 접속 테스트
3. 취약 환경(DVWA) 실행 및 스캔 테스트
4. 대시보드에서 결과 확인



