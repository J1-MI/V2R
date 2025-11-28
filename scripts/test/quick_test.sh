#!/bin/bash
# Docker 환경에서 빠른 테스트 실행 스크립트

set -e

echo "=========================================="
echo "V2R 빠른 테스트 실행"
echo "=========================================="
echo ""

# 컨테이너 확인
if ! docker-compose ps | grep -q "v2r-app.*Up"; then
    echo "❌ app 컨테이너가 실행 중이 아닙니다."
    echo "다음 명령어로 시작하세요: docker-compose up -d"
    exit 1
fi

echo "✓ Docker 컨테이너 확인 완료"
echo ""

# 테스트 실행
echo "[1/3] 데이터베이스 연결 확인"
docker-compose exec -T app python -c "
from src.database import get_db
db = get_db()
if db.test_connection():
    print('✓ 데이터베이스 연결 성공')
    exit(0)
else:
    print('✗ 데이터베이스 연결 실패')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ 데이터베이스 연결 실패"
    exit 1
fi

echo ""
echo "[2/3] 통합 테스트 실행"
docker-compose exec -T app python scripts/test/test_integration.py

if [ $? -eq 0 ]; then
    echo ""
    echo "[3/3] 테스트 완료"
    echo "=========================================="
    echo "✓ 모든 테스트 통과"
    echo ""
    echo "다음 단계:"
    echo "  1. 대시보드 실행: docker-compose exec app streamlit run src/dashboard/app.py --server.port 8501 --server.address 0.0.0.0"
    echo "  2. 브라우저에서 접속: http://localhost:8501"
    echo "=========================================="
else
    echo ""
    echo "❌ 테스트 실패"
    echo "로그 확인: docker-compose logs app"
    exit 1
fi

