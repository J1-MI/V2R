#!/bin/bash
# Docker 환경 초기화 스크립트

set -e

echo "=========================================="
echo "V2R Docker Environment Setup"
echo "=========================================="

# .env 파일 확인
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ .env file created. Please edit it with your configuration."
    else
        echo "❌ .env.example not found. Creating basic .env..."
        cat > .env << EOF
# Database
DB_HOST=postgres
DB_PORT=5432
DB_NAME=v2r
DB_USER=v2r
DB_PASSWORD=v2r_password

# AWS (optional)
AWS_REGION=ap-northeast-2

# LLM (optional)
LLM_MODEL=gpt-4
EOF
    fi
fi

# Docker 이미지 빌드
echo ""
echo "📦 Building Docker images..."
docker-compose build

# 데이터베이스 초기화
echo ""
echo "🗄️  Initializing database..."
docker-compose up -d postgres

# PostgreSQL이 준비될 때까지 대기
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 5

# 스키마 생성
echo "📋 Creating database schema..."
docker-compose exec -T postgres psql -U v2r -d v2r < src/database/schema.sql || \
    docker-compose exec app python scripts/utils/init_db.py

echo ""
echo "✅ Docker environment initialized!"
echo ""
echo "To start the services:"
echo "  docker-compose up -d"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop the services:"
echo "  docker-compose down"

