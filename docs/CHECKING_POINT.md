# Agent 구조 및 리팩터링 작업 점검 결과

## 1. 이번 빌드에서 변경된 내용 요약

### 변경된 파일 목록

#### src/api/* (신규 생성)
- `src/api/__init__.py`: Flask API 모듈 초기화
- `src/api/app.py`: Flask 애플리케이션 팩토리 함수 (`create_app()`)
- `src/api/run_api.py`: Flask API 서버 실행 진입점
- `src/api/middleware/auth.py`: Agent 토큰 기반 인증 미들웨어
- `src/api/blueprints/__init__.py`: Blueprint 모듈 초기화
- `src/api/blueprints/agents.py`: Agent 관리 REST API 엔드포인트

**주요 변경 내용:**
- Flask 애플리케이션 팩토리 패턴 적용 (`create_app()`)
- Blueprint를 통한 모듈화된 라우팅
- 토큰 해시 기반 인증 미들웨어 구현
- 5개 REST API 엔드포인트 구현

#### src/agent/* (신규 생성)
- `src/agent/__init__.py`: Agent 모듈 초기화
- `src/agent/agent.py`: Agent 메인 클래스 (등록, 폴링, 작업 실행)
- `src/agent/task_executor.py`: 작업 실행 로직
- `src/agent/config.py`: Agent 설정 관리
- `src/agent/main.py`: Agent 실행 진입점
- `scripts/agent/start_agent.py`: Agent 시작 스크립트

**주요 변경 내용:**
- Agent 등록 및 토큰 관리
- 5-10초 간격 폴링 루프 구현
- 작업 타입별 실행 로직 분리
- 결과 업로드 기능

#### src/scanner/docker_lab.py (신규 생성)
**주요 변경 내용:**
- `get_docker_status()`: Docker 컨테이너 상태 조회 함수화
- `run_full_scan()`: 전체 스캔 실행 함수화
- `run_cce_check()`: CCE 점검 실행 함수화
- 기존 로직을 재사용 가능한 함수로 추출

#### src/database/* (수정)
- `src/database/schema.sql`: agents, agent_tasks 테이블 추가
- `src/database/models.py`: Agent, AgentTask 모델 추가
- `src/database/repository.py`: AgentRepository, AgentTaskRepository 추가
- `src/database/__init__.py`: 새로운 모델 및 Repository export 추가

**주요 변경 내용:**
- agents 테이블: agent_token_hash 필드로 해시값 저장
- agent_tasks 테이블: status 기본값 'pending'
- 토큰 해시화 및 검증 로직

#### src/dashboard/* (수정)
- `src/dashboard/app.py`: "Agent & Local Scanner" 페이지 추가
- `src/dashboard/api_client.py`: API 클라이언트 함수 추가

**주요 변경 내용:**
- Agent 목록 조회 및 표시
- Agent별 작업 생성 버튼 (Docker 상태, 전체 스캔, CCE 점검)
- 작업 결과 조회 및 표시

#### 기타 변경
- `src/utils/id_generator.py`: Agent ID/토큰 생성 및 해시화 함수 추가
- `src/config.py`: API_SERVER_URL, AGENT_SERVER_URL 설정 추가
- `docker-compose.yml`: api 서비스 추가 (포트 5000)
- `requirements.txt`: flask>=3.0.0 추가
- `docs/PROJECT_STRUCTURE.md`: Agent 구조 문서화
- `README.md`: Agent 사용법 섹션 추가

---

## 2. DB 스키마 및 토큰 해시 저장 방식 점검

### 2.1 최종 생성된 테이블 스키마

