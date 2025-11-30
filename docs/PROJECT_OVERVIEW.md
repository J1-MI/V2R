# V2R 프로젝트 개요

## 프로젝트 소개

**V2R (Vuln2Report)**는 클라우드 기반 취약점 진단 및 리포트 자동화 시스템입니다. AWS 격리 테스트베드에서 취약점을 자동으로 스캔하고, PoC를 격리 환경에서 재현하며, 증거를 수집하여 신뢰도를 평가한 후, LLM 기반 리포트를 자동 생성하는 컨설팅형 워크플로우를 제공합니다.

## 핵심 목표

1. **자동화된 취약점 탐지**: Nmap, Nuclei 등 다양한 스캐너를 통합하여 포트 스캔, 서비스 탐지, 취약점 식별을 자동화
2. **격리된 PoC 재현**: Docker 기반 격리 환경에서 PoC를 안전하게 재현하고 증거를 수집
3. **신뢰도 기반 검증**: 출처 및 증거 기반으로 PoC의 신뢰도를 0-100 점수로 평가
4. **자동 리포트 생성**: LLM을 활용하여 Executive Summary와 기술본을 자동 생성
5. **CCE 기반 점검**: 금융보안원 기준 Linux 서버 보안 설정 점검 자동화

## 주요 기능

### 1. 스캐너 통합

- **Nmap 스캐너**: 포트 스캔 및 서비스 버전 탐지
- **Nuclei 스캔**: 템플릿 기반 취약점 스캔
- **취약점 체커**: Redis, MongoDB 등 특정 서비스의 무인증 접근 체크
- **결과 정규화**: 다양한 스캐너 결과를 공통 JSON 스키마로 변환

### 2. PoC 격리 재현

- **격리 환경**: Docker 컨테이너 기반 완전 격리된 실행 환경
- **증거 수집**:
  - 시스템콜 로그 (strace)
  - 네트워크 캡처 (tcpdump/pcap)
  - 파일 시스템 변화 추적 (diff)
- **자동 롤백**: 재현 실패 시 자동으로 환경 복구

### 3. 신뢰도 점수화

- **출처 가중치**: Exploit-DB, GitHub 등 출처별 신뢰도 가중치
- **증거 기반 점수**: 시스템콜, 네트워크, 파일 시스템 증거 기반 점수
- **최종 신뢰도**: 0-100 점수로 PoC의 신뢰도 평가

### 4. CCE 점검

- **자동 스크립트 생성**: JSON 기반 CCE 점검 항목에서 bash 스크립트 자동 생성
- **Docker 컨테이너 점검**: 실행 중인 Docker 컨테이너 대상 자동 점검
- **결과 저장**: 점검 결과를 데이터베이스에 저장하고 대시보드에서 확인

### 5. LLM 리포트 생성

- **Executive Summary**: LLM 기반 임원용 요약 자동 생성
- **기술본**: python-docx를 활용한 상세 기술 문서 생성
- **PR 템플릿**: GitHub PR 템플릿 자동 생성

### 6. 웹 대시보드

- **Streamlit 기반**: 직관적인 웹 인터페이스
- **취약점 리스트**: 스캔 결과를 심각도별로 정렬하여 표시
- **CCE 점검 결과**: 점검 세션별 결과 조회 및 통계
- **리포트 생성**: 대시보드에서 직접 리포트 생성 가능

## 시스템 아키텍처

### 워크플로우

```
타겟 인프라 (AWS EC2/VPC)
    ↓
스캐너 실행 (Nmap, Nuclei)
    ↓
스캔 결과 정규화
    ↓
CVE 추출 및 매핑
    ↓
데이터베이스 저장 (PostgreSQL)
    ↓
PoC 격리 재현 (Docker)
    ↓
증거 수집 (strace, pcap, FS diff)
    ↓
신뢰도 점수화 (0-100)
    ↓
LLM 리포트 생성
    ↓
최종 리포트 (DOCX/PDF)
```

### 기술 스택

- **언어**: Python 3.11+
- **데이터베이스**: PostgreSQL 15
- **컨테이너**: Docker, Docker Compose
- **스캐너**: Nmap, Nuclei
- **대시보드**: Streamlit
- **LLM**: OpenAI API (GPT-4)
- **인프라**: AWS (EC2, VPC, S3), Terraform
- **ORM**: SQLAlchemy

## 프로젝트 구조

```
V2R/
├── src/                    # 소스 코드
│   ├── scanner/            # 스캐너 모듈 (Nmap, Nuclei, 취약점 체커)
│   ├── pipeline/           # 파이프라인 (스캔, PoC 재현)
│   ├── cce/                # CCE 점검 모듈
│   ├── database/           # 데이터베이스 (연결, 모델, Repository)
│   ├── dashboard/          # Streamlit 대시보드
│   ├── poc/                # PoC 재현 엔진 (격리, 재현, 증거 수집)
│   ├── utils/              # 공통 유틸리티 (ID 생성 등)
│   ├── llm/                 # LLM 리포트 생성
│   ├── report/              # 리포트 자동화
│   └── verification/        # 신뢰도 점수화
├── scripts/                 # 실행 스크립트
│   ├── cce_checks.sh       # CCE 점검 스크립트
│   ├── scan_cve_lab.ps1    # CVE-Lab 스캔 스크립트
│   └── test/               # 테스트 스크립트
├── infra/                   # 인프라 설정
│   ├── docker/             # Docker 설정
│   └── terraform/          # Terraform 설정
├── evidence/                # PoC 증적 파일
├── reports/                 # 생성된 리포트
└── docs/                    # 문서
```

