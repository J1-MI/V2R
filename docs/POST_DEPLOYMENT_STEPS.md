# 배포 후 다음 단계 가이드

## 배포 완료 후 체크리스트

### 1단계: 웹 서버 정보 확인

```bash
# Terraform 출력 확인
cd terraform
terraform output

# 웹 서버 IP 저장
WEB_SERVER_IP=$(terraform output -raw web_server_public_ip)
echo "웹 서버 IP: ${WEB_SERVER_IP}"
```

### 2단계: 웹 서버 준비 대기

```bash
# 웹 서버 초기화 완료 대기 (약 3-5분)
echo "웹 서버 초기화 대기 중..."
sleep 180

# 서비스 확인
echo "서비스 확인 중..."
```

### 3단계: 서비스 접속 확인

```bash
# Text4shell 확인
curl "http://${WEB_SERVER_IP}:8080/api/test" || echo "Text4shell 아직 준비 안됨"

# PHP 앱 확인
curl "http://${WEB_SERVER_IP}/dvwa" || echo "PHP 앱 아직 준비 안됨"

# MySQL 접속 확인
mysql -h ${WEB_SERVER_IP} -u dvwa -p'p@ssw0rd' -e "SHOW DATABASES;" || echo "MySQL 아직 준비 안됨"
```

### 4단계: V2R 프로젝트로 외부 스캐닝

```bash
# 프로젝트 루트로 이동
cd ..

# Docker 환경에서 외부 스캐닝 실행
docker-compose exec app python scripts/test/test_vulnerable_web_deployment.py \
  --target ${WEB_SERVER_IP}
```

**스캔 항목:**
- Nmap 포트 스캔 (22, 80, 443, 3306, 8080)
- Nuclei 취약점 스캔
- Text4shell 취약점 탐지
- MySQL 외부 노출 탐지
- SSH 포트 외부 노출 탐지

### 5단계: CCE 서버 점검 (내부자 관점)

```bash
# Docker 환경에서 CCE 점검 실행
docker-compose exec app python scripts/test/test_cce_checker.py \
  --host ${WEB_SERVER_IP} \
  --username root \
  --password v2r_test_password
```

**점검 항목:**
- CCE-LNX-001: SSH PasswordAuthentication 설정
- CCE-LNX-002: MySQL 외부 접근 설정
- CCE-LNX-003: 불필요 서비스 실행 여부
- CCE-LNX-004: 패키지 업데이트 상태
- CCE-LNX-005: 방화벽 상태

### 6단계: 대시보드에서 결과 확인

```bash
# 대시보드 실행
docker-compose exec app streamlit run src/dashboard/app.py \
  --server.port 8501 \
  --server.address 0.0.0.0
```

브라우저에서 접속:
- `http://your-ec2-ip:8501`

확인 항목:
- 취약점 리스트 (우선순위 포함)
- CCE 점검 결과
- PoC 재현 결과

## 전체 워크플로우 (한 번에 실행)

```bash
# 1. 웹 서버 IP 확인
cd terraform
WEB_SERVER_IP=$(terraform output -raw web_server_public_ip)
echo "웹 서버 IP: ${WEB_SERVER_IP}"

# 2. 웹 서버 준비 대기
echo "웹 서버 초기화 대기 중 (3분)..."
sleep 180

# 3. 프로젝트 루트로 이동
cd ..

# 4. 외부 스캐닝
echo "외부 스캐닝 실행 중..."
docker-compose exec app python scripts/test/test_vulnerable_web_deployment.py \
  --target ${WEB_SERVER_IP}

# 5. CCE 서버 점검
echo "CCE 서버 점검 실행 중..."
docker-compose exec app python scripts/test/test_cce_checker.py \
  --host ${WEB_SERVER_IP} \
  --username root \
  --password v2r_test_password

# 6. 대시보드 실행
echo "대시보드 실행 중..."
docker-compose exec app streamlit run src/dashboard/app.py \
  --server.port 8501 \
  --server.address 0.0.0.0
```

## 예상 결과

### 외부 스캐닝 결과
- 포트 22, 80, 443, 3306, 8080 열림
- Text4shell 취약점 탐지
- MySQL 외부 노출 탐지
- SSH 포트 외부 노출 탐지

### CCE 점검 결과
- SSH PasswordAuthentication → **취약** (yes)
- MySQL 외부 접근 → **취약** (bind-address = 0.0.0.0)
- 불필요 서비스 → 양호/취약
- 패키지 업데이트 → 주의/취약
- 방화벽 상태 → 취약 (비활성화 가능)

## 문제 해결

### 웹 서버 접속 불가

```bash
# 웹 서버에 SSH 접속하여 로그 확인
ssh root@${WEB_SERVER_IP}
# 비밀번호: v2r_test_password

# 로그 확인
tail -f /var/log/user-data.log
tail -f /var/log/text4shell-app.log

# 서비스 상태 확인
systemctl status text4shell
systemctl status mysql
systemctl status apache2
```

### Text4shell 앱이 시작되지 않는 경우

```bash
# 웹 서버에 SSH 접속
ssh root@${WEB_SERVER_IP}

# 수동 시작
cd /opt/text4shell-app
mvn compile exec:java -Dexec.mainClass="Text4ShellServer" > /var/log/text4shell.log 2>&1 &
```

### Docker 컨테이너 문제

```bash
# 컨테이너 재시작
docker-compose restart

# 로그 확인
docker-compose logs app
```

## 다음 단계

1. ✅ 취약 웹 서버 배포 완료
2. ⏳ 외부 스캐닝 실행
3. ⏳ CCE 서버 점검 실행
4. ⏳ 대시보드에서 결과 확인
5. ⏳ 리포트 생성 및 분석

