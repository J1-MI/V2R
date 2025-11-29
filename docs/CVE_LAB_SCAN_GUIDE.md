# CVE-Lab 스캔 가이드

## 개요

CVE-Lab의 4개 Docker 컨테이너(Jenkins, Elasticsearch, Redis, MongoDB)를 대상으로 통합 스캔을 수행합니다.

## 스캔 대상

### 1. Jenkins (포트 8081)
- **CVE**: CVE-2018-100861
- **스캔 방법**: 포트 스캔 + Nuclei (Critical/High 심각도)

### 2. Elasticsearch (포트 9200)
- **CVE**: CVE-2015-1427
- **스캔 방법**: 포트 스캔 + Nuclei (Critical/High 심각도)

### 3. Log4Shell (포트 8085)
- **CVE**: CVE-2021-44228
- **스캔 방법**: 포트 스캔 + Nuclei (Critical/High 심각도)

### 4. Redis (포트 6379)
- **취약점**: 무인증 접근, 무방비 노출
- **스캔 방법**: 포트 스캔 + 무인증 체크

### 5. MongoDB (포트 27017)
- **취약점**: 무인증 접근, 외부 바인딩
- **스캔 방법**: 포트 스캔 + 무인증 체크

## 사용 방법

### PowerShell에서 실행

```powershell
# 프로젝트 루트 디렉토리에서 실행
.\scripts\scan_cve_lab.ps1
```

### Docker 컨테이너 내부에서 직접 실행

```bash
# 통합 스캔 스크립트 실행
docker-compose exec app python scripts/test/scan_cve_lab_full.py

# 데이터베이스 초기화와 함께 실행
docker-compose exec app python scripts/test/scan_cve_lab_full.py --init-db
```

## 스캔 프로세스

### 1. HTTP 서비스 (Jenkins, Elasticsearch, Log4Shell)

1. **Nmap 포트 스캔**
   - 대상: `host.docker.internal:8081` (Jenkins), `host.docker.internal:9200` (Elasticsearch), `host.docker.internal:8085` (Log4Shell)
   - 스캔 타입: `-sV` (버전 감지)
   - 결과: DB에 저장

2. **Nuclei 취약점 스캔**
   - 대상: HTTP URL
   - 필터: Critical/High 심각도
   - 템플릿: CVE 템플릿 우선 사용
   - 결과: DB에 저장

### 2. 비HTTP 서비스 (Redis, MongoDB)

1. **Nmap 포트 스캔**
   - 대상: `host.docker.internal:6379` (Redis), `host.docker.internal:27017` (MongoDB)
   - 스캔 타입: `-sV` (버전 감지)
   - 결과: DB에 저장

2. **무인증 취약점 체크**
   - **Redis**: `redis-cli PING` 명령어로 인증 없이 접근 가능한지 확인
   - **MongoDB**: `pymongo`로 인증 없이 데이터베이스 목록 조회 시도
   - 결과: 취약점 발견 시 DB에 저장

## 스캔 결과 확인

### 대시보드에서 확인

```bash
docker-compose exec app streamlit run src/dashboard/app.py
```

대시보드에서 다음 정보를 확인할 수 있습니다:
- 최근 스캔 결과 목록
- 발견된 취약점 상세 정보
- CVE 정보
- 무인증 취약점 정보

### 데이터베이스에서 직접 확인

```bash
# PostgreSQL에 접속
docker-compose exec postgres psql -U v2r_user -d v2r

# 최근 스캔 결과 조회
SELECT scan_id, target_host, scanner_name, severity, scan_timestamp 
FROM scan_results 
ORDER BY scan_timestamp DESC 
LIMIT 10;
```

## 예상 결과

### Jenkins
- Nmap: 포트 8081 오픈, Jenkins 버전 정보
- Nuclei: CVE-2018-100861 관련 취약점 (템플릿이 있는 경우)

### Elasticsearch
- Nmap: 포트 9200 오픈, Elasticsearch 버전 정보
- Nuclei: CVE-2015-1427 관련 취약점 (템플릿이 있는 경우)

### Redis
- Nmap: 포트 6379 오픈, Redis 버전 정보
- 무인증 체크: **취약점 발견** (인증 없이 접근 가능)

### Log4Shell
- Nmap: 포트 8085 오픈, Spring Boot 애플리케이션 정보
- Nuclei: CVE-2021-44228 관련 취약점 (템플릿이 있는 경우)

### MongoDB
- Nmap: 포트 27017 오픈, MongoDB 버전 정보
- 무인증 체크: **취약점 발견** (인증 없이 접근 가능)

## 문제 해결

### Redis/MongoDB 무인증 체크 실패

**증상**: `redis-cli: command not found` 또는 `pymongo not found`

**해결 방법**:
1. Dockerfile.dev에 `redis-tools` 패키지 추가 확인
2. `requirements.txt`에 `pymongo>=4.0.0` 추가 확인
3. Docker 이미지 재빌드:
   ```bash
   docker-compose build --no-cache app
   ```

### Nuclei 템플릿을 찾을 수 없음

**증상**: `Nuclei templates not found`

**해결 방법**:
1. 템플릿 경로 확인:
   ```bash
   docker-compose exec app ls -la /usr/local/bin/nuclei-templates
   ```
2. 템플릿이 없으면 Dockerfile.dev에서 템플릿 설치 확인

### 포트에 연결할 수 없음

**증상**: `Connection refused` 또는 `Connection timeout`

**해결 방법**:
1. CVE-Lab 컨테이너가 실행 중인지 확인:
   ```bash
   docker ps | grep cve-lab
   ```
2. 포트 매핑 확인:
   ```bash
   docker ps --format "table {{.Names}}\t{{.Ports}}" | grep cve-lab
   ```
3. `host.docker.internal`이 올바르게 설정되어 있는지 확인

## 참고 사항

- EPSS 기반 스캔은 현재 Nuclei의 severity 필터(Critical/High)를 사용합니다.
- 실제 EPSS 점수 기반 필터링은 추후 구현 예정입니다.
- 무인증 취약점은 자동으로 DB에 저장되며, 대시보드에서 확인할 수 있습니다.
