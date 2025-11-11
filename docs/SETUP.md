# 개발 환경 설정 가이드

## 개요
V2R 프로젝트 개발 환경을 설정하는 방법을 안내합니다.

**추천 방법**: Docker Compose를 사용한 환경 구성 (이 방법을 권장합니다)

## 필수 요구사항

### Docker 방식 (권장)
- Docker 20.10 이상
- Docker Compose 2.0 이상
- Git

### 로컬 설치 방식 (선택)
- Python 3.11 이상
- PostgreSQL 12 이상
- Terraform 1.0 이상 (인프라 배포용)
- Nmap (포트 스캔)
- Nuclei (취약점 스캔)

---

## 방법 1: Docker Compose 사용 (권장)

### 1. Docker 및 Docker Compose 설치

#### Windows/macOS
- [Docker Desktop](https://www.docker.com/products/docker-desktop) 설치

#### Linux
```bash
# Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. 프로젝트 클론 및 초기화

```bash
# 프로젝트 디렉토리로 이동
cd V2R

# 환경 초기화 (자동으로 .env 생성 및 DB 스키마 생성)
make init
# 또는
bash scripts/docker/init.sh
```

### 3. 환경 변수 설정

`.env` 파일을 편집하여 필요한 설정을 변경하세요:
```bash
# .env 파일 편집
vim .env  # 또는 원하는 에디터
```

주요 설정:
- `DB_PASSWORD`: PostgreSQL 비밀번호
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`: AWS 자격 증명 (선택)
- `OPENAI_API_KEY`: LLM API 키 (선택)

### 4. 서비스 시작

```bash
# 모든 서비스 시작
make up
# 또는
docker-compose up -d

# 상태 확인
make status
# 또는
docker-compose ps
```

### 5. 사용 가능한 명령어

```bash
# 로그 보기
make logs

# 컨테이너에 접속
make shell

# PostgreSQL 접속
make db-shell

# 스캐너 테스트
make test

# 서비스 중지
make down
```

### 6. 데이터베이스 초기화

```bash
# 스키마 생성
make init-db
```

---

## 방법 2: 로컬 설치 (Docker 미사용)

## 1. 프로젝트 클론 및 초기 설정

```bash
# 프로젝트 디렉토리로 이동
cd V2R

# Python 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

## 2. 환경 변수 설정

```bash
# .env.example을 .env로 복사
cp .env.example .env

# .env 파일을 열어서 실제 값으로 수정
# 특히 데이터베이스 및 AWS 자격 증명 설정 필요
```

### 주요 환경 변수
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`: PostgreSQL 설정
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`: AWS 자격 증명
- `OPENAI_API_KEY`: LLM API 키 (선택)

## 3. 데이터베이스 설정

### PostgreSQL 설치 (로컬)
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS (Homebrew)
brew install postgresql
brew services start postgresql
```

### 데이터베이스 및 사용자 생성
```bash
# PostgreSQL 접속
sudo -u postgres psql

# 데이터베이스 생성
CREATE DATABASE v2r;

# 사용자 생성
CREATE USER v2r WITH PASSWORD 'your_password';

# 권한 부여
GRANT ALL PRIVILEGES ON DATABASE v2r TO v2r;
\q
```

### 스키마 초기화
```bash
# 데이터베이스 스키마 생성
python scripts/utils/init_db.py
```

## 4. 스캐너 도구 설치 (선택)

### Nmap 설치
```bash
# Ubuntu/Debian
sudo apt-get install nmap python3-nmap

# macOS
brew install nmap
pip install python-nmap
```

### Nuclei 설치
```bash
# 공식 설치 스크립트
curl -sL https://raw.githubusercontent.com/projectdiscovery/nuclei/main/install.sh | bash

# 또는 Homebrew (macOS)
brew install nuclei
```

## 5. Terraform 설정 (AWS 인프라 배포용)

### AWS 자격 증명 설정
```bash
# AWS CLI 설치
pip install awscli

# 자격 증명 설정
aws configure
```

#### Windows PATH 설정 (예: `C:\Terraform`)
- Terraform 실행 파일(`terraform.exe`)을 `C:\Terraform` 등에 두었다면, 시스템 환경 변수 또는 PowerShell 세션에 경로를 추가해야 합니다.
```powershell
# PowerShell 세션에서 임시로 PATH 추가
$env:Path = "C:\Terraform;" + $env:Path

# 버전 확인
terraform -version
```
- 영구 설정은 **시스템 속성 → 고급 → 환경 변수 → Path**에 `C:\Terraform`을 추가하세요.

### SSH 키 생성
```bash
cd terraform/keys
ssh-keygen -t rsa -b 4096 -f id_rsa -N ""
```

### Terraform 초기화
```bash
cd terraform
terraform init
```

### Terraform 구성 검증
```bash
terraform validate
```
> **팁:** `terraform validate`가 실패한다면 에러 메시지를 확인하여 변수(`instance_ami` 등) 설정 여부나 스크립트 문법을 점검하세요.

## 6. 개발 환경 테스트

### 스캐너 모듈 테스트
```bash
# Nmap 스캐너 테스트
python src/scanner/test_scanner.py
```

### 데이터베이스 연결 테스트
```python
from src.database import get_db

db = get_db()
if db.test_connection():
    print("Database connection successful!")
```

## 7. 프로젝트 구조 확인

프로젝트 구조는 `PROJECT_STRUCTURE.md` 파일을 참조하세요.

## 문제 해결

### 데이터베이스 연결 실패
- PostgreSQL이 실행 중인지 확인
- `.env` 파일의 DB 설정 확인
- 방화벽 설정 확인

### Nmap 스캔 실패
- `python-nmap` 패키지 설치 확인
- 시스템에 Nmap이 설치되어 있는지 확인 (`which nmap`)

### Nuclei 스캔 실패
- Nuclei가 PATH에 있는지 확인 (`which nuclei`)
- Nuclei 템플릿 업데이트: `nuclei -update-templates`

## 다음 단계

환경 설정이 완료되면 다음을 진행하세요:
1. Terraform으로 AWS 인프라 배포 (Week 1)
   - 세부 절차는 `docs/AWS_EC2_GUIDE.md`를 참고하세요.
2. 스캐너 통합 테스트
3. PoC 재현 엔진 개발 시작 (Week 2)

