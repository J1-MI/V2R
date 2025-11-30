# EC2 배포 및 테스트 가이드

## 개요

이 가이드는 V2R 프로젝트를 EC2 서버에 배포하고, 로컬 PC의 Agent와 연동하여 테스트하는 방법을 설명합니다.

## 아키텍처

```
[로컬 PC]                    [EC2 서버]
┌─────────┐                 ┌──────────────┐
│ Agent   │ ←─── 폴링 ───→  │ Flask API    │
│ (로컬)  │                 │ (포트 5000)  │
│         │ ←─── 결과 ───→  │              │
└─────────┘                 └──────────────┘
     │                            │
     │                            │
     ↓                            ↓
┌─────────┐                 ┌──────────────┐
│ Docker  │                 │ PostgreSQL   │
│ 스캐너  │                 │ + Streamlit  │
└─────────┘                 │ 대시보드     │
                            └──────────────┘
```

---

## 1. EC2 서버 준비

### 1.1 기존 EC2 서버 정보

**현재 사용 중인 서버:**
- **서버 이름**: v2r-server
- **OS**: Amazon Linux 2023
- **인스턴스 타입**: t3.small
- **퍼블릭 IPv4**: 3.36.15.26

**보안 그룹 설정 확인:**
- SSH (22): 접속용
- PostgreSQL (5432): 선택사항 (Docker 사용 시 불필요)
- Streamlit 대시보드 (8501): 외부 접근용
- Flask API 서버 (5000): 외부 접근용

### 1.2 EC2 서버 초기 설정

**SSH 접속:**
```bash
# Amazon Linux 2023은 ec2-user 사용
ssh -i your-key.pem ec2-user@3.36.15.26
```

**초기 설정 스크립트 실행 (Amazon Linux 2023용):**
```bash
# 프로젝트 디렉토리로 이동 (또는 Git에서 클론)
cd ~
git clone https://github.com/J1-MI/V2R.git
cd V2R

# Amazon Linux 2023 초기 설정 스크립트 실행
chmod +x scripts/deployment/setup_amazon_linux.sh
./scripts/deployment/setup_amazon_linux.sh
```

**수동 설정 (Amazon Linux 2023):**
```bash
# 시스템 업데이트
sudo dnf update -y

# 필수 패키지 설치
sudo dnf install -y python3.11 python3-pip git docker docker-compose postgresql15 nmap gcc gcc-c++ make python3-devel curl wget

# Docker 설정
sudo systemctl start docker
sudo systemctl enable docker

# Docker 그룹에 사용자 추가
sudo usermod -aG docker $USER
# 재로그인 필요: exit 후 다시 SSH 접속
```

---

## 2. EC2 서버 배포

### 2.1 프로젝트 파일 배포

**방법 1: Git 클론 (권장)**
```bash
# EC2 서버에서
cd ~
git clone https://github.com/J1-MI/V2R.git
cd V2R
```

**방법 2: 배포 스크립트 사용**
```bash
# 로컬 PC에서 (Amazon Linux 2023은 ec2-user 사용)
chmod +x scripts/deployment/deploy_to_ec2.sh
./scripts/deployment/deploy_to_ec2.sh 3.36.15.26 ~/.ssh/your-key.pem ec2-user
```

**방법 3: 수동 배포**
```bash
# 로컬 PC에서
tar --exclude='venv' --exclude='__pycache__' --exclude='.git' \
    --exclude='evidence' --exclude='reports' \
    -czf v2r_deploy.tar.gz .

scp -i your-key.pem v2r_deploy.tar.gz ec2-user@3.36.15.26:/tmp/

# EC2 서버에서
cd ~
mkdir -p V2R
cd V2R
tar -xzf /tmp/v2r_deploy.tar.gz
```

### 2.2 환경 변수 설정

**EC2 서버에서 .env 파일 생성:**
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

# API 서버 설정 (대시보드에서 사용)
API_SERVER_URL=http://localhost:5000

