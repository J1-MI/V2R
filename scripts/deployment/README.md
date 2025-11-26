# EC2 배포 스크립트

## 개요
EC2 서버에 V2R 프로젝트를 배포하기 위한 스크립트입니다.

## 파일 설명

### `deploy_to_ec2.sh` (Linux/Mac)
- 로컬에서 EC2로 프로젝트를 자동 배포하는 스크립트
- 사용법: `./deploy_to_ec2.sh <ec2-ip> <key-file> [user]`

### `deploy_to_ec2.ps1` (Windows PowerShell)
- Windows에서 EC2로 프로젝트를 자동 배포하는 스크립트
- 사용법: `.\deploy_to_ec2.ps1 -EC2IP "1.2.3.4" -KeyFile "C:\path\to\key.pem"`

### `setup_ec2.sh`
- EC2 서버에서 직접 실행하는 초기 설정 스크립트
- 필수 패키지 설치 및 환경 설정

## 사용 방법

### 방법 1: 자동 배포 스크립트 사용

#### Linux/Mac
```bash
chmod +x scripts/deployment/deploy_to_ec2.sh
./scripts/deployment/deploy_to_ec2.sh 1.2.3.4 ~/.ssh/my-key.pem ubuntu
```

#### Windows (PowerShell)
```powershell
.\scripts\deployment\deploy_to_ec2.ps1 -EC2IP "1.2.3.4" -KeyFile "C:\path\to\key.pem" -User "ubuntu"
```

### 방법 2: 수동 배포

1. **로컬에서 파일 압축**
   ```bash
   tar --exclude='venv' --exclude='__pycache__' --exclude='.git' \
       -czf v2r_deploy.tar.gz .
   ```

2. **SCP로 파일 전송**
   ```bash
   scp -i your-key.pem v2r_deploy.tar.gz ubuntu@your-ec2-ip:/tmp/
   ```

3. **EC2에서 압축 해제 및 설정**
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   mkdir -p ~/V2R
   cd ~/V2R
   tar -xzf /tmp/v2r_deploy.tar.gz
   ```

4. **초기 설정 실행**
   ```bash
   chmod +x scripts/deployment/setup_ec2.sh
   ./scripts/deployment/setup_ec2.sh
   ```

## EC2 서버 설정

### 1. 환경 변수 설정
```bash
cd ~/V2R
cp .env.example .env
nano .env
```

### 2. Docker Compose 사용 (권장)
```bash
docker-compose up -d
docker-compose logs -f
```

### 3. 로컬 설치 사용
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python scripts/utils/init_db.py
```

## 테스트

### 스모크 테스트
```bash
python scripts/test/smoke_test.py
```

### 대시보드 실행
```bash
streamlit run src/dashboard/app.py --server.port 8501 --server.address 0.0.0.0
```

브라우저에서 접속: `http://your-ec2-ip:8501`

## 문제 해결

### SSH 접속 오류
- 키 파일 권한 확인: `chmod 400 your-key.pem`
- 보안 그룹에서 SSH 포트(22) 열기 확인

### 파일 전송 실패
- SCP 대신 WinSCP (Windows) 또는 FileZilla 사용
- 또는 Git 저장소에서 직접 클론

### Docker 권한 오류
```bash
sudo usermod -aG docker $USER
# 재로그인 필요
```

## 참고
- 상세한 배포 가이드는 `docs/DEPLOYMENT_EC2.md` 참조

