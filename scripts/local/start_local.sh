#!/bin/bash
# 로컬 PC에서 V2R Docker 서비스 시작 스크립트

set -e

echo "=========================================="
echo "V2R 로컬 Docker 서비스 시작"
echo "=========================================="

# 현재 디렉토리 확인
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ 오류: docker-compose.yml 파일을 찾을 수 없습니다."
    echo "프로젝트 루트 디렉토리에서 실행해주세요."
    exit 1
fi

# Docker 실행 확인
if ! command -v docker &> /dev/null; then
    echo "❌ 오류: Docker가 설치되어 있지 않습니다."
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ 오류: docker-compose가 설치되어 있지 않습니다."
    exit 1
fi

# 서비스 시작
echo ""
echo "📦 Docker 서비스 시작 중..."
docker-compose up -d

# 서비스 상태 확인
echo ""
echo "⏳ 서비스 시작 대기 중 (10초)..."
sleep 10

# 상태 확인
echo ""
echo "📊 서비스 상태:"
docker-compose ps

# 포트 확인
echo ""
echo "🔌 열린 포트:"
echo "  - PostgreSQL: 5432"
echo "  - API 서버: 8000"
echo "  - 대시보드: 8501"
echo "  - DVWA (테스트): 80 (--profile test 사용 시)"

# 공인 IP 확인 (선택사항)
echo ""
echo "🌐 공인 IP 확인 (EC2 접속용):"
if command -v curl &> /dev/null; then
    PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ipinfo.io/ip 2>/dev/null || echo "확인 불가")
    echo "  공인 IP: $PUBLIC_IP"
    echo ""
    echo "EC2에서 접속 시 다음 IP를 사용하세요:"
    echo "  DB: $PUBLIC_IP:5432"
    echo "  API: http://$PUBLIC_IP:8000"
    echo "  대시보드: http://$PUBLIC_IP:8501"
else
    echo "  curl이 설치되어 있지 않아 IP를 확인할 수 없습니다."
fi

echo ""
echo "✅ 서비스 시작 완료!"
echo ""
echo "다음 명령어로 로그 확인:"
echo "  docker-compose logs -f app"
echo ""
echo "취약 환경 포함 실행:"
echo "  docker-compose --profile test up -d"