# Flask 환경
FLASK_ENV=production

# 선택사항: AWS, S3, LLM 설정
# AWS_REGION=ap-northeast-2
# AWS_ACCESS_KEY_ID=
# AWS_SECRET_ACCESS_KEY=
# S3_BUCKET_NAME=
# OPENAI_API_KEY=
```

### 2.3 Docker Compose 실행

**서비스 시작:**
```bash
cd ~/V2R
docker-compose up -d
```

**서비스 상태 확인:**
```bash
docker-compose ps
```

**예상 출력:**
```
NAME          IMAGE                    STATUS
v2r-postgres  postgres:15-alpine       Up (healthy)
v2r-api       v2r-api:latest           Up
v2r-app       v2r-app:latest           Up
```

**로그 확인:**
```bash
# 전체 로그
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f api
docker-compose logs -f postgres
```

### 2.4 데이터베이스 초기화

**스키마 적용:**
```bash
# Docker Compose 사용 시 자동 적용됨
# 수동 적용이 필요한 경우:
docker exec v2r-postgres psql -U v2r -d v2r -f /docker-entrypoint-initdb.d/schema.sql

# 또는 Python 스크립트 사용
docker exec v2r-app python scripts/utils/init_db.py
```

**확인:**
```bash
docker exec v2r-postgres psql -U v2r -d v2r -c "\dt"
# agents, agent_tasks 테이블이 보여야 함
```

### 2.5 Streamlit 대시보드 실행

**방법 1: Docker 컨테이너에서 실행**
```bash
docker exec -d v2r-app streamlit run src/dashboard/app.py \
    --server.port 8501 \
    --server.address 0.0.0.0
```

**방법 2: 백그라운드로 실행 (권장)**
```bash
docker exec -d v2r-app bash -c "streamlit run src/dashboard/app.py --server.port 8501 --server.address 0.0.0.0 > /tmp/streamlit.log 2>&1"
```

**확인:**
```bash
# 로그 확인
docker exec v2r-app tail -f /tmp/streamlit.log

# 프로세스 확인
docker exec v2r-app ps aux | grep streamlit
```

---

## 3. EC2 서버 접근 확인

### 3.1 API 서버 확인

**로컬 PC에서 테스트:**
```bash
# API 서버 상태 확인
curl http://3.36.15.26:5000/api/agents

