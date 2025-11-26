# EC2 서버 빠른 시작 가이드

## 🚀 빠른 배포 (5분 안에)

### 1단계: EC2 서버 접속
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### 2단계: 초기 설정 실행
```bash
# 초기 설정 스크립트 다운로드 및 실행
curl -o setup_ec2.sh https://raw.githubusercontent.com/your-repo/V2R/main/scripts/deployment/setup_ec2.sh
chmod +x setup_ec2.sh
./setup_ec2.sh
```

또는 수동으로:
```bash
# 필수 패키지 설치
sudo apt-get update
sudo apt-get install -y python3.11 python3-pip docker.io docker-compose git nmap
sudo systemctl start docker
sudo usermod -aG docker $USER
# 재로그인 필요: exit 후 다시 접속
```

### 3단계: 프로젝트 클론 또는 전송

#### 방법 A: Git 사용 (권장)
```bash
cd ~
git clone <your-repository-url> V2R
cd V2R
```

#### 방법 B: 로컬에서 파일 전송
```bash
# 로컬에서 실행
scp -i your-key.pem -r V2R ubuntu@your-ec2-ip:~/
```

### 4단계: 환경 변수 설정
```bash
cd ~/V2R
nano .env
```

`.env` 파일 내용:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=v2r
DB_USER=v2r
DB_PASSWORD=your_password

AWS_REGION=ap-northeast-2
OPENAI_API_KEY=your_key  # 선택사항
```

### 5단계: Docker로 실행 (권장)
```bash
docker-compose up -d
docker-compose logs -f
```

### 6단계: 테스트
```bash
# 컨테이너 접속
docker-compose exec app bash

# 스모크 테스트
python scripts/test/smoke_test.py

# 대시보드 실행
streamlit run src/dashboard/app.py --server.port 8501 --server.address 0.0.0.0
```

### 7단계: 브라우저에서 접속
```
http://your-ec2-ip:8501
```

**중요**: EC2 보안 그룹에서 포트 8501을 열어야 합니다!

---

## 🔧 문제 해결

### 포트 접속 불가
```bash
# 보안 그룹 확인 (AWS 콘솔)
# Inbound rules에 포트 8501 추가

# 방화벽 확인
sudo ufw status
sudo ufw allow 8501
```

### Docker 권한 오류
```bash
sudo usermod -aG docker $USER
# 재로그인
exit
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### 데이터베이스 연결 실패
```bash
# PostgreSQL 설치 (로컬 DB 사용 시)
sudo apt-get install -y postgresql
sudo -u postgres createdb v2r
sudo -u postgres createuser v2r
```

---

## 📚 상세 가이드

- **전체 배포 가이드**: `docs/DEPLOYMENT_EC2.md`
- **배포 스크립트**: `scripts/deployment/`

---

## ✅ 체크리스트

- [ ] EC2 서버 접속 확인
- [ ] 필수 패키지 설치 완료
- [ ] 프로젝트 파일 전송/클론 완료
- [ ] .env 파일 설정 완료
- [ ] Docker Compose 실행 완료
- [ ] 보안 그룹 포트 설정 완료
- [ ] 대시보드 접속 확인

