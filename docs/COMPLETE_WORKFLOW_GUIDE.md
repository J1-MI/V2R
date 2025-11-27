# 전체 워크플로우 가이드

## 개요

이 가이드는 모식도에 따라 취약 웹 서버 배포 → 외부 스캐닝 → PoC 재현 → CCE 서버 점검까지의 전체 워크플로우를 설명합니다.

## 전체 워크플로우

```
1. 취약 웹 서버 배포 (Terraform)
   ↓
2. 외부 스캐닝 (Nmap, Nuclei)
   ↓
3. PoC 재현 (target_host 자동 추출)
   ↓
4. CCE 서버 점검 (전자금융기반시설 Linux 항목)
   ↓
5. 리포트 생성 (XML/JSON)
```

## 단계별 실행 가이드

### 1단계: 취약 웹 서버 배포

```bash
# Terraform으로 배포
cd terraform
terraform init
terraform apply

# 웹 서버 IP 확인
WEB_SERVER_IP=$(terraform output -raw web_server_public_ip)
echo "웹 서버 IP: $WEB_SERVER_IP"
```

**배포되는 취약점:**
- Command Injection (PHP)
- SQL Injection (PHP)
- MySQL 포트 외부 노출 (3306)
- SSH 포트 외부 노출 (22)
- Text4shell (CVE-2022-42889) - 포트 8080

### 2단계: 외부 스캐닝

```bash
# 테스트 스크립트 사용
python scripts/test/test_vulnerable_web_deployment.py --target $WEB_SERVER_IP

# 또는 수동 실행
python -c "
from src.pipeline.scanner_pipeline import ScannerPipeline
scanner = ScannerPipeline()
result = scanner.run_nmap_scan(target='$WEB_SERVER_IP', ports='22,80,443,3306,8080')
print(result)
"
```

**스캔 항목:**
- 네트워크 스캔 (Nmap): 포트 22, 80, 443, 3306, 8080
- CVE 스캔 (Nuclei): 웹 애플리케이션 취약점
- DAST 스캔 (Nuclei): 동적 분석

### 3단계: PoC 재현

```bash
# 스캔 결과 ID 확인 후
python -c "
from src.pipeline.poc_pipeline import POCPipeline
poc = POCPipeline()

# target_host는 자동으로 스캔 결과에서 추출됨
result = poc.run_poc_reproduction(
    scan_result_id=1,  # 스캔 결과 ID
    poc_script='import sys; print(\"PoC test\")',
    poc_type='command_injection',
    cve_id='CWE-78'
)
print(result)
"
```

**자동 추출 기능:**
- `target_host`가 None이면 스캔 결과에서 자동으로 추출
- 스캔 결과 ID만 제공하면 자동으로 대상 호스트 설정

### 4단계: CCE 서버 점검

```bash
# CCE 서버 점검 실행
python scripts/test/test_cce_checker.py \
  --host $WEB_SERVER_IP \
  --username ubuntu \
  --key-file ~/.ssh/v2r-key.pem
```

**점검 항목:**
- CCE-LNX-001: SSH PasswordAuthentication 설정
- CCE-LNX-002: MySQL 외부 접근 설정
- CCE-LNX-003: 불필요 서비스 실행 여부
- CCE-LNX-004: 패키지 업데이트 상태
- CCE-LNX-005: 방화벽 상태

**출력 형식:**
- XML: `reports/cce_report_*.xml`
- JSON: `reports/cce_report_*.json`

### 5단계: 리포트 생성

```bash
# 대시보드에서 리포트 생성
streamlit run src/dashboard/app.py

# 또는 Python에서 직접
python -c "
from src.report.generator import ReportGenerator
generator = ReportGenerator()
result = generator.generate_report(
    report_id='full_report',
    scan_results=[...],
    poc_reproductions=[...]
)
print(f'리포트 생성: {result[\"file_path\"]}')
"
```

## 통합 테스트 스크립트

전체 워크플로우를 한 번에 실행:

```bash
#!/bin/bash
# 전체 워크플로우 실행 스크립트

# 1. 웹 서버 배포 (Terraform)
cd terraform
terraform apply -auto-approve
WEB_SERVER_IP=$(terraform output -raw web_server_public_ip)
cd ..

# 2. 웹 서버 준비 대기
echo "웹 서버 준비 대기 중..."
sleep 120

# 3. 외부 스캐닝
echo "외부 스캐닝 실행..."
python scripts/test/test_vulnerable_web_deployment.py --target $WEB_SERVER_IP

# 4. CCE 서버 점검
echo "CCE 서버 점검 실행..."
python scripts/test/test_cce_checker.py \
  --host $WEB_SERVER_IP \
  --username ubuntu \
  --key-file terraform/keys/v2r-key.pem

echo "전체 워크플로우 완료!"
```

## 확인 사항

### 웹 서버 접속 확인

```bash
# HTTP
curl http://$WEB_SERVER_IP/dvwa

# Text4shell
curl "http://$WEB_SERVER_IP:8080/api/test"

# MySQL
mysql -h $WEB_SERVER_IP -u dvwa -p'p@ssw0rd' -e "SHOW DATABASES;"
```

### 취약점 확인

#### Command Injection
```bash
curl "http://$WEB_SERVER_IP/dvwa/index.php?cmd=id"
```

#### Text4shell (CVE-2022-42889)
```bash
curl "http://$WEB_SERVER_IP:8080/api/interpolate?input=\${script:javascript:java.lang.Runtime.getRuntime().exec('id')}"
```

## 대시보드에서 확인

```bash
streamlit run src/dashboard/app.py
```

대시보드에서:
- 취약점 리스트 확인
- PoC 재현 결과 확인
- CCE 점검 결과 확인 (향후 통합 예정)
- 리포트 생성

## 정리

### 리소스 삭제

```bash
cd terraform
terraform destroy -auto-approve
```

## 구현 완료 사항

### ✅ 완료된 기능

1. **target_host 자동 추출**
   - `poc_pipeline.py`에서 스캔 결과 ID로부터 자동 추출
   - None 처리 개선

2. **취약 웹 서버 배포**
   - Terraform으로 자동 배포
   - Command Injection, SQL Injection 포함
   - MySQL, SSH 포트 외부 노출

3. **Text4shell 취약 웹앱**
   - Java 기반 취약 애플리케이션
   - Apache Commons Text 1.9 (취약 버전)
   - 포트 8080에서 실행

4. **CCE 서버 점검 모듈**
   - 전자금융기반시설 Linux 항목 점검
   - XML/JSON 형식 출력
   - 양호/취약/주의 판정

### 📝 향후 개선 사항

1. CCE 점검 결과를 대시보드에 통합
2. Ansible 연동 (선택적)
3. 추가 CCE 항목 확장