# 예상 응답:
# {"success":true,"agents":[]}
```

**EC2 서버에서 확인:**
```bash
curl http://localhost:5000/api/agents
```

### 3.2 Streamlit 대시보드 확인

**브라우저에서 접속:**
```
http://3.36.15.26:8501
```

**예상 화면:**
- V2R 취약점 진단 대시보드
- 사이드바에 "Agent & Local Scanner" 메뉴 표시

### 3.3 보안 그룹 확인

**AWS 콘솔에서 확인:**
- 인바운드 규칙:
  - SSH (22): 내 IP 또는 특정 IP
  - Custom TCP (5000): 0.0.0.0/0 (또는 특정 IP)
  - Custom TCP (8501): 0.0.0.0/0 (또는 특정 IP)

---

## 4. 로컬 PC Agent 설정

### 4.1 환경 변수 설정

**Windows PowerShell:**
```powershell
$env:AGENT_SERVER_URL="http://your-ec2-ip:5000"
$env:AGENT_NAME="my-local-agent"
$env:POLLING_INTERVAL="10"
```

**Linux/Mac:**
```bash
export AGENT_SERVER_URL="http://your-ec2-ip:5000"
export AGENT_NAME="my-local-agent"
export POLLING_INTERVAL="10"
```

**.env 파일 사용 (권장):**
```bash
# 프로젝트 루트에 .env 파일 생성
cd ~/V2R  # 또는 프로젝트 경로
nano .env
```

**.env 파일 내용:**
```bash
AGENT_SERVER_URL=http://your-ec2-ip:5000
AGENT_NAME=my-local-agent
POLLING_INTERVAL=10
```

### 4.2 Agent 실행

**Python으로 직접 실행:**
```bash
cd ~/V2R  # 프로젝트 루트
python src/agent/main.py
```

**스크립트 사용:**
```bash
python scripts/agent/start_agent.py
```

**예상 로그:**
```
INFO:src.agent.agent:Agent 등록 시도: my-local-agent
INFO:src.agent.agent:✅ Agent 등록 완료: agent_my-local-agent_20250130_143022_123_a1b2c3d4
INFO:src.agent.storage:설정 파일 저장 완료: ~/.v2r_agent/config.json
INFO:src.agent.agent:✅ 설정 파일에 저장 완료: ~/.v2r_agent/config.json
WARNING:src.agent.agent:⚠️  토큰을 안전하게 보관하세요: a1b2c3d4-e5f6g7h8...
INFO:src.agent.agent:Agent 시작: agent_my-local-agent_...
INFO:src.agent.agent:폴링 간격: 10초
INFO:src.agent.agent:서버 URL: http://your-ec2-ip:5000
DEBUG:src.agent.agent:대기 중인 작업 없음
```

**재시작 시 (토큰 재사용):**
```
INFO:src.agent.storage:설정 파일 로드 완료: ~/.v2r_agent/config.json
INFO:src.agent.agent:저장된 설정 로드 완료: agent_my-local-agent_...
INFO:src.agent.agent:저장된 Agent 정보 사용: agent_my-local-agent_...
```

### 4.3 Agent 설정 파일 확인

**설정 파일 위치:**
```bash
# Windows
C:\Users\<username>\.v2r_agent\config.json

# Linux/Mac
~/.v2r_agent/config.json
```

**설정 파일 내용:**
```json
{
  "agent_id": "agent_my-local-agent_20250130_143022_123_a1b2c3d4",
  "agent_token": "a1b2c3d4-e5f6g7h8-i9j0k1l2-m3n4o5p6-q7r8s9t0",
  "agent_name": "my-local-agent",
  "server_url": "http://your-ec2-ip:5000"
}
```

---

## 5. E2E 테스트 시나리오

### 5.1 전체 워크플로우 테스트

#### Step 1: EC2 서버 준비 확인

**EC2 서버에서:**
```bash
# 서비스 상태 확인
docker-compose ps

# API 서버 확인
curl http://localhost:5000/api/agents
# 응답: {"success":true,"agents":[]}

# 로그 확인
docker-compose logs api | tail -20
```

#### Step 2: Agent 등록 확인

**로컬 PC에서 Agent 실행:**
```bash
python src/agent/main.py
```

**EC2 서버에서 확인:**
```bash
# API로 Agent 목록 조회
curl http://localhost:5000/api/agents

# 예상 응답:
# {
#   "success": true,
#   "agents": [
#     {
#       "agent_id": "agent_my-local-agent_...",
#       "agent_name": "my-local-agent",
#       "status": "online",
#       ...
#     }
#   ]
# }
```

**대시보드에서 확인:**
1. 브라우저에서 `http://your-ec2-ip:8501` 접속
2. "Agent & Local Scanner" 페이지 선택
3. 등록된 Agent 목록 확인 (🟢 온라인 상태)

#### Step 3: Docker 상태 조회 작업 테스트

**대시보드에서:**
1. Agent 목록에서 등록된 Agent 확장
2. "Docker 상태 조회" 버튼 클릭
3. "✅ 작업 생성 완료: task_..." 메시지 확인

**Agent 로그 확인 (로컬 PC):**
```
INFO:src.agent.agent:대기 중인 작업 1개 발견
INFO:src.agent.agent:작업 처리 시작: task_... (DOCKER_STATUS)
INFO:src.agent.agent:✅ 작업 상태 업데이트: task_... -> running
INFO:src.agent.task_executor:Docker 상태 조회 작업 실행
INFO:src.agent.agent:✅ 작업 결과 업로드 완료: task_... (completed)
```

