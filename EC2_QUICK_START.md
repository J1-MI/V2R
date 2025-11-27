# EC2 빠른 시작 가이드 (실전)

## ⚡ 5분 안에 시작하기

### 준비물
- EC2 IP 주소
- SSH 키 파일 (.pem)
- Git Bash 또는 WSL (Windows)

---

## 1️⃣ EC2 접속 (1분)

```bash
# Git Bash 또는 PowerShell에서
ssh -i "your-key.pem" ubuntu@your-ec2-ip
```

**접속 안 되면?**
- 키 파일 경로 확인
- 보안 그룹에서 포트 22 열기 확인

---

## 2️⃣ 초기 설정 (2분)

```bash
# 한 번에 실행
sudo apt-get update && \
sudo apt-get install -y python3.11 python3-pip git docker.io docker-compose nmap && \
sudo systemctl start docker && \
sudo usermod -aG docker $USER

# 재로그인 (중요!)
exit
ssh -i "your-key.pem" ubuntu@your-ec2-ip
```

---

## 3️⃣ 프로젝트 클론 (30초)

```bash
cd ~
git clone https://github.com/J1-MI/V2R.git
cd V2R
```

---

## 4️⃣ 환경 변수 설정 (1분)

```bash
nano .env
```

**최소 설정 (.env 파일 내용):**
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=v2r
DB_USER=v2r
DB_PASSWORD=test123

AWS_REGION=ap-northeast-2
```

저장: `Ctrl+X` → `Y` → `Enter`

---

## 5️⃣ Docker 실행 (30초)

```bash
docker-compose up -d
docker-compose logs -f
```

**에러 발생 시:**
```bash
# Docker 그룹 확인
groups
# docker가 없으면 재로그인
exit
ssh -i "your-key.pem" ubuntu@your-ec2-ip
```

---

## 6️⃣ 테스트 실행 (1분)

```bash
# 컨테이너 접속
docker-compose exec app bash

# 스모크 테스트
python scripts/test/smoke_test.py

# 대시보드 실행
streamlit run src/dashboard/app.py --server.port 8501 --server.address 0.0.0.0
```

---

## 7️⃣ 브라우저 접속

### 보안 그룹 설정 (중요!)
1. AWS 콘솔 → EC2 → Security Groups
2. 인스턴스의 보안 그룹 선택
3. Inbound rules → Edit inbound rules
4. Add rule:
   - Type: **Custom TCP**
   - Port: **8501**
   - Source: **0.0.0.0/0**
5. Save rules

### 접속
```
http://your-ec2-ip:8501
```

---

## ✅ 완료!

이제 대시보드에서 다음을 할 수 있습니다:
- 취약점 리스트 조회
- 스캔 결과 확인
- 리포트 생성

---

## 🆘 문제 해결

### 포트 접속 안 됨
```bash
# 방화벽 확인
sudo ufw allow 8501
```

### Docker 오류
```bash
sudo systemctl restart docker
docker-compose down
docker-compose up -d
```

### 데이터베이스 오류
```bash
# PostgreSQL 설치 (Docker 사용 시 불필요)
sudo apt-get install -y postgresql
```

---

## 📚 더 자세한 가이드

- **상세 가이드**: `docs/DEPLOYMENT_EC2.md`
- **단계별 가이드**: `docs/EC2_DEPLOYMENT_STEP_BY_STEP.md`

