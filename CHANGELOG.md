# V2R 변경 이력 (Changelog)

모든 중요 변경사항은 최신 항목이 위에 오도록 역순으로 정리합니다.

---

## 2025-01-XX (1주일 완성 계획 - 최종)

### EC2 배포 및 문서화
- **EC2 배포 가이드 작성**
  - 상세 배포 가이드 (`docs/DEPLOYMENT_EC2.md`)
  - 빠른 시작 가이드 (`QUICK_START_EC2.md`)
  - 자동 배포 스크립트 (Linux/Mac, Windows)
  - EC2 초기 설정 스크립트

- **프로젝트 진행률 분석**
  - 진행률 분석 문서 (`docs/PROGRESS_ANALYSIS.md`)
  - 최종 브리핑 문서 (`docs/FINAL_BRIEFING.md`)
  - 스모크 테스트 확장 (`scripts/test/smoke_test_extended.py`)

- **버그 수정**
  - 신뢰도 점수화 모듈 쿼리 오류 수정 (`src/verification/reliability.py`)

### 핵심 기능 구현 완료

- **PoC 격리 재현 엔진**
  - Docker 기반 격리 환경 구현 (`src/poc/isolation.py`)
  - PoC 재현 로직 구현 (`src/poc/reproduction.py`)
  - 증거 수집 모듈 구현 (`src/poc/evidence.py`)
  - strace, tcpdump, 파일 시스템 diff 수집 기능

- **PoC 신뢰도 점수화**
  - 신뢰도 점수화 모듈 구현 (`src/verification/reliability.py`)
  - 출처 가중치 기반 점수 계산
  - 증거 기반 점수 계산
  - 최종 신뢰도 점수 (0-100) 계산

- **LLM 리포트 생성**
  - OpenAI API 연동 (`src/llm/report_generator.py`)
  - Executive Summary 자동 생성
  - 취약점 요약 생성
  - 기본 RAG (증거 인용) 구현

- **리포트 자동화**
  - python-docx 기반 DOCX 리포트 생성 (`src/report/generator.py`)
  - GitHub PR 템플릿 생성 (`src/report/pr_template.py`)
  - 기술본 자동 생성 기능

- **Streamlit 대시보드**
  - 웹 대시보드 구현 (`src/dashboard/app.py`)
  - 취약점 리스트 화면
  - 신뢰도 점수 표시
  - 증거 다운로드 기능
  - 리포트 생성 버튼
  - 통계 차트

- **파이프라인 통합**
  - PoC 파이프라인 구현 (`src/pipeline/poc_pipeline.py`)
  - 전체 파이프라인 통합 테스트 스크립트 (`scripts/test/test_integration.py`)

- **의존성 추가**
  - docker>=6.1.0 추가 (requirements.txt)

### 문서 업데이트
- README 구현 상태 업데이트
- CHANGELOG 최신 변경사항 추가
- EC2 배포 가이드 추가
- 프로젝트 진행률 분석 문서 추가

## 2025-11-11
- **Terraform 구성 검증**
  - `terraform init`, `terraform validate` 실행으로 VPC/서브넷/보안그룹 설정 확인
  - S3 라이프사이클 규칙에 빈 프리픽스 필터 추가
  - 스캐너 `user_data` 템플릿의 `$${TIMESTAMP}` 이스케이프 처리
  - `.terraform.lock.hcl` 생성 및 프로바이더 버전 고정
- **문서 정리**
  - README에서 모집 관련 안내 제거
  - 진행 상황 및 최종 수정 일자 갱신
- **프로젝트 보드 업데이트**
  - Week 1 `Terraform VPC/서브넷/보안그룹 구성 테스트` 태스크 완료 처리

## 2025-11-01
- **프로젝트 구조 초기화**
  - 기본 디렉토리/파일 생성, `PROJECT_STRUCTURE.md` 추가
- **Terraform 인프라 코드**
  - VPC/서브넷/보안그룹 및 EC2, S3 리소스 정의
  - DVWA, Juice Shop 배포용 `user_data` 스크립트 작성
- **스캐너 모듈 구현**
  - Nmap, Nuclei 스캐너 및 정규화 모듈
- **데이터베이스 연결 및 ORM**
  - PostgreSQL 연결 모듈, SQLAlchemy 모델, Repository 패턴 구현
- **Docker 개발 환경**
  - 개발/프로덕션 Dockerfile, docker-compose, Makefile 구성
- **문서/의존성**
  - `SETUP.md`, `README_DOCKER.md`, `docs/DEPENDENCIES.md` 작성
- **스캐너 파이프라인 통합**
  - `ScannerPipeline` 클래스 및 통합 테스트 스크립트

## 2025-10-24 (초기 계획)
- EC2 취약 테스트 서버 배포 계획 수립 (의도적 취약 설정 포함)
- 네트워크/취약점 스캔 및 DAST 절차 정의
- CCE 기반 서버 점검 스크립트 초안 구상
- Ansible 플레이북을 통한 자동화 배포/수집 계획

--- 

이전에 기록되지 않은 변경 사항이 있다면 해당 날짜 섹션을 추가하거나 보완해 주세요.

