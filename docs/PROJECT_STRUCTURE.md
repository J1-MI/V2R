# V2R 프로젝트 구조

## 디렉토리 구조

```
V2R/
├── src/                          # 소스 코드
│   ├── scanner/                  # 스캐너 모듈
│   │   ├── nmap_scanner.py      # Nmap 스캐너
│   │   ├── nuclei_scanner.py    # Nuclei 스캐너
│   │   ├── vulnerability_checker.py  # 취약점 체커
│   │   ├── normalizer.py        # 결과 정규화
│   │   └── docker_lab.py        # Docker Lab 스캔 함수
│   ├── pipeline/                 # 파이프라인 모듈
│   │   ├── scanner_pipeline.py  # 스캔 파이프라인
│   │   └── poc_pipeline.py      # PoC 재현 파이프라인
│   ├── cce/                      # CCE 점검 모듈
│   │   ├── checker.py           # CCE 점검 실행
│   │   └── generator.py         # CCE 스크립트 생성
│   ├── database/                 # 데이터베이스 모듈
│   │   ├── connection.py        # DB 연결
│   │   ├── models.py            # ORM 모델
│   │   ├── repository.py        # Repository 패턴
│   │   └── schema.sql           # DB 스키마
│   ├── dashboard/                # 대시보드 모듈
│   │   ├── app.py               # Streamlit 대시보드
│   │   └── api_client.py        # API 클라이언트
│   ├── poc/                      # PoC 재현 모듈
│   │   ├── isolation.py         # 격리 환경
│   │   ├── reproduction.py      # PoC 재현
│   │   └── evidence.py          # 증거 수집
│   ├── api/                      # Flask API 서버
│   │   ├── app.py               # Flask 앱 팩토리
│   │   ├── run_api.py           # API 서버 실행
│   │   ├── middleware/          # 미들웨어
│   │   │   └── auth.py         # 인증 미들웨어
│   │   └── blueprints/          # Blueprint
│   │       └── agents.py       # Agent 관리 API
│   ├── agent/                    # Agent 프로그램
│   │   ├── agent.py             # Agent 메인 클래스
│   │   ├── config.py            # Agent 설정
│   │   ├── task_executor.py     # 작업 실행
│   │   └── main.py              # Agent 실행 진입점
│   ├── utils/                    # 공통 유틸리티
│   │   └── id_generator.py      # ID 생성 유틸리티 (Agent 토큰 포함)
│   ├── llm/                      # LLM 모듈
│   │   └── report_generator.py  # LLM 리포트 생성
│   ├── report/                   # 리포트 모듈
│   │   ├── generator.py         # 리포트 생성
│   │   └── pr_template.py       # PR 템플릿
│   ├── verification/             # 검증 모듈
│   │   └── reliability.py       # 신뢰도 점수화
│   └── config.py                # 설정 관리
├── scripts/                      # 스크립트
│   ├── cce_checks.sh            # CCE 점검 스크립트
│   ├── scan_cve_lab.ps1         # CVE-Lab 스캔 스크립트
│   ├── test/                    # 테스트 스크립트
│   ├── utils/                   # 유틸리티 스크립트
│   ├── agent/                   # Agent 시작 스크립트
│   │   └── start_agent.py       # Agent 실행 스크립트
│   └── deployment/              # 배포 스크립트
├── infra/                        # 인프라 설정
│   ├── docker/                  # Docker 설정
│   │   ├── docker-compose.yml   # 개발 환경
│   │   ├── docker-compose.prod.yml  # 프로덕션 환경
│   │   ├── Dockerfile           # 프로덕션 이미지
│   │   └── Dockerfile.dev       # 개발 이미지
│   └── terraform/               # Terraform 설정
│       ├── main.tf
│       ├── vpc.tf
│       ├── ec2.tf
│       └── user_data/
├── evidence/                     # PoC 증적 파일
├── reports/                      # 생성된 리포트
├── docs/                         # 문서
├── data.json                     # CCE 점검 데이터
├── requirements.txt              # Python 의존성
└── README.md                     # 프로젝트 설명
```

## 주요 모듈 설명

### 스캐너 모듈 (`src/scanner/`)
- **NmapScanner**: 포트 및 서비스 스캔
- **NucleiScanner**: 취약점 템플릿 기반 스캔
- **VulnerabilityChecker**: 특정 취약점 체크 (Redis, MongoDB 등)
- **ScanResultNormalizer**: 스캔 결과 정규화

### 파이프라인 모듈 (`src/pipeline/`)
- **ScannerPipeline**: 스캔 실행 → 정규화 → DB 저장 파이프라인
- **POCPipeline**: PoC 재현 → 증거 수집 → DB 저장 파이프라인

### CCE 모듈 (`src/cce/`)
- **checker.py**: Docker 컨테이너 대상 CCE 점검 실행
- **generator.py**: CCE 점검 스크립트 자동 생성

### 데이터베이스 모듈 (`src/database/`)
- **connection.py**: PostgreSQL 연결 관리
- **models.py**: SQLAlchemy ORM 모델
- **repository.py**: Repository 패턴 구현

### API 모듈 (`src/api/`)
- **app.py**: Flask 애플리케이션 팩토리 함수 (`create_app()`)
- **run_api.py**: Flask API 서버 실행 진입점
- **middleware/auth.py**: Agent 토큰 기반 인증 미들웨어
- **blueprints/agents.py**: Agent 관리 REST API (등록, 작업 생성, 결과 업로드)

### Agent 모듈 (`src/agent/`)
- **agent.py**: Agent 메인 클래스 (등록, 폴링, 작업 실행)
- **task_executor.py**: 작업 실행 로직 (Docker 상태, 전체 스캔, CCE 점검)
- **config.py**: Agent 설정 관리
- **storage.py**: Agent 토큰 영구 저장 관리 (`~/.v2r_agent/config.json`)
- **main.py**: Agent 실행 진입점

### 유틸리티 모듈 (`src/utils/`)
- **id_generator.py**: 스캔 ID, 세션 ID, 컨테이너 이름, Agent ID/토큰 생성 및 해시화

## Import 경로 규칙

모든 Python 모듈은 절대 경로를 사용합니다:

```python
# ✅ 올바른 방법
from src.scanner import NmapScanner
from src.database import get_db
from src.utils.id_generator import generate_scan_id

# ❌ 잘못된 방법
from .scanner import NmapScanner
from ..database import get_db
```

## 주요 변경사항 (2025-01)

1. **디렉토리 재구성**
   - `scripts/compliance/` → `src/cce/`로 이동
   - `terraform/` → `infra/terraform/`로 이동
   - Docker 파일 → `infra/docker/`로 이동

2. **공통 유틸리티 추가**
   - `src/utils/id_generator.py`: ID 생성 로직 통일

3. **Import 경로 통일**
   - 모든 상대 import를 절대 import로 변경

4. **중복 코드 제거**
   - 스캔 ID 생성 로직 통일
   - 세션 ID 생성 로직 통일
   - 컨테이너 이름 생성 로직 통일

5. **Agent 구조 도입 (2025-01)**
   - Flask API 서버 추가 (`src/api/`)
   - Agent 프로그램 추가 (`src/agent/`)
   - Docker/스캔 로직 함수화 (`src/scanner/docker_lab.py`)
   - 대시보드에 Agent 제어 UI 추가
   - 데이터베이스에 agents, agent_tasks 테이블 추가
