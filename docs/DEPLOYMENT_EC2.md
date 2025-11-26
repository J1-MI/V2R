# EC2 서버 배포 가이드

## 개요
V2R 프로젝트를 EC2 서버에 배포하고 테스트하는 방법을 안내합니다.

## 사전 준비사항

### 1. EC2 서버 정보 확인
- EC2 인스턴스 IP 주소 또는 도메인
- SSH 키 파일 경로 (.pem 파일)
- 사용자 이름 (일반적으로 `ubuntu` 또는 `ec2-user`)

### 2. 로컬 환경 준비
- SSH 클라이언트 설치
- Git 설치 (선택사항, 코드 전송용)

---

## 배포 방법

### 방법 1: Git을 사용한 배포 (권장)

#### 1단계: EC2 서버 접속
```bash
# Windows (PowerShell)
ssh -i "your-key.pem" ubuntu@your-ec2-ip

# Linux/Mac
ssh -i your-key.pem ubuntu@your-ec2-ip
```

#### 2단계: EC2 서버 환경 설정
```bash
# 시스템 업데이트
sudo apt-get update
sudo apt-get upgrade -y

# 필수 도구 설치
sudo apt-get install -y \
    python3.11 \
    python3-pip \
    git \
    docker.io \
    docker-compose \
    postgresql-client

# Docker 서비스 시작
sudo systemctl start docker
sudo systemctl enable docker

# Docker 그룹에 사용자 추가 (sudo 없이 docker 사용)
sudo usermod -aG docker $USER
# 재로그인 필요: exit 후 다시 ssh 접속
```

#### 3단계: 프로젝트 클론
```bash
# 프로젝트 디렉토리 생성
mkdir -p ~/projects
cd ~/projects

# Git 저장소 클론 (또는 SCP로 파일 전송)
git clone <your-repository-url> V2R
# 또는
# 로컬에서 압축 후 전송:
# tar -czf v2r.tar.gz V2R/
# scp -i your-key.pem v2r.tar.gz ubuntu@your-ec2-ip:~/
# EC2에서: tar -xzf v2r.tar.gz

cd V2R
```

#### 4단계: 환경 변수 설정
```bash
# .env 파일 생성
nano .env
# 또는
vim .env
```

`.env` 파일 내용:
```env
# 데이터베이스 설정
DB_HOST=localhost
DB_PORT=5432
DB_NAME=v2r
DB_USER=v2r
DB_PASSWORD=your_secure_password

# AWS 설정 (EC2에서 실행 중이므로 자동 인증 가능)
AWS_REGION=ap-northeast-2

# S3 설정 (선택)
S3_BUCKET_NAME=your-bucket-name
S3_EVIDENCE_PREFIX=evidence/

# LLM 설정 (선택)
OPENAI_API_KEY=your-openai-api-key
LLM_MODEL=gpt-4

# 스캐닝 설정
SCAN_TIMEOUT=300
MAX_CONCURRENT_SCANS=5
```

#### 5단계: Docker를 사용한 배포 (권장)

```bash
# Docker Compose로 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 컨테이너 접속
docker-compose exec app bash
```

#### 6단계: 로컬 설치 방식 (Docker 미사용 시)

```bash
# Python 가상환경 생성
python3 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install --upgrade pip
pip install -r requirements.txt

# PostgreSQL 설치 및 설정
sudo apt-get install -y postgresql postgresql-contrib
sudo -u postgres psql << EOF
CREATE DATABASE v2r;
CREATE USER v2r WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE v2r TO v2r;
\q
EOF

# 데이터베이스 스키마 초기화
python scripts/utils/init_db.py
```

---

### 방법 2: SCP를 사용한 파일 전송

#### 로컬에서 실행
```bash
# 프로젝트 디렉토리로 이동
cd /path/to/V2R

# 파일 전송 (제외할 파일 설정)
rsync -avz --exclude 'venv' --exclude '__pycache__' --exclude '.git' \
    -e "ssh -i your-key.pem" \
    ./ ubuntu@your-ec2-ip:~/V2R/

# 또는 tar + scp 사용
tar --exclude='venv' --exclude='__pycache__' --exclude='.git' \
    -czf v2r.tar.gz .
scp -i your-key.pem v2r.tar.gz ubuntu@your-ec2-ip:~/
```

