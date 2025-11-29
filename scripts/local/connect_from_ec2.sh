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
        echo "❌ 연결 실패"
    fi
elif command -v telnet &> /dev/null; then
    if timeout 5 bash -c "echo > /dev/tcp/$LOCAL_PC_IP/$DB_PORT" 2>/dev/null; then
        echo "✅ 연결 가능"
    else
        echo "❌ 연결 실패"
    fi
else
    echo "⚠️  테스트 도구 없음 (nc 또는 telnet 필요)"
fi

# API 서버 연결 테스트
echo -n "  API 서버 (http://$LOCAL_PC_IP:$API_PORT): "
if command -v curl &> /dev/null; then
    if curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "http://$LOCAL_PC_IP:$API_PORT" | grep -q "200\|404\|500"; then
        echo "✅ 연결 가능"
    else
        echo "❌ 연결 실패"
    fi
else
    echo "⚠️  curl이 설치되어 있지 않습니다"
fi

# 대시보드 연결 테스트
echo -n "  대시보드 (http://$LOCAL_PC_IP:$DASHBOARD_PORT): "
if command -v curl &> /dev/null; then
    if curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "http://$LOCAL_PC_IP:$DASHBOARD_PORT" | grep -q "200\|404\|500"; then
        echo "✅ 연결 가능"
    else
        echo "❌ 연결 실패"
    fi
else
    echo "⚠️  curl이 설치되어 있지 않습니다"
fi

echo ""
echo "📝 환경 변수 설정:"
echo "  export DB_HOST=$LOCAL_PC_IP"
echo "  export DB_PORT=$DB_PORT"
echo ""
echo "테스트 실행:"
echo "  python scripts/test/run_full_test.py --scan-target http://$LOCAL_PC_IP:80"

