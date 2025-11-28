# EC2 배포 단계별 가이드 (Windows)

## 사전 준비사항 확인

### 1. 필요한 정보
- ✅ EC2 인스턴스 IP 주소 (예: `1.2.3.4`)
- ✅ SSH 키 파일 (.pem 파일 경로)
- ✅ EC2 사용자 이름 (일반적으로 `ubuntu` 또는 `ec2-user`)

### 2. 로컬 환경 확인
```powershell
# Git Bash 또는 WSL 설치 확인
wsl --version
# 또는
bash --version
```

**없다면 설치:**
- Git Bash: https://git-scm.com/downloads
- WSL: `wsl --install` (PowerShell 관리자 권한)

---

## 방법 1: Git을 사용한 배포 (가장 간단)

### 1단계: EC2 서버 접속
```powershell
# PowerShell에서
ssh -i "C:\path\to\your-key.pem" ubuntu@your-ec2-ip

# 또는 Git Bash에서
ssh -i /c/path/to/your-key.pem ubuntu@your-ec2-ip
```

**접속이 안 되면:**
- 키 파일 권한 확인: `.pem` 파일 우클릭 → 속성 → 보안 → 고급 → 상속 비활성화 → 현재 사용자만 읽기 권한
- 보안 그룹에서 SSH 포트(22) 열기 확인

### 2단계: EC2에서 초기 설정
```bash
# 시스템 업데이트
sudo apt-get update
sudo apt-get upgrade -y

# 필수 패키지 설치
sudo apt-get install -y \
    python3.11 \
    python3-pip \
    git \
    docker.io \
    docker-compose \
    nmap

# Docker 서비스 시작
sudo systemctl start docker
sudo systemctl enable docker

# Docker 그룹에 사용자 추가
sudo usermod -aG docker $USER

# 재로그인 (exit 후 다시 접속)
exit
```

### 3단계: 프로젝트 클론
```bash
# EC2에서 실행
cd ~
git clone https://github.com/J1-MI/V2R.git
cd V2R
```

### 4단계: 환경 변수 설정
```bash
# .env 파일 생성
nano .env
```

`.env` 파일 내용:
```env
# 데이터베이스 설정
DB_HOST=localhost
DB_PORT=5432
DB_NAME=v2r
DB_USER=v2r
DB_PASSWORD=your_secure_password_here

# AWS 설정 (EC2에서 실행 중이므로 자동 인증)
AWS_REGION=ap-northeast-2

# S3 설정 (선택)
S3_BUCKET_NAME=
S3_EVIDENCE_PREFIX=evidence/

# LLM 설정 (선택, 테스트 시에는 없어도 됨)
OPENAI_API_KEY=
LLM_MODEL=gpt-4.1-nano

# 스캐닝 설정
SCAN_TIMEOUT=300
MAX_CONCURRENT_SCANS=5
```

저장: `Ctrl + X`, `Y`, `Enter`

### 5단계: Docker로 실행 (권장)
```bash
# Docker Compose로 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 컨테이너 접속
docker-compose exec app bash
```

### 6단계: 테스트 실행
```bash
# 컨테이너 내에서
python scripts/test/smoke_test.py

# 통합 테스트
python scripts/test/test_integration.py
```

### 7단계: 대시보드 실행
```bash
# 컨테이너 내에서
streamlit run src/dashboard/app.py --server.port 8501 --server.address 0.0.0.0
```

### 8단계: 브라우저에서 접속
1. **EC2 보안 그룹 설정** (중요!)
   - AWS 콘솔 → EC2 → Security Groups
   - 해당 인스턴스의 보안 그룹 선택
   - Inbound rules → Edit inbound rules
   - Add rule:
     - Type: Custom TCP
     - Port: 8501
     - Source: 0.0.0.0/0 (또는 특정 IP)
     - Save rules

2. **브라우저에서 접속**
   ```
   http://your-ec2-ip:8501
   ```

---

## 방법 2: SCP로 파일 전송 (Git 사용 불가 시)

### 1단계: 로컬에서 파일 압축
```powershell
# PowerShell에서 프로젝트 디렉토리로 이동
cd C:\Users\user\Desktop\DEEP_DIVE\final_project\V2R\V2R

# Git Bash 또는 WSL에서 압축
# Git Bash 실행 후:
tar --exclude='venv' --exclude='__pycache__' --exclude='.git' \
    --exclude='evidence' --exclude='reports' --exclude='.env' \
    -czf v2r_deploy.tar.gz .
```

### 2단계: 파일 전송
```powershell
# PowerShell에서 (WSL 또는 Git Bash 필요)
# Git Bash 실행 후:
scp -i "C:/path/to/your-key.pem" v2r_deploy.tar.gz ubuntu@your-ec2-ip:/tmp/
```

