#!/bin/bash
# Bash 스크립트: Docker 환경에서 테스트 실행

echo "=========================================="
echo "V2R 통합 테스트 실행"
echo "=========================================="
echo ""

# Docker Compose 상태 확인
echo "[1/4] Docker 컨테이너 상태 확인..."
docker-compose ps
echo ""

# 컨테이너가 실행 중이 아니면 시작
if ! docker-compose ps | grep -q "Up"; then
    echo "[2/4] Docker 컨테이너 시작 중..."
    docker-compose up -d
    sleep 5
else
    echo "[2/4] Docker 컨테이너가 이미 실행 중입니다."
fi
echo ""

# 데이터베이스 연결 확인
echo "[3/4] 데이터베이스 연결 확인..."
docker-compose exec -T app python -c "from src.database import get_db; db = get_db(); print('✓ 연결 성공' if db.test_connection() else '✗ 연결 실패')"
echo ""

# 통합 테스트 실행
echo "[4/4] 통합 테스트 실행..."
echo "=========================================="
docker-compose exec app python scripts/test/test_integration.py
echo "=========================================="
echo ""

echo "테스트 완료!"

