# 취약한 Docker 환경 사용 가이드

## 개요

직접 만든 취약 웹앱 대신, 공식적으로 배포된 취약한 Docker 환경을 사용하면:
- **신뢰성**: 검증된 취약점 시나리오
- **표준화**: 업계 표준 테스트 환경
- **유지보수**: 커뮤니티에서 지속적으로 업데이트

## 추천 취약 환경

### DVWA (Damn Vulnerable Web Application) - 가장 추천

**특징:**
- 다양한 취약점 시나리오 (SQL Injection, XSS, CSRF 등)
- 난이도 조절 가능 (Low, Medium, High, Impossible)
- Nuclei 템플릿과 잘 매칭됨
- 업계 표준 실습 환경

**설치 및 실행:**

```bash
# 로컬 PC에서 실행 (docker-compose 사용 권장)
docker-compose --profile test up -d dvwa

# 또는 직접 실행
docker run -d \
  --name dvwa \
  -p 8080:80 \
  vulnerables/web-dvwa

# 접속 확인
curl http://localhost:8080

# 기본 계정
# ID: admin
# Password: password
```

**V2R 스캔 실행:**

```bash
# EC2 퍼블릭 IP 사용 (포트 8080)
docker-compose exec app python scripts/test/run_full_test.py --scan-target http://3.36.15.26:8080

# 또는 로컬에서 DVWA 컨테이너 이름 사용 (권장)
docker-compose exec app python scripts/test/run_full_test.py --scan-target http://dvwa:80
```

## 기타 추천 취약 환경

### 1. VulnHub (가장 추천)

**VulnHub**는 다양한 취약점을 포함한 가상머신/컨테이너 모음입니다.

#### Text4Shell (CVE-2022-42889) 테스트 환경

```bash
# 공식 Text4Shell 취약 환경 (예시)
docker run -d --name text4shell-vuln \
  -p 8080:8080 \
  ghcr.io/christophetd/log4shell-vulnerable-app:latest

# 또는 다른 Text4Shell 데모
docker run -d --name text4shell-vuln \
  -p 8080:8080 \
  vulhub/apache-log4j2:2.14.1
```

#### 기타 취약 환경

```bash
# Log4Shell (CVE-2021-44228)
docker run -d --name log4shell-vuln \
  -p 8080:8080 \
  ghcr.io/christophetd/log4shell-vulnerable-app:latest

# Spring4Shell (CVE-2022-22965)
docker run -d --name spring4shell-vuln \
  -p 8080:8080 \
  vulhub/spring:4.3.25

# 다양한 취약점 모음
docker run -d --name dvwa \
  -p 80:80 \
  vulnerables/web-dvwa
```

### 2. WebGoat

```bash
docker run -d --name webgoat \
  -p 8080:8080 \
  webgoat/webgoat:latest

# 접속: http://<EC2-IP>:8080/WebGoat
```

### 4. OWASP Juice Shop

```bash
docker run -d --name juice-shop \
  -p 3000:3000 \
  bkimminich/juice-shop

# 접속: http://<EC2-IP>:3000
```

## V2R 프로젝트에 통합

### docker-compose.yml에 추가

```yaml
services:
  # ... 기존 서비스들 ...
  
  # 취약한 웹앱 (테스트용)
  vulnerable-app:
    image: ghcr.io/christophetd/log4shell-vulnerable-app:latest
    container_name: text4shell-vuln
    ports:
      - "8080:8080"
    networks:
      - v2r-network
    # 개발/테스트 환경에서만 사용
    profiles:
      - test
```

### 실행 방법

```bash
# 취약 환경만 실행
docker-compose --profile test up -d vulnerable-app

# 전체 환경 실행 (취약 앱 포함)
docker-compose --profile test up -d

# 취약 환경 중지
docker-compose --profile test stop vulnerable-app
```

### V2R 워크플로우에서 사용

```bash
# Text4Shell 워크플로우 실행
docker-compose exec app python scripts/test/run_full_test.py \
  --text4shell-target <EC2-IP>

# 또는 로컬 취약 환경 사용
docker-compose exec app python scripts/test/run_full_test.py \
  --text4shell-target http://vulnerable-app:8080
```

## 추천 워크플로우

### 1. 공식 취약 환경 사용 (권장)

```bash
# 1. 취약 환경 실행
docker run -d --name text4shell-vuln \
  -p 8080:8080 \
  ghcr.io/christophetd/log4shell-vulnerable-app:latest

# 2. V2R 스캔 실행
docker-compose exec app python scripts/test/run_full_test.py \
  --text4shell-target <EC2-IP>

# 3. 결과 확인
docker-compose exec app python -c "
from src.database import get_db
from src.database.repository import ScanResultRepository
db = get_db()
with db.get_session() as session:
    repo = ScanResultRepository(session)
    scans = repo.get_recent(days=1, limit=10)
    for s in scans:
        print(f'{s.scanner_name}: {s.target_host} - {s.severity}')
"
```

### 2. 여러 취약 환경 동시 테스트

```bash
# 여러 취약 환경 실행
docker run -d --name vuln-1 -p 8080:8080 <image1>
docker run -d --name vuln-2 -p 8081:8080 <image2>
docker run -d --name vuln-3 -p 8082:8080 <image3>

# 각각에 대해 스캔 실행
for port in 8080 8081 8082; do
  docker-compose exec app python scripts/test/run_full_test.py \
    --text4shell-target http://<EC2-IP>:$port
done
```

## 주의사항

1. **보안**: 취약 환경은 **절대 프로덕션에 배포하지 마세요**
2. **네트워크 격리**: 가능하면 별도 네트워크에서 실행
3. **리소스**: 여러 취약 환경을 동시에 실행하면 리소스 사용량 증가

## 유용한 리소스

- **VulnHub**: https://www.vulnhub.com/
- **Docker Hub 취약 환경**: https://hub.docker.com/search?q=vulnerable
- **OWASP 취약 환경 목록**: https://owasp.org/www-project-vulnerable-web-applications-directory/
- **Awesome Vulnerable**: https://github.com/vulhub/vulhub

## 다음 단계

1. 공식 취약 환경으로 전환
2. 다양한 취약점 시나리오 테스트
3. Nuclei 템플릿과의 매칭 검증
4. 대시보드/리포트에 다양한 취약점 표시

