# V2R 변경 이력 (Changelog)

모든 중요 변경사항은 최신 항목이 위에 오도록 역순으로 정리합니다.

---

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

