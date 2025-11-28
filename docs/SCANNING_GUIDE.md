# 외부 스캐닝 가이드

## 빠른 시작

### 1. 웹 서버 IP 확인

```bash
cd terraform
terraform output web_server_public_ip
```

또는:

```bash
WEB_SERVER_IP=$(terraform output -raw web_server_public_ip)
echo "웹 서버 IP: ${WEB_SERVER_IP}"
```

### 2. 외부 스캐닝 실행

**올바른 명령어:**

```bash
# 방법 1: IP 주소 직접 입력 (권장)
docker-compose exec app python scripts/test/test_vulnerable_web_deployment.py \
  --target 13.125.220.26

# 방법 2: 변수 사용
WEB_SERVER_IP=$(terraform output -raw web_server_public_ip)
docker-compose exec app python scripts/test/test_vulnerable_web_deployment.py \
  --target ${WEB_SERVER_IP}

# 방법 3: http:// 접두사 포함 (자동으로 제거됨)
docker-compose exec app python scripts/test/test_vulnerable_web_deployment.py \
  --target http://13.125.220.26
```

## 주의사항

### ❌ 잘못된 사용법

```bash
# $ 기호 포함 (잘못됨)
--target $13.125.220.26

# 백슬래시로 줄바꿈 (잘못됨)
docker-compose exec app python scripts/test/test_vulnerable_web_deployment.py \
 --target $13.125.220.26
```

### ✅ 올바른 사용법

```bash
# IP 주소만 입력
--target 13.125.220.26

# 변수 사용 시 따옴표 없이
WEB_SERVER_IP=13.125.220.26
--target ${WEB_SERVER_IP}
```

## 스캔 항목

### Nmap 스캔
- 포트: 22 (SSH), 80 (HTTP), 443 (HTTPS), 3306 (MySQL)
- 서비스 버전 탐지
- 열린 포트 확인

### Nuclei 스캔
- HTTP/HTTPS 취약점 탐지
- Text4shell (CVE-2022-42889) 탐지
- 기타 알려진 취약점 탐지

## 예상 결과

### 성공 시
```
[1/4] 데이터베이스 초기화
✓ 데이터베이스 연결 성공

[2/4] 취약점 스캔 실행
  - Nmap 스캔 실행: 13.125.220.26
  ✓ Nmap 스캔 완료: nmap_13.125.220.26_20251127_...
  - Nuclei 스캔 실행: 13.125.220.26
  ✓ Nuclei 스캔 완료: nuclei_13.125.220.26_20251127_...
  ✓ 스캔 결과 저장됨 (ID: 1, Target: 13.125.220.26)

[3/4] PoC 재현 테스트
  ✓ PoC 재현 완료: poc_20251127_...

[4/4] 테스트 결과 요약
✓ 데이터베이스 연결: 성공
✓ 스캔 실행: 성공 (ID: 1)
✓ PoC 재현: 성공
```

### 실패 시

**IP 주소 형식 오류:**
```
잘못된 대상 주소 형식: $13.125.220.26
올바른 형식: IP 주소 (예: 13.125.220.26) 또는 도메인 (예: example.com)
```

**연결 실패:**
```
✗ Nmap 스캔 실패: Connection refused
```

해결 방법:
1. 웹 서버가 완전히 초기화되었는지 확인 (3-5분 대기)
2. Security Group에서 포트가 열려있는지 확인
3. 웹 서버에 직접 접속 가능한지 확인

## 문제 해결

### 1. IP 주소 확인

```bash
# Terraform 출력 확인
cd terraform
terraform output

# 또는 AWS 콘솔에서 확인
aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=v2r-test-web-server" \
  --query "Reservations[*].Instances[*].PublicIpAddress" \
  --output text
```

### 2. 웹 서버 준비 확인

```bash
# 웹 서버에 직접 접속 테스트
curl http://13.125.220.26/dvwa
curl http://13.125.220.26:8080/api/test

# MySQL 접속 테스트
mysql -h 13.125.220.26 -u dvwa -p'p@ssw0rd' -e "SHOW DATABASES;"
```

### 3. Docker 컨테이너 확인

```bash
# 컨테이너 실행 중인지 확인
docker-compose ps

# 컨테이너 로그 확인
docker-compose logs app

# 컨테이너 재시작
docker-compose restart app
```

## 다음 단계

스캔 완료 후:

1. **대시보드에서 결과 확인**
   ```bash
   docker-compose exec app streamlit run src/dashboard/app.py \
     --server.port 8501 \
     --server.address 0.0.0.0
   ```

2. **CCE 서버 점검 실행**
   ```bash
   docker-compose exec app python scripts/test/test_cce_checker.py \
     --host 13.125.220.26 \
     --username root \
     --password v2r_test_password
   ```

3. **리포트 생성**
   - 대시보드에서 리포트 생성 버튼 클릭
   - 또는 스크립트로 직접 생성

