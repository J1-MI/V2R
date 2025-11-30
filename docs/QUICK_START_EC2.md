# EC2 빠른 시작 가이드

## 서버 정보

- **서버 이름**: v2r-server
- **OS**: Amazon Linux 2023
- **인스턴스 타입**: t3.small
- **퍼블릭 IPv4**: 3.36.15.26
- **SSH 사용자**: ec2-user

---

## 1. EC2 서버 설정 (5분)

### SSH 접속
```bash
ssh -i your-key.pem ec2-user@3.36.15.26
```

### 초기 설정
```bash
# 시스템 업데이트
sudo dnf update -y

# 필수 패키지 설치
sudo dnf install -y python3.11 python3-pip git docker docker-compose postgresql15 nmap gcc gcc-c++ make python3-devel curl wget

# Docker 시작 및 자동 시작 설정
sudo systemctl start docker
sudo systemctl enable docker

# Docker 그룹에 사용자 추가
sudo usermod -aG docker $USER

# 재로그인 (Docker 그룹 적용)
exit
# 다시 SSH 접속
ssh -i your-key.pem ec2-user@3.36.15.26
```

### 프로젝트 배포
```bash
# Git 클론
cd ~
git clone https://github.com/J1-MI/V2R.git
cd V2R

# 또는 배포 스크립트 사용 (로컬 PC에서)
# ./scripts/deployment/deploy_to_ec2.sh 3.36.15.26 ~/.ssh/your-key.pem ec2-user
```

### 환경 변수 설정
```bash
cd ~/V2R
nano .env
```

**.env 파일 내용:**
```bash
# 데이터베이스 설정
DB_HOST=postgres
DB_PORT=5432
DB_NAME=v2r
DB_USER=v2r
DB_PASSWORD=v2r_password_변경필요

# API 서버 설정
API_SERVER_URL=http://localhost:5000
FLASK_ENV=production
```

### Docker Compose 실행
```bash
cd ~/V2R
docker-compose up -d
```

### 서비스 확인
```bash
# 서비스 상태 확인
docker-compose ps

# API 서버 확인
curl http://localhost:5000/api/agents
# 예상 응답: {"success":true,"agents":[]}

# Streamlit 대시보드 실행
docker exec -d v2r-app streamlit run src/dashboard/app.py \
    --server.port 8501 \
    --server.address 0.0.0.0
```

---

## 2. 로컬 PC Agent 설정 (2분)

### 환경 변수 설정
```bash
# Windows PowerShell
$env:AGENT_SERVER_URL="http://3.36.15.26:5000"
$env:AGENT_NAME="my-local-agent"

# Linux/Mac
export AGENT_SERVER_URL="http://3.36.15.26:5000"
export AGENT_NAME="my-local-agent"
```

### Agent 실행
```bash
cd ~/V2R  # 프로젝트 루트
python src/agent/main.py
```

**예상 로그:**
```
INFO:src.agent.agent:Agent 등록 시도: my-local-agent
INFO:src.agent.agent:✅ Agent 등록 완료: agent_my-local-agent_...
INFO:src.agent.storage:설정 파일 저장 완료: ~/.v2r_agent/config.json
INFO:src.agent.agent:Agent 시작: agent_my-local-agent_...
INFO:src.agent.agent:폴링 간격: 10초
```

---

## 3. 테스트 (3분)

### 대시보드 접속
```
http://3.36.15.26:8501
```

### Agent 확인
1. "Agent & Local Scanner" 페이지 선택
2. 등록된 Agent 목록 확인 (🟢 온라인 상태)

### 작업 생성 및 실행
1. Agent 목록에서 "Docker 상태 조회" 버튼 클릭
2. 작업 생성 확인: "✅ 작업 생성 완료: task_..."
3. Agent 로그에서 작업 처리 확인
4. 대시보드에서 작업 결과 확인

---

## 4. 빠른 테스트 스크립트

**EC2 서버에서:**
```bash
cd ~/V2R
chmod +x scripts/deployment/quick_test.sh
./scripts/deployment/quick_test.sh
```

---

## 5. 문제 해결

### API 서버 연결 실패
```bash
# 보안 그룹 확인 (포트 5000 열기)
# EC2 서버에서 확인
docker-compose logs api
docker-compose ps api
```

### Agent 등록 실패
```bash
# 로컬 PC에서
# 1. 방화벽 확인
# 2. EC2 보안 그룹에서 포트 5000 열기 확인
# 3. Agent 로그 확인
```

### Streamlit 대시보드 접속 불가
```bash
# EC2 서버에서
docker exec v2r-app ps aux | grep streamlit
# 실행되지 않으면:
docker exec -d v2r-app streamlit run src/dashboard/app.py \
    --server.port 8501 \
    --server.address 0.0.0.0
```

---

## 6. 다음 단계

- 전체 스캔 실행 테스트
- CCE 점검 실행 테스트
- 상세 가이드: `docs/EC2_DEPLOYMENT_GUIDE.md`

