#!/bin/bash
# Amazon Linux 2023 초기 설정 스크립트
# EC2 서버에서 직접 실행

set -e

echo "=========================================="
echo "V2R Amazon Linux 2023 초기 설정"
echo "=========================================="

# 시스템 업데이트
echo "1. 시스템 업데이트 중..."
sudo dnf update -y

# 필수 패키지 설치
echo "2. 필수 패키지 설치 중..."
sudo dnf install -y \
    python3.11 \
    python3-pip \
    git \
    docker \
    docker-compose \
    postgresql15 \
    nmap \
    gcc \
    gcc-c++ \
    make \
    python3-devel \
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

# Docker Compose 설치 확인 (없으면 설치)
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose 설치 중..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Nuclei 설치
echo "4. Nuclei 설치 중..."
if ! command -v nuclei &> /dev/null; then
    if command -v go &> /dev/null; then
        go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
    else
        # Go 설치
        echo "Go 설치 중..."
        sudo dnf install -y golang
        export PATH=$PATH:/usr/local/go/bin
        go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
    fi
fi

echo ""
echo "=========================================="
echo "초기 설정 완료!"
echo "=========================================="
echo "다음 단계:"
echo "1. 재로그인: exit 후 다시 SSH 접속"
echo "2. 프로젝트 파일을 ~/V2R에 배치"
echo "3. .env 파일 설정"
echo "4. Docker Compose 사용: docker-compose up -d"
echo "=========================================="