#### EC2에서 실행
```bash
# 파일 압축 해제
cd ~
tar -xzf v2r.tar.gz
cd V2R

# 이후 방법 1의 4-6단계와 동일
```

---

## 테스트 실행

### 1. 기본 모듈 테스트
```bash
# Docker 환경에서
docker-compose exec app python scripts/test/smoke_test.py

# 로컬 환경에서
source venv/bin/activate
python scripts/test/smoke_test.py
```

### 2. 스캐너 테스트
```bash
# Nmap 스캐너 테스트
python src/scanner/test_scanner.py

# 또는 파이프라인 테스트
python scripts/test/test_pipeline.py
```

### 3. 통합 테스트
```bash
# 전체 파이프라인 테스트
python scripts/test/test_integration.py
```

### 4. 대시보드 실행
```bash
# Streamlit 대시보드 실행
streamlit run src/dashboard/app.py --server.port 8501 --server.address 0.0.0.0

# 브라우저에서 접속: http://your-ec2-ip:8501
```

---

## 보안 그룹 설정

EC2 보안 그룹에서 다음 포트를 열어야 합니다:

### 필수 포트
- **22 (SSH)**: 서버 접속용
- **8501 (Streamlit)**: 대시보드 접속용 (선택)

### 보안 그룹 설정 방법
1. AWS 콘솔 → EC2 → Security Groups
2. 해당 인스턴스의 보안 그룹 선택
3. Inbound rules → Edit inbound rules
4. 다음 규칙 추가:
   - Type: Custom TCP, Port: 8501, Source: 0.0.0.0/0 (또는 특정 IP)

---

## 실행 스크립트 예제

### systemd 서비스로 자동 실행 (선택)

`/etc/systemd/system/v2r-dashboard.service` 파일 생성:
```ini
[Unit]
Description=V2R Dashboard Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/V2R
Environment="PATH=/home/ubuntu/V2R/venv/bin"
ExecStart=/home/ubuntu/V2R/venv/bin/streamlit run src/dashboard/app.py --server.port 8501 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

서비스 활성화:
```bash
sudo systemctl daemon-reload
sudo systemctl enable v2r-dashboard
sudo systemctl start v2r-dashboard
sudo systemctl status v2r-dashboard
```

---

## 문제 해결

### 1. Docker 권한 오류
```bash
# Docker 그룹에 사용자 추가
sudo usermod -aG docker $USER
# 재로그인 필요
```

### 2. 포트 접속 불가
- 보안 그룹에서 포트 열기 확인
- 방화벽 설정 확인: `sudo ufw status`

### 3. 데이터베이스 연결 실패
```bash
# PostgreSQL 서비스 확인
sudo systemctl status postgresql

# 연결 테스트
psql -h localhost -U v2r -d v2r
```

### 4. 의존성 설치 실패
```bash
# 시스템 패키지 업데이트
sudo apt-get update

# 빌드 도구 설치
sudo apt-get install -y build-essential python3-dev
```

### 5. Nmap/Nuclei 실행 오류
```bash
# Nmap 설치
sudo apt-get install -y nmap

# Nuclei 설치
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
# 또는
wget -q -O - https://raw.githubusercontent.com/projectdiscovery/nuclei/main/install.sh | bash
```

---

## 모니터링 및 로그

### 로그 확인
```bash
# Docker 로그
docker-compose logs -f app

# 시스템 로그
journalctl -u v2r-dashboard -f

# 애플리케이션 로그
tail -f ~/V2R/logs/app.log
```

### 리소스 모니터링
```bash
# CPU/메모리 사용량
htop

# 디스크 사용량
df -h

# 네트워크 연결
netstat -tulpn
```

---

## 다음 단계

1. ✅ EC2 서버 접속 및 환경 설정
2. ✅ 프로젝트 파일 전송
3. ✅ 의존성 설치 및 환경 변수 설정
4. ✅ 데이터베이스 초기화
5. ✅ 스모크 테스트 실행
6. ✅ 대시보드 실행 및 접속 확인
7. ✅ 실제 스캔 테스트

---

## 참고사항

- EC2 인스턴스 타입에 따라 성능이 달라질 수 있습니다 (최소 t2.micro 권장)
- 스캔 작업은 리소스를 많이 사용하므로 모니터링 필요
- 보안을 위해 SSH 키 파일은 안전하게 관리하세요
- 프로덕션 환경에서는 HTTPS 설정을 권장합니다