**대시보드에서 결과 확인:**
1. 작업 목록에서 상태 필터: "completed" 선택
2. 완료된 작업 확인
3. "상세 정보 표시" 체크박스 선택하여 JSON 결과 확인

#### Step 4: 전체 스캔 작업 테스트

**대시보드에서:**
1. "전체 스캔 실행" 버튼 클릭
2. 작업 생성 확인

**Agent 로그 확인:**
```
INFO:src.agent.agent:대기 중인 작업 1개 발견
INFO:src.agent.agent:작업 처리 시작: task_... (FULL_SCAN)
INFO:src.agent.agent:✅ 작업 상태 업데이트: task_... -> running
INFO:src.agent.task_executor:전체 스캔 작업 실행
# ... 스캔 진행 로그 ...
INFO:src.agent.agent:✅ 작업 결과 업로드 완료: task_... (completed)
```

**대시보드에서 결과 확인:**
- 작업 상태가 "completed"로 변경
- 결과 JSON에 스캔 결과 포함

#### Step 5: CCE 점검 작업 테스트

**대시보드에서:**
1. "CCE 점검 실행" 버튼 클릭
2. 작업 생성 확인

**Agent 로그 확인:**
```
INFO:src.agent.agent:대기 중인 작업 1개 발견
INFO:src.agent.agent:작업 처리 시작: task_... (CCE_CHECK)
INFO:src.agent.agent:✅ 작업 상태 업데이트: task_... -> running
INFO:src.agent.task_executor:CCE 점검 작업 실행
# ... 점검 진행 로그 ...
INFO:src.agent.agent:✅ 작업 결과 업로드 완료: task_... (completed)
```

---

## 6. 문제 해결

### 6.1 API 서버 연결 실패

**증상:**
```
ERROR:src.agent.agent:❌ Agent 등록 중 오류: Connection refused
```

**해결 방법:**
1. EC2 보안 그룹에서 포트 5000 열기 확인
2. API 서버 실행 확인:
   ```bash
   docker-compose logs api
   docker-compose ps api
   ```
3. 방화벽 확인:
   ```bash
   sudo ufw status
   sudo ufw allow 5000/tcp
   ```

### 6.2 Agent 토큰 검증 실패

**증상:**
```
ERROR:src.agent.agent:작업 조회 실패: 401 - {"error": "유효하지 않은 토큰입니다."}
```

**해결 방법:**
1. Agent가 자동으로 재등록 시도 (로그 확인)
2. 수동 재등록:
   ```bash
   # 설정 파일 삭제
   rm ~/.v2r_agent/config.json
   
   # Agent 재시작
   python src/agent/main.py
   ```

### 6.3 데이터베이스 연결 실패

**증상:**
```
ERROR: Database connection failed
```

**해결 방법:**
```bash
# PostgreSQL 컨테이너 상태 확인
docker-compose ps postgres

# 로그 확인
docker-compose logs postgres

# 재시작
docker-compose restart postgres

# 연결 테스트
docker exec v2r-postgres psql -U v2r -d v2r -c "SELECT 1"
```

### 6.4 Streamlit 대시보드 접속 불가

**증상:**
- 브라우저에서 접속 불가
- Connection refused

**해결 방법:**
1. Streamlit 실행 확인:
   ```bash
   docker exec v2r-app ps aux | grep streamlit
   ```
2. 수동 실행:
   ```bash
   docker exec -it v2r-app streamlit run src/dashboard/app.py \
       --server.port 8501 \
       --server.address 0.0.0.0
   ```
3. 보안 그룹에서 포트 8501 열기 확인

### 6.5 작업이 pending 상태에서 멈춤

**확인 사항:**
1. Agent가 실행 중인지 확인
2. Agent 로그에서 폴링 동작 확인
3. API 서버 로그 확인:
   ```bash
   docker-compose logs api | grep "tasks"
   ```

