#!/bin/bash
# EC2 서버 초기 설정 스크립트
# EC2 서버에서 직접 실행

set -e

echo "=========================================="
echo "V2R EC2 서버 초기 설정"
echo "=========================================="

# 시스템 업데이트
echo "1. 시스템 업데이트 중..."
sudo apt-get update
sudo apt-get upgrade -y

# 필수 패키지 설치
echo "2. 필수 패키지 설치 중..."
sudo apt-get install -y \
    python3.11 \
    python3-pip \
    python3-venv \
    git \
    docker.io \
    docker-compose \
    postgresql-client \
    nmap \
    build-essential \
    python3-dev \
    curl \
    wget

# Docker 설정
echo "3. Docker 설정 중..."
sudo systemctl start docker
sudo systemctl enable docker

# Docker 그룹에 사용자 추가
if ! groups | grep -q docker; then
    sudo usermod -aG docker $USER
    echo "⚠️  Docker 그룹에 추가되었습니다. 재로그인 후 적용됩니다."
fi

# Nuclei 설치
echo "4. Nuclei 설치 중..."
if ! command -v nuclei &> /dev/null; then
    if command -v go &> /dev/null; then
        go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
    else
        wget -q -O - https://raw.githubusercontent.com/projectdiscovery/nuclei/main/install.sh | bash || echo "Nuclei 설치 실패 (수동 설치 필요)"
    fi
fi

# PostgreSQL 설치 (선택)
echo "5. PostgreSQL 설치 중 (선택)..."
read -p "PostgreSQL을 로컬에 설치하시겠습니까? (y/n): " install_pg
if [ "$install_pg" = "y" ]; then
    sudo apt-get install -y postgresql postgresql-contrib
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
    
    echo "PostgreSQL 데이터베이스 설정..."
    read -p "DB 비밀번호를 입력하세요: " db_password
    sudo -u postgres psql << EOF
CREATE DATABASE v2r;
CREATE USER v2r WITH PASSWORD '$db_password';
GRANT ALL PRIVILEGES ON DATABASE v2r TO v2r;
\q
EOF
    echo "PostgreSQL 설정 완료"
fi

# 프로젝트 디렉토리 확인
if [ ! -d "~/V2R" ]; then
    echo "6. 프로젝트 디렉토리 생성..."
    mkdir -p ~/V2R
fi

echo ""
echo "=========================================="
echo "초기 설정 완료!"
echo "=========================================="
echo "다음 단계:"
echo "1. 프로젝트 파일을 ~/V2R에 배치"
echo "2. .env 파일 설정"
echo "3. Python 가상환경 생성 및 의존성 설치"
echo "   또는 Docker Compose 사용"
echo "=========================================="

