#!/bin/bash
# 취약 웹 서버 배포 후 테스트 스크립트

set -e

echo "=========================================="
echo "취약 웹 서버 테스트"
echo "=========================================="
echo ""

# 1. 웹 서버 IP 확인
cd terraform
WEB_SERVER_IP=$(terraform output -raw web_server_public_ip)
echo "웹 서버 IP: ${WEB_SERVER_IP}"
cd ..

# 2. 웹 서버 준비 대기
echo ""
echo "웹 서버 초기화 대기 중 (3분)..."
sleep 180

# 3. 서비스 확인
echo ""
echo "서비스 확인 중..."
echo "Text4shell: http://${WEB_SERVER_IP}:8080"
echo "PHP App: http://${WEB_SERVER_IP}/dvwa"
echo "MySQL: ${WEB_SERVER_IP}:3306"
echo "SSH: root@${WEB_SERVER_IP} (password: v2r_test_password)"

# 4. 외부 스캐닝
echo ""
echo "외부 스캐닝 실행 중..."
docker-compose exec app python scripts/test/test_vulnerable_web_deployment.py \
  --target ${WEB_SERVER_IP}

# 5. CCE 서버 점검
echo ""
echo "CCE 서버 점검 실행 중..."
docker-compose exec app python scripts/test/test_cce_checker.py \
  --host ${WEB_SERVER_IP} \
  --username root \
  --password v2r_test_password

echo ""
echo "=========================================="
echo "테스트 완료!"
echo "=========================================="
echo ""
echo "다음 단계:"
echo "  1. 대시보드 실행: docker-compose exec app streamlit run src/dashboard/app.py --server.port 8501 --server.address 0.0.0.0"
echo "  2. 브라우저에서 결과 확인: http://your-ec2-ip:8501"
echo ""