---

## 7. 모니터링 및 로그

### 7.1 로그 확인 명령어

**EC2 서버에서:**
```bash
# 전체 서비스 로그
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f api
docker-compose logs -f postgres
docker-compose logs -f app

# 최근 100줄
docker-compose logs --tail=100 api
```

**로컬 PC Agent:**
- Agent 실행 터미널에서 실시간 로그 확인
- 또는 로그 파일로 리다이렉트:
  ```bash
  python src/agent/main.py > agent.log 2>&1
  tail -f agent.log
  ```

### 7.2 데이터베이스 확인

**Agent 목록 조회:**
```bash
docker exec v2r-postgres psql -U v2r -d v2r -c "SELECT agent_id, agent_name, status, last_seen FROM agents;"
```

**작업 목록 조회:**
```bash
docker exec v2r-postgres psql -U v2r -d v2r -c "SELECT task_id, agent_id, task_type, status, created_at FROM agent_tasks ORDER BY created_at DESC LIMIT 10;"
```

---

## 8. 프로덕션 배포 고려사항

### 8.1 보안 강화

1. **환경 변수 관리**
   - `.env` 파일을 Git에 커밋하지 않음
   - AWS Secrets Manager 또는 환경 변수 사용

2. **API 서버 보안**
   - HTTPS 사용 (Nginx 리버스 프록시)
   - API 키 또는 추가 인증 레이어 고려

3. **데이터베이스 보안**
   - 강력한 비밀번호 사용
   - 외부 접근 제한 (보안 그룹)

### 8.2 성능 최적화

1. **리소스 모니터링**
   ```bash
   # 컨테이너 리소스 사용량
   docker stats
   ```

2. **데이터베이스 인덱스 확인**
   ```bash
   docker exec v2r-postgres psql -U v2r -d v2r -c "\di"
   ```

### 8.3 백업

**데이터베이스 백업:**
```bash
# 백업
docker exec v2r-postgres pg_dump -U v2r v2r > backup_$(date +%Y%m%d).sql

# 복원
docker exec -i v2r-postgres psql -U v2r v2r < backup_20250130.sql
```

---

## 9. 빠른 시작 체크리스트

### EC2 서버 설정
- [ ] EC2 인스턴스 생성 및 SSH 접속
- [ ] Docker 및 Docker Compose 설치
- [ ] 프로젝트 파일 배포
- [ ] `.env` 파일 설정
- [ ] `docker-compose up -d` 실행
- [ ] API 서버 확인: `curl http://localhost:5000/api/agents`
- [ ] Streamlit 대시보드 실행 및 접속 확인

### 로컬 PC Agent 설정
- [ ] 환경 변수 설정 (`AGENT_SERVER_URL`, `AGENT_NAME`)
- [ ] Agent 실행 및 등록 확인
- [ ] 설정 파일 저장 확인: `~/.v2r_agent/config.json`

### 통합 테스트
- [ ] 대시보드에서 Agent 목록 확인
- [ ] "Docker 상태 조회" 작업 생성 및 실행
- [ ] 작업 결과 확인
- [ ] "전체 스캔 실행" 테스트
- [ ] "CCE 점검 실행" 테스트

---

## 10. 빠른 테스트 스크립트

**EC2 서버에서 실행:**
```bash
# Linux/Mac
chmod +x scripts/deployment/quick_test.sh
./scripts/deployment/quick_test.sh

# Windows PowerShell
.\scripts\deployment\quick_test.ps1
```

이 스크립트는 다음을 자동으로 확인합니다:
- Docker 서비스 상태
- API 서버 응답
- 데이터베이스 테이블 존재 여부
- 등록된 Agent 수
- Streamlit 대시보드 실행 상태

---

## 11. 참고 자료

- 프로젝트 구조: `docs/PROJECT_STRUCTURE.md`
- 점검 결과: `docs/CHECKING_POINT.md`
- 배포 스크립트: `scripts/deployment/`

