# V2R 프로젝트 Kanban 보드

## 보드 구조
```
[Backlog] → [This Week] → [In Progress] → [Blocked] → [Review] → [Done]
```

---

## Backlog

### Epic A: 인프라(테스트베드)
- [ ] AWS 계정 및 권한 설정
- [ ] Terraform 기본 구조 작성
- [ ] VPC/서브넷/보안그룹 구성
- [ ] EC2 인스턴스 생성 스크립트
- [ ] DVWA/Juice Shop 배포
- [ ] 취약 설정 적용 (MySQL/SSH 포트 공개 등)
- [ ] S3 증거 저장소 설정

### Epic B: 스캐너 통합 및 인게스천
- [ ] Nmap 통합 스크립트
- [ ] Nuclei 통합 및 템플릿 설정
- [ ] OpenVAS 연동 (선택)
- [ ] 스캔 결과 정규화 스키마 정의
- [ ] 공통 JSON 스키마 구현
- [ ] DB 저장 파이프라인

### Epic C: PoC 격리 재현 엔진 & 증거수집
- [ ] Docker 격리 환경 구축
- [ ] 스냅샷/롤백 메커니즘 구현
- [ ] strace 시스템콜 로그 수집
- [ ] tcpdump/tshark 네트워크 캡처
- [ ] 파일 시스템 diff 추적
- [ ] 증거 자동 저장 로직

### Epic D: PoC 진위 검증 & 신뢰도 점수화
- [ ] 정적 분석 로직 구현
- [ ] 동적 행동 매칭 알고리즘
- [ ] 출처 가중치 계산
- [ ] 신뢰도 점수화 모델 (0~100)
- [ ] 큐레이션 워크플로우

### Epic E: ML / LLM 연동
- [ ] 취약점 메타데이터 수집
- [ ] XGBoost 우선순위 모델 학습
- [ ] LLM API 연동 (OpenAI or local)
- [ ] RAG 구현 (증거 인용)
- [ ] Executive Summary 생성 프롬프트

### Epic F: 리포트 자동화 & 개발 연계
- [ ] python-docx 리포트 템플릿
- [ ] 기술본 자동 생성 로직
- [ ] 임원용 요약 생성
- [ ] GitHub API 연동
- [ ] PR/Issue 템플릿 자동 생성

### Epic G: 대시보드 / UI
- [ ] Streamlit 기본 구조
- [ ] 취약점 리스트 화면
- [ ] 신뢰도 표시
- [ ] 증거 다운로드 기능
- [ ] 리포트 생성 버튼
- [ ] PR 생성 버튼

### 인프라 / DevOps
- [ ] PostgreSQL DB 스키마 구현
- [ ] 환경 변수 설정
- [ ] Docker Compose 구성 (선택)
- [ ] CI/CD 파이프라인 (선택)

---

## This Week (Week 0)

### 목표
- 레포·Notion 초기화
- 개발 방법론 설정
- Kanban 보드 초기화
- 개발 환경 셋업 계획

### 태스크
- [x] README.md 개선 (1인 프로젝트 반영)
- [x] 개발 방법론 문서화
- [x] Kanban 보드 생성
- [x] 프로젝트 기본 구조 생성
- [x] .gitignore 생성
- [x] Terraform 기본 구조 작성
- [ ] 개발 환경 셋업 (AWS 계정, IDE, 도구 설치)

---

## In Progress

### Week 1 진행 중
- [x] 스캐너 모듈 기본 구조 구현
  - [x] Nmap 스캐너 클래스
  - [x] Nuclei 스캐너 클래스
  - [x] 결과 정규화 모듈
- [x] 데이터베이스 연결 모듈
- [ ] 환경 설정 문서화
- [ ] Terraform VPC/서브넷/보안그룹 구성 테스트
- [ ] EC2 인스턴스 생성 테스트
- [ ] SSH 키 생성 및 설정

---

## Blocked

*현재 차단된 작업이 없습니다.*

---

## Review

*검토 중인 작업이 없습니다.*

---

## Done

