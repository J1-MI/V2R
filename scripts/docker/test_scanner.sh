#!/bin/bash
# Docker 환경에서 스캐너 테스트 실행

set -e

echo "Running scanner tests in Docker..."

# 애플리케이션 컨테이너에서 스캐너 테스트 실행
docker-compose exec app python src/scanner/test_scanner.py