상세한 구조는 `docs/PROJECT_STRUCTURE.md`를 참조하세요.

## 데이터베이스 스키마

### 주요 테이블

- **scan_results**: 스캔 결과 저장
- **poc_metadata**: PoC 메타데이터 (출처, 해시, 버전 등)
- **poc_reproductions**: PoC 재현 결과 (상태, 증거 경로, 신뢰도 점수)
- **cce_check_results**: CCE 점검 결과
- **events**: 탐지된 보안 이벤트
- **reports**: 생성된 리포트 메타데이터

## 주요 모듈 설명

### 스캐너 모듈 (`src/scanner/`)

- **NmapScanner**: 포트 및 서비스 스캔 수행
- **NucleiScanner**: 템플릿 기반 취약점 스캔 수행
- **VulnerabilityChecker**: 특정 취약점 체크 (Redis, MongoDB 무인증 등)
- **ScanResultNormalizer**: 다양한 스캐너 결과를 공통 형식으로 정규화

### 파이프라인 모듈 (`src/pipeline/`)

- **ScannerPipeline**: 스캔 실행 → 정규화 → DB 저장 파이프라인
- **POCPipeline**: PoC 재현 → 증거 수집 → DB 저장 파이프라인

### CCE 모듈 (`src/cce/`)

- **checker.py**: Docker 컨테이너 대상 CCE 점검 실행
- **generator.py**: JSON 기반 CCE 점검 항목에서 bash 스크립트 자동 생성

### PoC 재현 모듈 (`src/poc/`)

- **isolation.py**: Docker 기반 격리 환경 생성 및 관리
- **reproduction.py**: PoC 스크립트 실행 및 재현
- **evidence.py**: 시스템콜, 네트워크, 파일 시스템 증거 수집

### 신뢰도 점수화 (`src/verification/`)

- **reliability.py**: 출처 및 증거 기반 신뢰도 점수 계산 (0-100)

### LLM 모듈 (`src/llm/`)

- **report_generator.py**: OpenAI API를 활용한 Executive Summary 생성

### 리포트 모듈 (`src/report/`)

- **generator.py**: python-docx 기반 DOCX 리포트 생성
- **pr_template.py**: GitHub PR 템플릿 생성

## 실행 방법

### 빠른 시작

```bash
# 1. Docker 서비스 시작
docker-compose up -d

# 2. 데이터베이스 초기화
docker-compose exec app python scripts/utils/init_db.py

# 3. CVE-Lab 스캔 실행
.\scripts\scan_cve_lab.ps1  # PowerShell
# 또는
docker-compose exec app python scripts/test/scan_cve_lab_full.py

# 4. 대시보드 실행
docker-compose exec app streamlit run src/dashboard/app.py
# 브라우저에서 http://localhost:8501 접속
```

상세한 명령어는 `docs/QUICK_START.md`를 참조하세요.

## 환경 변수

`.env` 파일을 생성하여 다음 환경 변수를 설정할 수 있습니다:

```env
# 데이터베이스
DB_HOST=postgres
DB_PORT=5432
DB_NAME=v2r
DB_USER=v2r
DB_PASSWORD=v2r_password

# LLM (선택)
OPENAI_API_KEY=your_api_key_here
LLM_MODEL=gpt-4

# AWS (선택)
AWS_REGION=ap-northeast-2
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
S3_BUCKET_NAME=
```

## 주요 특징

### 1. 격리된 PoC 재현

- Docker 컨테이너 기반 완전 격리 환경
- 재현 실패 시 자동 롤백
- 증거 자동 수집 (시스템콜, 네트워크, 파일 시스템)

### 2. 신뢰도 기반 검증

- 출처 가중치 (Exploit-DB: 80, GitHub: 70 등)
- 증거 기반 점수 (시스템콜: 30, 네트워크: 20, FS diff: 20)
- 최종 신뢰도 점수 (0-100)

### 3. 자동화된 리포트 생성

- LLM 기반 Executive Summary 자동 생성
- python-docx 기반 기술본 자동 생성
- GitHub PR 템플릿 자동 생성

### 4. CCE 기반 점검

- 금융보안원 기준 Linux 서버 보안 설정 점검
- JSON 기반 점검 항목에서 bash 스크립트 자동 생성
- Docker 컨테이너 대상 자동 점검

## 구현 상태

### ✅ 구현 완료

- 스캐너 통합 (Nmap, Nuclei)
- 스캔 결과 정규화 및 DB 저장
- PoC 격리 재현 엔진
- 증거 수집 (strace, tcpdump, FS diff)
- 신뢰도 점수화
- LLM 리포트 생성
- 리포트 자동화 (DOCX)
- Streamlit 대시보드
- CCE 점검 자동화

### 🟡 선택적 기능

- ML 우선순위 모델 (XGBoost)
- GitHub PR 자동 생성 (API 연동)

## 기대 효과

1. **운영 효율성**: 보고서 초안 자동화로 문서 작성 시간 절감
2. **대응 속도 개선**: 우선순위 자동화로 패치 의사결정 시간 단축
3. **신뢰성 향상**: PoC 재현 및 증거 기반 검증으로 가짜 PoC 및 오탐 감소
4. **인재 역량 확보**: 펜테스팅, 클라우드, ML/LLM 실무 역량 강화

## 참고 문서

- **빠른 시작**: `docs/QUICK_START.md`
- **프로젝트 구조**: `docs/PROJECT_STRUCTURE.md`
- **PoC 목록**: `docs/POC_LIST.md`
- **변경 이력**: `CHANGELOG.md`

## 라이선스

프로젝트 라이선스는 `LICENSE` 파일을 참조하세요.

