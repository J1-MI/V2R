# 취약 환경 설정 가이드

## 추천 취약 환경

### 1. DVWA (Damn Vulnerable Web Application) - 가장 추천

**특징:**
- 다양한 취약점 시나리오 (SQL Injection, XSS, CSRF 등)
- 난이도 조절 가능 (Low, Medium, High, Impossible)
- Nuclei 템플릿과 잘 매칭됨
- 업계 표준 실습 환경

**설치 및 실행:**

```bash
# EC2에서 실행
docker run -d \
  --name dvwa \
  -p 80:80 \
  vulnerables/web-dvwa

# 접속 확인
curl http://localhost:80

# 기본 계정
# ID: admin
# Password: password
```

**V2R 스캔 실행:**

```bash
# EC2 퍼블릭 IP 사용
docker-compose exec app python scripts/test/run_full_test.py \
  --scan-target http://3.36.15.26:80
```

### 2. WebGoat

```bash
docker run -d \
  --name webgoat \
  -p 8080:8080 \
  webgoat/webgoat:latest

# 접속: http://<EC2-IP>:8080/WebGoat
```

### 3. OWASP Juice Shop

```bash
docker run -d \
  --name juice-shop \
  -p 3000:3000 \
  bkimminich/juice-shop

# 접속: http://<EC2-IP>:3000
```

### 4. VulnHub 컬렉션

```bash
# 다양한 취약 환경
docker pull vulnerables/web-dvwa
docker pull webgoat/webgoat
docker pull bkimminich/juice-shop
```

## docker-compose.yml 통합 (선택)

```yaml
services:
  # ... 기존 서비스들 ...
  
  # DVWA 취약 환경
  dvwa:
    image: vulnerables/web-dvwa:latest
    container_name: dvwa
    ports:
      - "80:80"
    networks:
      - v2r-network
    profiles:
      - test  # 테스트 환경에서만 실행

  # WebGoat
  webgoat:
    image: webgoat/webgoat:latest
    container_name: webgoat
    ports:
      - "8080:8080"
    networks:
      - v2r-network
    profiles:
      - test
```

**실행 방법:**

```bash
# 취약 환경만 실행
docker-compose --profile test up -d dvwa

# 전체 환경 실행
docker-compose --profile test up -d
```

## V2R 스캔 워크플로우

### 1. DVWA 스캔

```bash
# DVWA 실행 확인
curl http://localhost:80

# V2R 스캔 실행
docker-compose exec app python scripts/test/run_full_test.py \
  --scan-target http://3.36.15.26:80
```

### 2. 여러 취약 환경 동시 테스트

```bash
# 여러 환경 실행
docker run -d --name dvwa -p 80:80 vulnerables/web-dvwa
docker run -d --name webgoat -p 8080:8080 webgoat/webgoat
docker run -d --name juice-shop -p 3000:3000 bkimminich/juice-shop

# 각각 스캔
for port in 80 8080 3000; do
  docker-compose exec app python scripts/test/run_full_test.py \
    --scan-target http://3.36.15.26:$port
done
```

## 예상 결과

DVWA 같은 표준 취약 환경은:
- ✅ Nuclei 템플릿과 잘 매칭됨
- ✅ 다양한 취약점 탐지 (SQL Injection, XSS, CSRF 등)
- ✅ DB에 결과 저장 → 대시보드에서 확인 가능
- ✅ 리포트 생성 가능

## 다음 단계

1. DVWA 실행 및 스캔 테스트
2. 대시보드에서 결과 확인
3. 리포트 생성 및 검증
4. 필요시 다른 취약 환경 추가 테스트

