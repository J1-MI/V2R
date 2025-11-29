#!/bin/bash
# 전체 시스템 통합 테스트 실행 스크립트

set -e

echo "============================================================"
echo "V2R 전체 시스템 통합 테스트"
echo "============================================================"
echo ""

# Docker 컨테이너 내부에서 실행
if [ -f /.dockerenv ] || [ -n "$DOCKER_CONTAINER" ]; then
    echo "Docker 컨테이너 내부에서 실행 중..."
    python scripts/test/run_full_test.py
else
    echo "Docker 컨테이너에서 실행합니다..."
    docker-compose exec app python scripts/test/run_full_test.py
fi