### 3단계: EC2에서 압축 해제
```bash
# EC2에서 실행
cd ~
mkdir -p V2R
cd V2R
tar -xzf /tmp/v2r_deploy.tar.gz
rm /tmp/v2r_deploy.tar.gz
```

### 4단계: 이후 방법 1의 4-8단계와 동일

---

## 방법 3: 자동 배포 스크립트 사용

### Windows PowerShell
```powershell
cd C:\Users\user\Desktop\DEEP_DIVE\final_project\V2R\V2R
.\scripts\deployment\deploy_to_ec2.ps1 -EC2IP "your-ec2-ip" -KeyFile "C:\path\to\key.pem" -User "ubuntu"
```

### Linux/Mac 또는 Git Bash
```bash
cd /c/Users/user/Desktop/DEEP_DIVE/final_project/V2R/V2R
chmod +x scripts/deployment/deploy_to_ec2.sh
./scripts/deployment/deploy_to_ec2.sh your-ec2-ip your-key.pem ubuntu
```

---

## 로컬 설치 방식 (Docker 미사용)

### 1단계: Python 가상환경 생성
```bash
cd ~/V2R
python3 -m venv venv
source venv/bin/activate
```

### 2단계: 의존성 설치
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3단계: PostgreSQL 설치 및 설정
```bash
sudo apt-get install -y postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 데이터베이스 생성
sudo -u postgres psql << EOF
CREATE DATABASE v2r;
CREATE USER v2r WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE v2r TO v2r;
\q
EOF
```

### 4단계: 데이터베이스 스키마 초기화
```bash
python scripts/utils/init_db.py
```

### 5단계: 테스트 실행
```bash
python scripts/test/smoke_test.py
python scripts/test/test_integration.py
```

### 6단계: 대시보드 실행
```bash
streamlit run src/dashboard/app.py --server.port 8501 --server.address 0.0.0.0
```

---

## 문제 해결

### 1. SSH 접속 실패
```bash
# 키 파일 권한 확인 (Linux/Mac)
chmod 400 your-key.pem

# Windows에서는 파일 속성에서 권한 설정
# 우클릭 → 속성 → 보안 → 고급 → 상속 비활성화 → 현재 사용자만 읽기
```

### 2. Docker 권한 오류
```bash
sudo usermod -aG docker $USER
# 재로그인 필요
exit
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### 3. 포트 접속 불가
```bash
# 방화벽 확인
sudo ufw status
sudo ufw allow 8501

# 보안 그룹에서 포트 8501 열기 확인 (AWS 콘솔)
```

### 4. 데이터베이스 연결 실패
```bash
# PostgreSQL 서비스 확인
sudo systemctl status postgresql

# 연결 테스트
psql -h localhost -U v2r -d v2r
```

### 5. 의존성 설치 실패
```bash
# 시스템 패키지 업데이트
sudo apt-get update

# 빌드 도구 설치
sudo apt-get install -y build-essential python3-dev
```

### 6. Nmap/Nuclei 실행 오류
```bash
# Nmap 설치 확인
which nmap
sudo apt-get install -y nmap

# Nuclei 설치
wget -q -O - https://raw.githubusercontent.com/projectdiscovery/nuclei/main/install.sh | bash
```

---

## 빠른 체크리스트

- [ ] EC2 서버 접속 확인
- [ ] 필수 패키지 설치 완료
- [ ] 프로젝트 파일 전송/클론 완료
- [ ] .env 파일 설정 완료
- [ ] Docker Compose 실행 완료 (또는 로컬 설치 완료)
- [ ] 보안 그룹에서 포트 8501 열기
- [ ] 스모크 테스트 통과
- [ ] 대시보드 접속 확인

---

## 다음 단계

1. **기본 테스트**
   - 스모크 테스트 실행
   - 통합 테스트 실행

2. **실제 스캔 테스트**
   - 로컬호스트 스캔: `python -c "from src.pipeline.scanner_pipeline import ScannerPipeline; p = ScannerPipeline(); p.run_nmap_scan('127.0.0.1')"`

3. **대시보드 사용**
   - 취약점 리스트 확인
   - 리포트 생성 테스트

---

## 참고사항

- EC2 인스턴스 타입에 따라 성능이 달라질 수 있습니다 (최소 t2.micro 권장)
- 스캔 작업은 리소스를 많이 사용하므로 모니터링 필요
- 보안을 위해 SSH 키 파일은 안전하게 관리하세요
- 프로덕션 환경에서는 HTTPS 설정을 권장합니다


