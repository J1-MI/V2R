# 취약 웹 앱 배포 단계별 가이드

## 전체 흐름

```
1. 로컬에서 변경사항 커밋 & 푸시
   ↓
2. EC2 서버에서 git pull
   ↓
3. Terraform으로 취약 웹 서버 배포
   ↓
4. V2R 프로젝트로 스캔 및 점검
```

---

## 1단계: 로컬에서 커밋 & 푸시

### 변경사항 확인
```bash
git status
git diff
```

### 커밋 & 푸시
```bash
git add .
git commit -m "취약 웹 앱 구성 추가 (Text4shell, MySQL/SSH 외부 노출, SSH 취약 설정)"
git push origin main
```

---

## 2단계: EC2 서버에서 git pull

### EC2 서버 접속
```bash
ssh -i your-key.pem ec2-user@your-ec2-ip
# 또는
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### 프로젝트 디렉토리로 이동 및 pull
```bash
cd V2R
git pull origin main
```

---

## 3단계: Terraform으로 취약 웹 서버 배포

### Terraform 디렉토리로 이동
```bash
cd terraform
```

### AWS 자격 증명 설정 (필요시)
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=ap-northeast-2
```

### Terraform 초기화 및 배포
```bash
# 초기화
terraform init

# 배포 실행
terraform apply
# 확인 메시지에 'yes' 입력
```

### 웹 서버 IP 확인
```bash
terraform output web_server_public_ip
# 또는
terraform output -raw web_server_public_ip
```

### 웹 서버 준비 대기
```bash
# 약 3-5분 대기 (서비스 초기화 시간)
echo "웹 서버 초기화 대기 중..."
sleep 180
```

---

## 4단계: V2R 프로젝트로 스캔 및 점검

### 웹 서버 IP 변수 설정
```bash
WEB_SERVER_IP=$(terraform output -raw web_server_public_ip)
echo "웹 서버 IP: ${WEB_SERVER_IP}"
```

### 서비스 확인 (선택)
```bash
# Text4shell 확인
curl "http://${WEB_SERVER_IP}:8080/api/test"

# MySQL 접속 확인
mysql -h ${WEB_SERVER_IP} -u dvwa -p'p@ssw0rd' -e "SHOW DATABASES;"
```

### 외부 스캐닝 (외부자 관점)
```bash
# 프로젝트 루트로 이동
cd ..

# Docker 환경에서 실행 (또는 로컬에서)
docker-compose exec app python scripts/test/test_vulnerable_web_deployment.py \
  --target ${WEB_SERVER_IP}

# 또는 컨테이너 내부에서
docker-compose exec app bash
python scripts/test/test_vulnerable_web_deployment.py --target ${WEB_SERVER_IP}
```

### CCE 서버 점검 (내부자 관점)
```bash
# Docker 환경에서 실행
docker-compose exec app python scripts/test/test_cce_checker.py \
  --host ${WEB_SERVER_IP} \
  --username root \
  --password v2r_test_password

# 또는 컨테이너 내부에서
docker-compose exec app bash
python scripts/test/test_cce_checker.py \
  --host ${WEB_SERVER_IP} \
  --username root \
  --password v2r_test_password
```

---

## 5단계: 대시보드에서 결과 확인

### 대시보드 실행
```bash
# Docker 환경에서
docker-compose exec app streamlit run src/dashboard/app.py \
  --server.port 8501 \
  --server.address 0.0.0.0

# 또는 컨테이너 내부에서
docker-compose exec app bash
streamlit run src/dashboard/app.py --server.port 8501 --server.address 0.0.0.0
```

### 브라우저에서 접속
```
http://your-ec2-ip:8501
```

확인 항목:
- 취약점 리스트 (우선순위 포함)
- CCE 점검 결과
- PoC 재현 결과

---

## 빠른 참조 명령어

### 전체 워크플로우 (한 번에)
```bash
# 1. git pull
cd V2R && git pull origin main

# 2. Terraform 배포
cd terraform
terraform init
terraform apply -auto-approve
WEB_SERVER_IP=$(terraform output -raw web_server_public_ip)
echo "웹 서버 IP: ${WEB_SERVER_IP}"

# 3. 대기
sleep 180

# 4. 외부 스캐닝
cd ..
docker-compose exec app python scripts/test/test_vulnerable_web_deployment.py \
  --target ${WEB_SERVER_IP}

# 5. CCE 점검
docker-compose exec app python scripts/test/test_cce_checker.py \
  --host ${WEB_SERVER_IP} \
  --username root \
  --password v2r_test_password
```

---

## 문제 해결

### Terraform 오류
```bash
# 상태 확인
terraform plan

# 상태 초기화 (필요시)
terraform init -upgrade
```

### 웹 서버 접속 불가
```bash
# 웹 서버에 SSH 접속하여 로그 확인
ssh -i your-key.pem root@${WEB_SERVER_IP}
# 비밀번호: v2r_test_password

# 로그 확인
tail -f /var/log/user-data.log
tail -f /var/log/text4shell-app.log

# 서비스 상태 확인
systemctl status text4shell
systemctl status mysql
systemctl status apache2
```

### Docker 컨테이너 문제
```bash
# 컨테이너 재시작
docker-compose restart

# 로그 확인
docker-compose logs app
```

---

## 리소스 정리 (테스트 완료 후)

```bash
cd terraform
terraform destroy
```

---

## 체크리스트

- [ ] 로컬에서 git commit & push 완료
- [ ] EC2 서버에서 git pull 완료
- [ ] Terraform 배포 완료
- [ ] 웹 서버 IP 확인
- [ ] 웹 서버 초기화 대기 (3-5분)
- [ ] 외부 스캐닝 실행
- [ ] CCE 서버 점검 실행
- [ ] 대시보드에서 결과 확인

