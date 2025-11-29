#!/bin/bash
# EC2에서 로컬 PC의 V2R 서비스에 접속하는 스크립트

set -e

# 설정
LOCAL_PC_IP="${LOCAL_PC_IP:-}"
DB_PORT="${DB_PORT:-5432}"
API_PORT="${API_PORT:-8000}"
DASHBOARD_PORT="${DASHBOARD_PORT:-8501}"

if [ -z "$LOCAL_PC_IP" ]; then
    echo "❌ 오류: LOCAL_PC_IP 환경 변수가 설정되지 않았습니다."
    echo ""
    echo "사용법:"
    echo "  export LOCAL_PC_IP=<로컬PC-공인IP>"
    echo "  bash scripts/local/connect_from_ec2.sh"
    echo ""
    echo "또는:"
    echo "  LOCAL_PC_IP=<로컬PC-공인IP> bash scripts/local/connect_from_ec2.sh"
    exit 1
fi

echo "=========================================="
echo "로컬 PC V2R 서비스 연결 테스트"
echo "=========================================="
echo "로컬 PC IP: $LOCAL_PC_IP"
echo ""

# 연결 테스트
echo "🔌 연결 테스트 중..."

# PostgreSQL 연결 테스트
echo -n "  PostgreSQL ($LOCAL_PC_IP:$DB_PORT): "
if command -v nc &> /dev/null; then
    if nc -zv -w 5 "$LOCAL_PC_IP" "$DB_PORT" &>/dev/null; then
        echo "✅ 연결 가능"
    else
        echo "❌ 연결 실패 (방화벽 또는 서비스 미실행 확인 필요)"
    fi
elif timeout 5 bash -c "echo > /dev/tcp/$LOCAL_PC_IP/$DB_PORT" 2>/dev/null; then
    echo "✅ 연결 가능"
else
    echo "❌ 연결 실패 (방화벽 또는 서비스 미실행 확인 필요)"
    echo "    해결: 로컬 PC에서 'docker-compose ps'로 서비스 확인"
fi

# API 서버 연결 테스트
echo -n "  API 서버 (http://$LOCAL_PC_IP:$API_PORT): "
if command -v curl &> /dev/null; then
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "http://$LOCAL_PC_IP:$API_PORT" 2>/dev/null)
    if [ -n "$HTTP_CODE" ] && echo "$HTTP_CODE" | grep -qE "^[0-9]+$"; then
        echo "✅ 연결 가능 (HTTP $HTTP_CODE)"
    else
        echo "❌ 연결 실패 (방화벽 또는 서비스 미실행)"
        echo "    해결: 로컬 PC에서 'docker-compose ps' 및 방화벽 확인"
    fi
else
    echo "⚠️  curl이 설치되어 있지 않습니다"
    echo "    설치: sudo yum install curl -y (Amazon Linux) 또는 sudo apt-get install curl -y (Ubuntu)"
fi

# 대시보드 연결 테스트
echo -n "  대시보드 (http://$LOCAL_PC_IP:$DASHBOARD_PORT): "
if command -v curl &> /dev/null; then
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "http://$LOCAL_PC_IP:$DASHBOARD_PORT" 2>/dev/null)
    if [ -n "$HTTP_CODE" ] && echo "$HTTP_CODE" | grep -qE "^[0-9]+$"; then
        echo "✅ 연결 가능 (HTTP $HTTP_CODE)"
    else
        echo "❌ 연결 실패 (방화벽 또는 서비스 미실행)"
        echo "    해결: 로컬 PC에서 'docker-compose ps' 및 방화벽 확인"
    fi
else
    echo "⚠️  curl이 설치되어 있지 않습니다"
    echo "    설치: sudo yum install curl -y (Amazon Linux) 또는 sudo apt-get install curl -y (Ubuntu)"
fi

echo ""
echo "📝 환경 변수 설정:"
echo "  export DB_HOST=$LOCAL_PC_IP"
echo "  export DB_PORT=$DB_PORT"
echo ""
echo "테스트 실행:"
echo "  # Python3 사용 (EC2에 Python 설치 필요)"
echo "  python3 scripts/test/run_full_test.py --scan-target http://$LOCAL_PC_IP:80"
echo ""
echo "💡 Python 설치 방법:"
echo "  Amazon Linux: sudo yum install python3 python3-pip -y"
echo "  Ubuntu: sudo apt-get install python3 python3-pip -y"
echo ""
echo "🔧 연결 문제 해결:"
echo "  문서 참조: docs/EC2_CONNECTION_TROUBLESHOOTING.md"

