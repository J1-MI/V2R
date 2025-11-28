# 취약 웹 앱 배포 가이드

## 개요

이 가이드는 V2R 프로젝트 테스트를 위한 취약 웹 서버를 EC2에 배포하는 방법을 설명합니다.

## 배포된 취약점

### 1. Text4shell (CVE-2022-42889)
- **포트**: 8080
- **설명**: Apache Commons Text 1.9 취약 버전 사용
- **엔드포인트**:
  - `GET /api/interpolate?input=${script:javascript:...}`
  - `POST /api/process` (JSON body)
  - `GET /api/test` (테스트 페이지)

### 2. MySQL 외부 노출
- **포트**: 3306
- **설정**: `bind-address = 0.0.0.0`
- **계정**: `dvwa` / `p@ssw0rd`
- **데이터베이스**: `dvwa`, `testdb`

### 3. SSH 외부 노출 및 취약 설정
- **포트**: 22
- **설정**:
  - `PasswordAuthentication yes`
  - `PermitRootLogin yes`
  - root 비밀번호: `v2r_test_password` (테스트용)

### 4. Command Injection (PHP)
- **포트**: 80
- **경로**: `/dvwa/index.php?cmd=...`

### 5. SQL Injection (PHP)
- **포트**: 80
- **경로**: `/dvwa/index.php` (POST)

## Terraform 배포

### 1. 사전 준비

```bash
cd terraform

# AWS 자격 증명 설정
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=ap-northeast-2
```

### 2. Terraform 초기화

```bash
terraform init
```

### 3. 배포 실행

```bash
terraform apply
```

### 4. 출력 확인

```bash
terraform output
```

다음 정보를 확인하세요:
- `web_server_public_ip`: 웹 서버 공인 IP
- `web_server_private_ip`: 웹 서버 사설 IP
- `scanner_public_ip`: 스캐너 서버 공인 IP

## 배포 확인

### 1. Text4shell 확인

```bash
# 웹 서버 IP 확인
WEB_SERVER_IP=$(terraform output -raw web_server_public_ip)

# Text4shell 테스트 페이지 접속
curl "http://${WEB_SERVER_IP}:8080/api/test"

# 취약점 테스트
curl "http://${WEB_SERVER_IP}:8080/api/interpolate?input=\${script:javascript:java.lang.Runtime.getRuntime().exec('id')}"
```

### 2. MySQL 외부 접근 확인

```bash
# MySQL 접속 테스트
mysql -h ${WEB_SERVER_IP} -u dvwa -p'p@ssw0rd' -e "SHOW DATABASES;"
```

### 3. SSH 접속 확인

```bash
# SSH 접속 테스트
ssh -o StrictHostKeyChecking=no root@${WEB_SERVER_IP}
# 비밀번호: v2r_test_password
```

### 4. PHP 취약점 확인

```bash
# Command Injection 테스트
curl "http://${WEB_SERVER_IP}/dvwa/index.php?cmd=id"

# SQL Injection 테스트
curl -X POST "http://${WEB_SERVER_IP}/dvwa/index.php" \
  -d "username=admin' OR '1'='1&password=test"
```

## V2R 프로젝트로 스캔

### 1. 외부 스캐닝 (외부자 관점)

```bash
# 스캐너 서버에서 실행
cd /path/to/V2R

# Nmap 스캔
python -c "
from src.pipeline.scanner_pipeline import ScannerPipeline
scanner = ScannerPipeline()
result = scanner.run_nmap_scan(
    target='${WEB_SERVER_IP}',
    ports='22,80,443,3306,8080',
    save_to_db=True
)
print(result)
"
```

### 2. CCE 서버 점검 (내부자 관점)

```bash
# 스캐너 서버에서 실행
python scripts/test/test_cce_checker.py \
  --host ${WEB_SERVER_IP} \
  --username root \
  --password v2r_test_password
```

**예상 결과:**
- CCE-LNX-001: SSH PasswordAuthentication → **취약** (yes)
- CCE-LNX-002: MySQL 외부 접근 → **취약** (bind-address = 0.0.0.0)
- CCE-LNX-003: 불필요 서비스 → 양호/취약
- CCE-LNX-004: 패키지 업데이트 → 주의/취약
- CCE-LNX-005: 방화벽 상태 → 취약 (비활성화 가능)

## 전체 테스트 워크플로우

### 1. 인프라 배포

```bash
cd terraform
terraform apply
```

### 2. 웹 서버 준비 대기

```bash
# 웹 서버 초기화 완료 대기 (약 2-3분)
sleep 180
```

### 3. 외부 스캐닝

```bash
# 스캐너 서버에서
python scripts/test/test_vulnerable_web_deployment.py \
  --target ${WEB_SERVER_IP}
```

### 4. CCE 서버 점검

```bash
# 스캐너 서버에서
python scripts/test/test_cce_checker.py \
  --host ${WEB_SERVER_IP} \
  --username root \
  --password v2r_test_password
```

### 5. 대시보드에서 확인

```bash
# 스캐너 서버에서
streamlit run src/dashboard/app.py --server.port 8501 --server.address 0.0.0.0
```

브라우저에서 접속:
- 취약점 리스트 확인
- CCE 점검 결과 확인
- 우선순위 확인

## 보안 주의사항

⚠️ **중요**: 이 설정은 **테스트 환경에서만** 사용하세요!

1. **SSH 비밀번호 인증**: 실제 환경에서는 키 기반 인증 사용
2. **MySQL 외부 노출**: 실제 환경에서는 VPC 내부에서만 접근 허용
3. **SSH 포트 외부 노출**: 실제 환경에서는 특정 IP만 허용
4. **root 비밀번호**: 테스트용으로만 사용, 실제 환경에서는 절대 사용 금지

## 리소스 정리

```bash
cd terraform
terraform destroy
```

## 문제 해결

### Text4shell 앱이 시작되지 않는 경우

```bash
# 웹 서버에 SSH 접속
ssh root@${WEB_SERVER_IP}

# 로그 확인
tail -f /var/log/text4shell-app.log
tail -f /var/log/text4shell-setup.log

# 수동 시작
cd /opt/text4shell-app
java -jar target/text4shell-vulnerable-1.0.0.jar
```

### MySQL 접속 실패

```bash
# MySQL 서비스 확인
systemctl status mysql

# MySQL 설정 확인
grep bind-address /etc/mysql/mysql.conf.d/mysqld.cnf

# MySQL 재시작
systemctl restart mysql
```

### SSH 접속 실패

```bash
# SSH 설정 확인
grep -E "PasswordAuthentication|PermitRootLogin" /etc/ssh/sshd_config

# SSH 재시작
systemctl restart sshd
```

## 참고

- Text4shell 앱은 Spring Boot로 실행되며, 시작에 시간이 걸릴 수 있습니다 (약 1-2분)
- 모든 서비스가 준비될 때까지 약 3-5분 정도 기다려주세요
- 로그는 `/var/log/user-data.log`에서 확인할 수 있습니다
