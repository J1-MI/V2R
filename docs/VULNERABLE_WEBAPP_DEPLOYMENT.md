# 취약 웹 애플리케이션 배포 및 테스트 가이드

## 모식도 요구사항 분석

### 1. 취약 웹 페이지 구성
- ✅ **기본 취약점**: Command Injection, SQL Injection (이미 구현됨)
- ⚠️ **Text4shell (CVE-2022-42889)**: 추가 구현 필요
- ✅ **MySQL 포트 외부 노출**: 이미 구현됨 (`terraform/user_data/web_server.sh`)
- ✅ **SSH 포트 외부 노출**: 이미 구현됨 (`terraform/vpc.tf`)

### 2. 외부 스캐닝
- ✅ **네트워크 스캔**: Nmap 구현됨
- ✅ **CVE 스캔**: Nuclei 구현됨
- ✅ **DAST 스캔**: Nuclei 웹 템플릿 사용 가능

### 3. CCE 서버 점검
- ❌ **전자금융기반시설 Linux 항목**: 미구현
- ❌ **XML/JSON 출력 형식**: 미구현
- ❌ **양호/취약 판정 로직**: 미구현

## 현재 구현 상태

### ✅ 이미 구현된 부분

1. **취약 웹 서버 배포** (`terraform/user_data/web_server.sh`)
   - Command Injection 취약점
   - SQL Injection 취약점
   - MySQL 외부 접근 허용 (포트 3306)
   - SSH 포트 외부 노출 (포트 22)
   - DVWA, Juice Shop 배포

2. **외부 스캐닝**
   - Nmap 포트/서비스 스캔
   - Nuclei 취약점 스캔
   - 스캔 결과 정규화 및 DB 저장

3. **PoC 재현 엔진**
   - Docker 격리 환경
   - 증거 수집 (strace, tcpdump, FS diff)

## 추가 구현 필요 사항

### 1. Text4shell (CVE-2022-42889) 취약 웹앱

**구현 방법:**
- Apache Commons Text 취약 버전 사용
- Java 웹 애플리케이션 (Spring Boot 또는 Tomcat)
- 취약한 문자열 보간 기능 포함

**예시 코드:**
```java
// 취약한 코드
StringSubstitutor substitutor = new StringSubstitutor();
String result = substitutor.replace("${script:javascript:java.lang.Runtime.getRuntime().exec('id')}");
```

### 2. CCE 서버 점검 모듈

**필요 기능:**
- 전자금융기반시설 2025년도 서버 Linux 항목 점검
- 각 항목에 대한 IF문 기반 양호/취약 판정
- XML/JSON 형식 출력

**구현 구조:**
```
src/compliance/
  ├── __init__.py
  ├── cce_checker.py      # CCE 항목 점검 로직
  ├── linux_checker.py    # Linux 서버 점검
  └── report_generator.py # XML/JSON 리포트 생성
```

**점검 항목 예시:**
- SSH PasswordAuthentication 설정
- MySQL 외부 접근 설정
- 불필요 서비스 실행 여부
- 패키지 업데이트 상태
- 방화벽 설정
- 로그 설정

## 구현 계획

### Phase 1: Text4shell 취약 웹앱 추가

1. **Java 웹 애플리케이션 생성**
   - Spring Boot 프로젝트
   - Apache Commons Text 1.9 (취약 버전) 의존성
   - 취약한 엔드포인트 구현

2. **Docker 컨테이너화**
   - Dockerfile 작성
   - `web_server.sh`에 배포 스크립트 추가

3. **테스트**
   - Text4shell PoC 실행
   - Nuclei 템플릿으로 탐지 확인

### Phase 2: CCE 서버 점검 모듈

1. **점검 항목 정의**
   - 전자금융기반시설 Linux 항목 리스트
   - 각 항목별 판정 로직 (IF문)

2. **점검 로직 구현**
   - SSH 접속하여 설정 파일 확인
   - 서비스 실행 상태 확인
   - 패키지 버전 확인

3. **리포트 생성**
   - XML 형식 출력
   - JSON 형식 출력
   - 양호/취약/주의 상태 포함

### Phase 3: 통합 테스트

1. **전체 워크플로우 테스트**
   - 취약 웹앱 배포
   - 외부 스캐닝 실행
   - CCE 서버 점검 실행
   - 결과 통합 및 리포트 생성

## 빠른 시작 (현재 상태에서)

### 1. 취약 웹 서버 배포

```bash
# Terraform으로 배포
cd terraform
terraform init
terraform plan
terraform apply

# 웹 서버 IP 확인
terraform output web_server_public_ip
```

### 2. 외부 스캐닝 실행

```bash
# EC2에서 실행
python -m src.pipeline.scanner_pipeline \
  --target <web_server_ip> \
  --scan-type nmap,nuclei
```

### 3. PoC 재현

```bash
# 스캔 결과 ID로 PoC 재현
python -m src.pipeline.poc_pipeline \
  --scan-result-id 1 \
  --target-host <web_server_ip>
```

## 다음 단계

1. **Text4shell 취약 웹앱 구현** (우선순위: 높음)
2. **CCE 서버 점검 모듈 구현** (우선순위: 중간)
3. **Ansible 연동** (우선순위: 낮음, 선택적)