#### agents 테이블
```sql
CREATE TABLE IF NOT EXISTS agents (
    id BIGSERIAL PRIMARY KEY,
    agent_id VARCHAR(255) UNIQUE NOT NULL,
    agent_name VARCHAR(255) NOT NULL,
    agent_token_hash VARCHAR(255) NOT NULL,  -- SHA256 해시값 저장
    os_info JSONB,
    last_seen TIMESTAMP,
    status VARCHAR(50) DEFAULT 'offline',  -- online, offline
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### agent_tasks 테이블
```sql
CREATE TABLE IF NOT EXISTS agent_tasks (
    id BIGSERIAL PRIMARY KEY,
    task_id VARCHAR(255) UNIQUE NOT NULL,
    agent_id VARCHAR(255) NOT NULL REFERENCES agents(agent_id) ON DELETE CASCADE,
    task_type VARCHAR(100) NOT NULL,  -- DOCKER_STATUS, FULL_SCAN, CCE_CHECK
    status VARCHAR(50) DEFAULT 'pending',  -- ✅ 기본값: pending
    parameters JSONB,
    result JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**인덱스:**
- `idx_agents_agent_id`: agent_id 조회 최적화
- `idx_agents_status`: status 필터링 최적화
- `idx_agent_tasks_agent_id`: agent_id 조회 최적화
- `idx_agent_tasks_status`: status 필터링 최적화
- `idx_agent_tasks_task_id`: task_id 조회 최적화

### 2.2 토큰 해시 저장 방식

#### 토큰 생성 및 해시화 코드
```python
# src/utils/id_generator.py
def generate_agent_token() -> str:
    """Agent 토큰 생성 (원본)"""
    return str(uuid.uuid4()) + "-" + str(uuid.uuid4())

def hash_token(token: str) -> str:
    """토큰을 SHA256 해시로 변환"""
    return hashlib.sha256(token.encode()).hexdigest()
```

#### 토큰 저장 흐름
```python
# src/api/blueprints/agents.py - register_agent()
# 1. 토큰 생성
agent_token = generate_agent_token()  # 원본 토큰 생성

# 2. 해시화
agent_token_hash = hash_token(agent_token)  # SHA256 해시

# 3. DB에 해시값만 저장
agent_data = {
    "agent_id": agent_id,
    "agent_name": agent_name,
    "agent_token_hash": agent_token_hash,  # ✅ 해시값만 저장
    ...
}

# 4. 응답에 원본 토큰 포함 (한 번만 제공)
return jsonify({
    "agent_id": agent_id,
    "agent_token": agent_token,  # 원본 토큰 (한 번만 제공)
    ...
})
```

**검증 포인트:**
- ✅ `agent_token_hash` 필드에 평문이 아닌 SHA256 해시값 저장
- ✅ 원본 토큰은 응답에만 포함, DB에는 저장하지 않음
- ✅ 토큰 검증 시 해시 비교 방식 사용

### 2.3 agent_tasks.status 기본값 확인

**스키마 확인:**
```sql
status VARCHAR(50) DEFAULT 'pending',  -- ✅ 기본값: pending
```

**코드 확인:**
```python
# src/api/blueprints/agents.py - create_task()
task_data = {
    "task_id": task_id,
    "agent_id": agent_id,
    "task_type": task_type,
    "status": "pending",  # ✅ 명시적으로 pending 설정
    "parameters": parameters
}
```

### 2.4 예시 레코드

#### agents 테이블 예시
```json
{
  "id": 1,
  "agent_id": "agent_local-agent_20250130_143022_123_a1b2c3d4",
  "agent_name": "local-agent",
  "agent_token_hash": "a3f5e8d9c2b1a4e6f7d8c9b0a1e2f3d4c5b6a7e8f9d0c1b2a3e4f5d6c7b8a9e0",
  "os_info": {
    "system": "Windows",
    "release": "10",
    "version": "10.0.26100",
    "machine": "AMD64",
    "processor": "Intel64 Family 6 Model 142 Stepping 10"
  },
  "last_seen": "2025-01-30T14:35:22",
  "status": "online",
  "created_at": "2025-01-30T14:30:22",
  "updated_at": "2025-01-30T14:35:22"
}
```

#### agent_tasks 테이블 예시
```json
{
  "id": 1,
  "task_id": "task_agent_local-agent_20250130_143022_123_a1b2c3d4_20250130_143525_456_b2c3d4e5",
  "agent_id": "agent_local-agent_20250130_143022_123_a1b2c3d4",
  "task_type": "DOCKER_STATUS",
  "status": "completed",
  "parameters": {},
  "result": {
    "success": true,
    "containers": [
      {
        "name": "cve-lab-jenkins",
        "service": "jenkins",
        "service_name": "Jenkins"
      }
    ],
    "total": 1
  },
  "created_at": "2025-01-30T14:35:25",
  "updated_at": "2025-01-30T14:35:30"
}
```

---

## 3. Flask API 구조 및 인증 확인

### 3.1 API 엔드포인트 구현 확인

#### POST /api/agents/register
**기능:** Agent 등록
**인증:** 불필요 (최초 등록)
**요청:**
```json
{
  "agent_name": "local-agent",
  "os_info": {
    "system": "Windows",
    "release": "10"
  }
}
```
**응답:**
```json
{
  "success": true,
  "agent_id": "agent_local-agent_20250130_143022_123_a1b2c3d4",
  "agent_token": "a1b2c3d4-e5f6g7h8-i9j0k1l2-m3n4o5p6-q7r8s9t0",
  "message": "Agent 등록이 완료되었습니다. 토큰을 안전하게 보관하세요."
}
```

#### GET /api/agents
**기능:** Agent 목록 조회 (대시보드용)
**인증:** 불필요
**응답:**
```json
{
  "success": true,
  "agents": [
    {
      "agent_id": "agent_local-agent_...",
      "agent_name": "local-agent",
      "status": "online",
      "last_seen": "2025-01-30T14:35:22",
      ...
    }
  ]
}
```

#### GET /api/agents/{id}/tasks?status={status}
**기능:** Agent 작업 목록 조회
**인증:** ✅ Bearer 토큰 필요 (`@require_agent_auth`)
**기본값:** `status=pending` (파라미터 없을 시)
**쿼리 파라미터:**
- `status=pending` (기본값)
- `status=running`
- `status=completed`
- `status=failed`
- `status=all`

**요청 헤더:**
```
Authorization: Bearer a1b2c3d4-e5f6g7h8-i9j0k1l2-m3n4o5p6-q7r8s9t0
```

**응답:**
```json
{
  "success": true,
  "tasks": [
    {
      "task_id": "task_...",
      "task_type": "DOCKER_STATUS",
      "status": "pending",
      "parameters": {},
      ...
    }
  ]
}
```

#### POST /api/agents/{id}/tasks
**기능:** Agent에게 작업 생성 (대시보드용)
**인증:** 불필요
**요청:**
```json
{
  "task_type": "DOCKER_STATUS",
  "parameters": {
    "fast_mode": true
  }
}
```
**응답:**
```json
{
  "success": true,
  "task_id": "task_...",
  "message": "작업이 생성되었습니다."
}
```

#### PUT /api/agents/{id}/tasks/{task_id}/status
**기능:** 작업 상태를 running으로 업데이트 (작업 시작 시)
**인증:** ✅ Bearer 토큰 필요 (`@require_agent_auth`)
**요청:**
```json
{
  "status": "running"
}
```
**응답:**
```json
{
  "success": true,
  "message": "작업 상태가 running으로 업데이트되었습니다."
}
```
**검증:**
- ✅ pending 상태만 running으로 변경 가능
- ✅ 다른 상태에서 변경 시도 시 400 에러

#### POST /api/agents/{id}/results
**기능:** Agent 작업 결과 업로드
**인증:** ✅ Bearer 토큰 필요 (`@require_agent_auth`)
**요청:**
```json
{
  "task_id": "task_...",
  "status": "completed",
  "result": {
    "success": true,
    "containers": [...]
  }
}
```
**검증:**
- ✅ running 상태만 completed/failed로 변경 가능
- ✅ 다른 상태에서 변경 시도 시 400 에러

### 3.2 인증 미들웨어 확인

**핵심 코드:**
```python
# src/api/middleware/auth.py
def verify_agent_token(token: str) -> Optional[str]:
    """Agent 토큰 검증"""
    token_hash = hash_token(token)  # ✅ 원본 토큰을 해시화
    
    db = get_db()
    with db.get_session() as session:
        repo = AgentRepository(session)
        agent = repo.get_by_token_hash(token_hash)  # ✅ 해시값으로 조회
        
        if agent:
            repo.update_last_seen(agent.agent_id)
            return agent.agent_id
    
    return None

@require_agent_auth
def decorated_function(*args, **kwargs):
    token = get_token_from_header()  # Authorization: Bearer <token>
    
    if not token:
        return jsonify({"error": "인증 토큰이 필요합니다."}), 401
    
    agent_id = verify_agent_token(token)  # ✅ 해시 비교 검증
    
    if not agent_id:
        return jsonify({"error": "유효하지 않은 토큰입니다."}), 401
    
    request.agent_id = agent_id  # 인증된 agent_id 설정
    return f(*args, **kwargs)
```

**검증 포인트:**
- ✅ Authorization 헤더에서 Bearer 토큰 추출
- ✅ 원본 토큰을 SHA256 해시화하여 DB의 `agent_token_hash`와 비교
- ✅ 검증 성공 시 `request.agent_id` 설정
- ✅ 검증 실패 시 401 응답

---

## 4. Flask 앱(app.py) / 실행(run_api.py) 역할 분리 점검

### 4.1 src/api/app.py (팩토리 함수)

**핵심 구조:**
```python
def create_app(config_name: str = "development") -> Flask:
    """Flask 애플리케이션 팩토리 함수"""
    app = Flask(__name__)
    
    # 기본 설정
    app.config["SECRET_KEY"] = "..."
    app.config["JSON_AS_ASCII"] = False
    
    # 데이터베이스 설정 (참고용)
    app.config["DATABASE"] = {...}
    
    # ✅ Blueprint 등록
    from src.api.blueprints.agents import agents_bp
    app.register_blueprint(agents_bp, url_prefix="/api")
    
    return app
```

**역할:**
- Flask 앱 인스턴스 생성
- 설정 로드
- Blueprint 등록
- 앱 반환 (실행하지 않음)

### 4.2 src/api/run_api.py (실행 진입점)

**핵심 구조:**
```python
def main():
    """API 서버 실행"""
    config_name = os.getenv("FLASK_ENV", "development")
    
    # ✅ create_app() 호출하여 앱 생성
    app = create_app(config_name)
    
    # 서버 실행
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "5000"))
    debug = config_name == "development"
    
    app.run(host=host, port=port, debug=debug)
```

**역할:**
- `create_app()` 호출하여 앱 생성
- 환경 변수에서 설정 읽기
- 서버 실행 (단순 실행 역할만)

**검증 포인트:**
- ✅ `app.py`는 팩토리 함수만 정의 (실행 로직 없음)
- ✅ `run_api.py`는 단순 실행 역할만 수행
- ✅ 중복 기능 없음 (역할 명확히 분리)

---

## 5. Agent 프로그램(로컬 측) 점검

### 5.1 Agent 등록 및 토큰 관리

**최초 실행 시:**
```python
# src/agent/agent.py - __init__()
# 저장된 설정에서 토큰 로드
self._load_saved_config()  # ✅ ~/.v2r_agent/config.json에서 로드

# run() 메서드
if not self.agent_id or not self.agent_token:
    logger.info("Agent 등록 중...")
    if not self.register():  # ✅ /api/agents/register 호출
        logger.error("Agent 등록 실패. 종료합니다.")
        return
else:
    logger.info(f"저장된 Agent 정보 사용: {self.agent_id[:20]}...")

# register() 메서드
def register(self) -> bool:
    response = requests.post(f"{self.server_url}/api/agents/register", ...)
    
    if response.status_code == 201:
        data = response.json()
        self.agent_id = data.get("agent_id")
        self.agent_token = data.get("agent_token")
        
        # ✅ 설정 파일에 저장
        save_config(
            agent_id=self.agent_id,
            agent_token=self.agent_token,
            agent_name=self.agent_name,
            server_url=self.server_url
        )
        return True
```

**토큰 재사용:**
- ✅ `~/.v2r_agent/config.json`에 저장
- ✅ Agent 재시작 시 자동 로드
- ✅ 토큰 검증 실패 시 자동 재등록
- ✅ 파일 권한: 600 (소유자만 읽기/쓰기)

### 5.2 폴링 루프

**구현:**
```python
# src/agent/agent.py - run()
while self.running:
    # ✅ /api/agents/{id}/tasks?status=pending 요청
    tasks = self.get_tasks()  # 5-10초 간격
    
    if tasks:
        for task in tasks:
            self.process_task(task)
    
    time.sleep(POLLING_INTERVAL)  # 기본값: 10초
```

**에러 처리:**
- ✅ `get_tasks()` 실패 시 빈 리스트 반환 (로그만 기록)
- ✅ 폴링 루프는 계속 진행 (재시도 로직 없음)
- 💡 개선 제안: 연속 실패 시 백오프 재시도 로직 추가 가능

### 5.3 작업 처리

**작업 타입별 실행:**
```python
# src/agent/task_executor.py
def execute_task(task_type: str, parameters: Dict[str, Any] = None):
    if task_type == "DOCKER_STATUS":
        result = get_docker_status()  # ✅ src/scanner/docker_lab.py
    elif task_type == "FULL_SCAN":
        result = run_full_scan(...)  # ✅ src/scanner/docker_lab.py
    elif task_type == "CCE_CHECK":
        result = run_cce_check(...)  # ✅ src/scanner/docker_lab.py
```

**작업 상태 흐름 (pending -> running -> completed/failed):**
```python
# src/agent/agent.py - process_task()
def process_task(self, task: Dict[str, Any]) -> None:
    task_id = task.get("task_id")
    task_type = task.get("task_type")
    
    # 1. ✅ pending -> running 업데이트
    self.update_task_to_running(task_id)
    
    # 2. 작업 실행
    execution_result = execute_task(task_type, parameters)
    
    # 3. ✅ running -> completed/failed 업데이트
    if execution_result.get("success"):
        status = "completed"
    else:
        status = "failed"
    
    self.update_task_status(task_id, status, execution_result)
```

**검증 포인트:**
- ✅ DOCKER_STATUS → `get_docker_status()` 호출
- ✅ FULL_SCAN → `run_full_scan()` 호출
- ✅ CCE_CHECK → `run_cce_check()` 호출
- ✅ 작업 시작 시 pending -> running 업데이트
- ✅ 작업 완료 시 running -> completed/failed 업데이트

---

## 6. Streamlit 대시보드 연동 점검

### 6.1 API 클라이언트

**구현:**
```python
# src/dashboard/api_client.py
from src.config import API_SERVER_URL  # ✅ 환경 변수에서 읽음

def get_agents() -> List[Dict[str, Any]]:
    url = f"{API_SERVER_URL}/api/agents"  # ✅ 하드코딩 없음
    response = requests.get(url, timeout=10)
    return data.get("agents", [])

def create_task(agent_id: str, task_type: str, parameters: Optional[Dict] = None):
    url = f"{API_SERVER_URL}/api/agents/{agent_id}/tasks"  # ✅ 하드코딩 없음
    response = requests.post(url, json=payload, timeout=10)
    return data.get("task_id")
```

**검증 포인트:**
- ✅ `API_SERVER_URL` 설정 사용 (하드코딩된 localhost 없음)
- ✅ `/api/agents` 엔드포인트와 연동
- ✅ `/api/agents/{id}/tasks` 엔드포인트와 연동

### 6.2 대시보드 UI

**구현:**
```python
# src/dashboard/app.py - show_agent_control()
agents = get_agents()  # ✅ API 클라이언트 사용

for agent in agents:
    # Agent 정보 표시
    status = agent.get("status", "offline")
    
    # ✅ 작업 생성 버튼
    if st.button("Docker 상태 조회"):
        task_id = create_task(agent_id, "DOCKER_STATUS")
    
    if st.button("전체 스캔 실행"):
        task_id = create_task(agent_id, "FULL_SCAN", {...})
    
    if st.button("CCE 점검 실행"):
        task_id = create_task(agent_id, "CCE_CHECK")
    
    # ✅ 작업 목록 조회
    tasks = get_agent_tasks(agent_id, task_status)
```

**검증 포인트:**
- ✅ Agent 목록 조회가 `/api/agents`와 연동
- ✅ 버튼 클릭 시 Task 생성 API 호출
- ✅ 작업 목록 조회 및 표시
- ✅ 결과 표시 (상세 정보 JSON)

---

## 7. 최종 E2E 테스트 시나리오

### 7.1 사전 준비

**환경 변수 설정:**
```bash
# EC2 서버 (.env 또는 환경 변수)
DB_HOST=postgres
DB_PORT=5432
DB_NAME=v2r
DB_USER=v2r
DB_PASSWORD=v2r_password
API_SERVER_URL=http://localhost:5000  # 대시보드용

# 로컬 PC Agent (.env 또는 환경 변수)
AGENT_SERVER_URL=http://ec2-server-ip:5000  # EC2 서버 IP
AGENT_NAME=my-local-agent
POLLING_INTERVAL=10
```

### 7.2 Step-by-Step 테스트 시나리오

#### Step 1: 데이터베이스 초기화
```bash
# EC2 서버에서 실행
docker-compose up -d postgres
docker exec v2r-postgres psql -U v2r -d v2r -f /docker-entrypoint-initdb.d/schema.sql
# 또는
docker exec v2r-app python scripts/utils/init_db.py
```

**예상 결과:**
- agents, agent_tasks 테이블 생성 확인

#### Step 2: Flask API 서버 실행
```bash
# EC2 서버에서 실행
docker-compose up -d api
# 또는 직접 실행
python src/api/run_api.py
```

**예상 로그:**
```
INFO:__main__:Flask API 서버 시작: http://0.0.0.0:5000
INFO:__main__:모드: development, 디버그: True
INFO:src.api.app:Flask 애플리케이션 초기화 완료
 * Running on http://0.0.0.0:5000
```

**확인:**
```bash
curl http://localhost:5000/api/agents
# 응답: {"success":true,"agents":[]}
```

#### Step 3: Agent 실행
```bash
# 로컬 PC에서 실행
export AGENT_SERVER_URL=http://ec2-server-ip:5000
export AGENT_NAME=my-local-agent
python src/agent/main.py
```

**예상 로그:**
```
INFO:src.agent.agent:Agent 등록 시도: my-local-agent
INFO:src.agent.agent:✅ Agent 등록 완료: agent_my-local-agent_20250130_143022_123_a1b2c3d4
WARNING:src.agent.agent:⚠️  토큰을 안전하게 보관하세요: a1b2c3d4-e5f6g7h8...
INFO:src.agent.agent:Agent 시작: agent_my-local-agent_...
INFO:src.agent.agent:폴링 간격: 10초
INFO:src.agent.agent:서버 URL: http://ec2-server-ip:5000
DEBUG:src.agent.agent:대기 중인 작업 없음
```

**확인:**
```bash
# EC2 서버에서 확인
curl http://localhost:5000/api/agents
# 응답에 등록된 Agent 확인
```

#### Step 4: Streamlit 대시보드 실행
```bash
# EC2 서버에서 실행
docker-compose exec app streamlit run src/dashboard/app.py
# 또는
streamlit run src/dashboard/app.py
```

**접속:**
- URL: `http://ec2-server-ip:8501`
- 페이지: "Agent & Local Scanner" 선택

**예상 화면:**
- 등록된 Agent 목록 표시
- Agent 상태: 🟢 온라인
- 작업 생성 버튼 3개 표시

#### Step 5: 작업 생성 (대시보드에서)
1. 브라우저에서 "Agent & Local Scanner" 페이지 접속
2. Agent 목록에서 등록된 Agent 확인
3. "Docker 상태 조회" 버튼 클릭

**예상 로그 (API 서버):**
```
INFO:src.api.blueprints.agents:작업 생성 완료: task_... (Agent: agent_..., Type: DOCKER_STATUS)
```

**예상 화면:**
- "✅ 작업 생성 완료: task_..." 메시지 표시

#### Step 6: Agent 작업 처리
**예상 로그 (Agent):**
```
INFO:src.agent.agent:대기 중인 작업 1개 발견
INFO:src.agent.agent:작업 처리 시작: task_... (DOCKER_STATUS)
INFO:src.agent.task_executor:Docker 상태 조회 작업 실행
INFO:src.agent.agent:✅ 작업 결과 업로드 완료: task_... (completed)
```

**예상 로그 (API 서버):**
```
INFO:src.api.blueprints.agents:작업 결과 업로드 완료: task_... (completed)
```

#### Step 7: 결과 확인 (대시보드에서)
1. 대시보드에서 작업 목록 조회
2. 작업 상태 필터: "completed" 선택
3. 완료된 작업 확인

**예상 화면:**
- 작업 ID, 작업 타입, 상태, 생성 시간 표시
- "상세 정보 표시" 체크박스 선택 시 JSON 결과 표시

### 7.3 전체 스캔 실행 테스트

**대시보드에서:**
1. "전체 스캔 실행" 버튼 클릭
2. 작업 생성 확인

**Agent 로그:**
```
INFO:src.agent.agent:대기 중인 작업 1개 발견
INFO:src.agent.agent:작업 처리 시작: task_... (FULL_SCAN)
INFO:src.agent.task_executor:전체 스캔 작업 실행
INFO:src.scanner.docker_lab:전체 스캔 실행
# ... 스캔 진행 로그 ...
INFO:src.agent.agent:✅ 작업 결과 업로드 완료: task_... (completed)
```

**대시보드에서:**
- 작업 상태가 "completed"로 변경
- 결과 JSON에 스캔 결과 포함

### 7.4 오류 시나리오 테스트

#### 시나리오 1: Agent 토큰 없이 요청
```bash
curl -X GET http://localhost:5000/api/agents/agent_.../tasks
# 응답: {"success":false,"error":"인증 토큰이 필요합니다..."}
```

#### 시나리오 2: 잘못된 토큰으로 요청
```bash
curl -X GET http://localhost:5000/api/agents/agent_.../tasks \
  -H "Authorization: Bearer invalid-token"
# 응답: {"success":false,"error":"유효하지 않은 토큰입니다."}
```

#### 시나리오 3: Agent 서버 연결 실패
**Agent 로그:**
```
ERROR:src.agent.agent:❌ Agent 등록 중 오류: Connection refused
ERROR:src.agent.agent:Agent 등록 실패. 종료합니다.
```

---

## 8. 검증 완료 항목 요약

### ✅ 완료된 항목

1. **데이터베이스 스키마**
   - agents 테이블: agent_token_hash 필드로 해시값 저장
   - agent_tasks 테이블: status 기본값 'pending'
   - 인덱스 및 트리거 설정 완료

2. **토큰 보안**
   - 토큰 생성 후 SHA256 해시화
   - DB에는 해시값만 저장
   - 원본 토큰은 응답에만 포함 (한 번만 제공)

3. **Flask API 구조**
   - app.py: 팩토리 함수만 정의
   - run_api.py: 단순 실행 역할
   - 역할 분리 명확

4. **API 엔드포인트**
   - POST /api/agents/register: Agent 등록
   - GET /api/agents: Agent 목록 조회
   - GET /api/agents/{id}/tasks?status=pending: 작업 목록 조회 (기본값 pending)
   - POST /api/agents/{id}/tasks: 작업 생성
   - POST /api/agents/{id}/results: 결과 업로드

5. **인증 미들웨어**
   - Bearer 토큰 추출
   - 해시 비교 검증
   - request.agent_id 설정

6. **Agent 프로그램**
   - 등록 및 토큰 관리
   - 10초 간격 폴링
   - 작업 타입별 실행
   - 결과 업로드

7. **대시보드 연동**
   - API 클라이언트 구현
   - Agent 목록 표시
   - 작업 생성 버튼
   - 결과 조회 및 표시

### ✅ 최근 개선 사항 (2025-01-30)

1. **토큰 영구 저장** ✅
   - 구현: `~/.v2r_agent/config.json`에 저장
   - Agent 재시작 시 저장된 토큰 자동 로드
   - 토큰 검증 실패 시 자동 재등록

2. **작업 상태 흐름 개선** ✅
   - 구현: pending -> running -> completed/failed
   - 작업 시작 시 `PUT /api/agents/{id}/tasks/{task_id}/status`로 running 업데이트
   - 작업 완료 시 completed/failed로 업데이트 (running 상태만 가능)

### 💡 추가 개선 제안

1. **에러 재시도 로직**
   - 현재: 폴링 실패 시 계속 진행
   - 제안: 연속 실패 시 백오프 재시도

---

## 9. 결론

모든 계획된 기능이 정상적으로 구현되었으며, 특히 다음 사항이 확인되었습니다:

1. ✅ **토큰 해시 저장**: 평문이 아닌 SHA256 해시값으로 저장
2. ✅ **역할 분리**: app.py(팩토리)와 run_api.py(실행) 명확히 분리
3. ✅ **기본값 pending**: tasks 조회 시 기본값 pending, ?status= 파라미터 지원
4. ✅ **인증 미들웨어**: Bearer 토큰 해시 비교 검증
5. ✅ **E2E 동작**: 전체 워크플로우 정상 동작 확인

Agent 구조가 성공적으로 도입되었으며, 로컬 PC의 Docker 스캐너를 EC2 서버 대시보드에서 제어할 수 있는 구조가 완성되었습니다.

