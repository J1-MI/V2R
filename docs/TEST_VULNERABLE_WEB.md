# 취약 웹 서버 배포 및 테스트 가이드

## 개요

이 가이드는 Terraform을 사용하여 취약 웹 서버를 배포하고, V2R 시스템으로 스캔 및 PoC 재현을 테스트하는 방법을 설명합니다.

## 사전 준비

### 1. AWS 자격 증명 설정

```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=ap-northeast-2
```

### 2. SSH 키 생성 (없는 경우)

```bash
cd terraform/keys
ssh-keygen -t rsa -b 4096 -f v2r-key -N ""
```

## 배포 단계

### 1. Terraform 초기화

```bash
cd terraform
terraform init
```

### 2. 변수 설정 (선택)

`terraform/variables.tf`에서 기본값을 확인하거나 `terraform.tfvars` 파일 생성:

```hcl
project_name = "v2r"
environment = "test"
instance_type = "t3.micro"
allowed_ssh_cidr = "0.0.0.0/0"  # 테스트용 (프로덕션에서는 제한)
```

### 3. 배포 계획 확인

```bash
terraform plan
```

### 4. 배포 실행

```bash
terraform apply
```

배포 완료 후 출력:
```
web_server_public_ip = "x.x.x.x"
scanner_public_ip = "y.y.y.y"
```

### 5. 웹 서버 준비 대기 (약 5-10분)

```bash
# 웹 서버가 준비될 때까지 대기
WEB_SERVER_IP=$(terraform output -raw web_server_public_ip)
while ! curl -s http://$WEB_SERVER_IP/dvwa > /dev/null; do
    echo "웹 서버 준비 중..."
    sleep 10
done
echo "웹 서버 준비 완료!"
```

## 테스트 실행

### 방법 1: 테스트 스크립트 사용 (권장)

```bash
# EC2 스캐너 서버 또는 로컬에서 실행
cd /path/to/V2R
python scripts/test/test_vulnerable_web_deployment.py --target <web_server_ip>
```

### 방법 2: 수동 테스트

#### 1. 스캔 실행

```bash
# Python 인터프리터에서
from src.pipeline.scanner_pipeline import ScannerPipeline

scanner = ScannerPipeline()
result = scanner.run_nmap_scan(
    target="<web_server_ip>",
    ports="22,80,443,3306",
    scan_type="-sV"
)
print(result)
```

#### 2. PoC 재현

```bash
# 스캔 결과 ID 확인 후
from src.pipeline.poc_pipeline import POCPipeline

poc = POCPipeline()
result = poc.run_poc_reproduction(
    scan_result_id=1,  # 스캔 결과 ID
    poc_script="...",  # PoC 스크립트
    poc_type="command_injection"
)
```

## 확인 사항

### 1. 웹 서버 접속 확인

```bash
# HTTP 접속
curl http://<web_server_ip>/dvwa

# MySQL 포트 확인
nmap -p 3306 <web_server_ip>

# SSH 포트 확인
nmap -p 22 <web_server_ip>
```

### 2. 취약점 확인

#### Command Injection
```bash
curl "http://<web_server_ip>/dvwa/index.php?cmd=id"
```

#### SQL Injection
```bash
curl -X POST "http://<web_server_ip>/dvwa/index.php" \
  -d "username=admin' OR '1'='1&password=test"
```

#### MySQL 외부 접근
```bash
mysql -h <web_server_ip> -u dvwa -p'p@ssw0rd' -e "SHOW DATABASES;"
```

## 대시보드에서 확인

```bash
# 대시보드 실행
streamlit run src/dashboard/app.py

# 브라우저에서 접속
# http://localhost:8501
```

대시보드에서:
- 취약점 리스트 확인
- PoC 재현 결과 확인
- 리포트 생성

## 정리

### 리소스 삭제

```bash
cd terraform
terraform destroy
```

**주의**: 모든 리소스가 삭제되므로 데이터 백업 필요

## 문제 해결

### 웹 서버 접속 불가

1. 보안 그룹 확인
   ```bash
   aws ec2 describe-security-groups --group-ids <sg-id>
   ```

2. 인스턴스 상태 확인
   ```bash
   aws ec2 describe-instances --instance-ids <instance-id>
   ```

### 스캔 실패

1. 네트워크 연결 확인
   ```bash
   ping <web_server_ip>
   ```

2. 포트 확인
   ```bash
   nmap -p 80,443,3306 <web_server_ip>
   ```

### PoC 재현 실패

1. Docker 확인
   ```bash
   docker ps
   ```

2. 로그 확인
   ```bash
   docker logs <container_id>
   ```

## 다음 단계

1. Text4shell 취약 웹앱 추가
2. CCE 서버 점검 모듈 구현
3. 전체 워크플로우 통합 테스트