### Week 0 완료
- [x] README.md 수정 (오타, 역할분담 삭제, 1인 프로젝트 반영)
- [x] 개발 방법론 섹션 추가
- [x] PROJECT_KANBAN.md 생성
- [x] 프로젝트 기본 구조 생성
  - [x] .gitignore 생성
  - [x] requirements.txt 작성
  - [x] src/ 디렉토리 구조 생성
  - [x] 프로젝트 구조 문서 작성
- [x] Terraform 기본 구조 작성
  - [x] main.tf, variables.tf, outputs.tf
  - [x] vpc.tf (VPC/서브넷/보안그룹)
  - [x] ec2.tf (웹 서버, 스캐너 인스턴스)
  - [x] s3.tf (증거 저장소)
  - [x] user_data 스크립트 (web_server.sh, scanner.sh)
  - [x] Terraform README 작성
- [x] 데이터베이스 스키마 초안 작성 (schema.sql)
- [x] PoC 목록 문서 작성 (docs/POC_LIST.md)
- [x] 설정 관리 모듈 작성 (src/config.py)
- [x] 스캐너 모듈 구현
  - [x] Nmap 스캐너 (src/scanner/nmap_scanner.py)
  - [x] Nuclei 스캐너 (src/scanner/nuclei_scanner.py)
  - [x] 결과 정규화 모듈 (src/scanner/normalizer.py)
  - [x] 기본 스캐너 인터페이스 (src/scanner/base_scanner.py)
  - [x] 테스트 스크립트 (src/scanner/test_scanner.py)
- [x] 데이터베이스 연결 모듈
  - [x] 연결 관리 클래스 (src/database/connection.py)
  - [x] DB 초기화 스크립트 (scripts/utils/init_db.py)
- [x] 환경 설정 문서화
  - [x] .env.example 파일
  - [x] SETUP.md 가이드 문서
- [x] Docker 환경 마이그레이션
  - [x] Dockerfile (프로덕션)
  - [x] Dockerfile.dev (개발)
  - [x] docker-compose.yml (개발 환경)
  - [x] docker-compose.prod.yml (프로덕션)
  - [x] Makefile (편의 명령어)
  - [x] Docker 초기화 스크립트
  - [x] .dockerignore
  - [x] README_DOCKER.md 문서
- [x] 의존성 관리 및 문서화
  - [x] requirements.txt 패키지 확인 및 검증
  - [x] Dockerfile 패키지 설치 로직 개선
  - [x] 의존성 문서 작성 (docs/DEPENDENCIES.md)
  - [x] README 의존성 목록 추가
- [x] 데이터베이스 ORM 모델 구현
  - [x] SQLAlchemy 모델 정의 (src/database/models.py)
  - [x] ScanResult, POCMetadata, POCReproduction, Event, Report 모델
- [x] 데이터베이스 저장소 패턴
  - [x] Repository 패턴 구현 (src/database/repository.py)
  - [x] ScanResultRepository CRUD 및 통계
  - [x] POCMetadataRepository, POCReproductionRepository
- [x] 스캐너 파이프라인 통합
  - [x] ScannerPipeline 클래스 구현
  - [x] Nmap/Nuclei 스캔 파이프라인
  - [x] 전체 스캔 (Full Scan) 기능
  - [x] 통합 테스트 스크립트 (scripts/test/test_pipeline.py)

---

## 주간 회고 (Weekly Retrospective)

### Week 0 (예정)
- **완료된 작업:**
  - README 개선
  - 개발 방법론 수립
  - Kanban 보드 초기화
  
- **진행 중:**
  - 개발 환경 셋업
  
- **차단 사항:**
  - 없음
  
- **다음 주 계획:**
  - Week 1 목표에 맞춰 Epic A (인프라) 작업 시작

---

## 통계

### 속도 추적
- **Week 0:** - (초기화 단계)
- **Week 1:** - (예정)
- **Week 2:** - (예정)
- **Week 3:** - (예정)
- **Week 4:** - (예정)
- **Week 5:** - (예정)
- **Week 6:** - (예정)

### 차단 시간
- **평균 차단 시간:** - 
- **최장 차단 시간:** - 

---

## 참고사항

- 각 태스크는 2-4시간 단위로 세분화
- Must Have 우선, Nice to Have는 시간 여유 시 진행
- 차단 발생 시 즉시 문서화 및 대안 탐색
- 주간 회고는 매주 금요일 진행

