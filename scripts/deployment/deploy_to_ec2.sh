#!/bin/bash
# EC2 서버 배포 스크립트
# 사용법: ./deploy_to_ec2.sh <ec2-ip> <key-file> [user]

set -e

EC2_IP=$1
KEY_FILE=$2
USER=${3:-ubuntu}

if [ -z "$EC2_IP" ] || [ -z "$KEY_FILE" ]; then
    echo "Usage: $0 <ec2-ip> <key-file> [user]"
    echo "Example: $0 1.2.3.4 ~/.ssh/my-key.pem ubuntu"
    exit 1
fi

if [ ! -f "$KEY_FILE" ]; then
    echo "Error: Key file not found: $KEY_FILE"
    exit 1
fi

echo "=========================================="
echo "V2R EC2 배포 스크립트"
echo "=========================================="
echo "EC2 IP: $EC2_IP"
echo "User: $USER"
echo "Key File: $KEY_FILE"
echo "=========================================="
echo ""

# 프로젝트 루트 확인
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

echo "1. 프로젝트 파일 압축 중..."
cd "$PROJECT_ROOT"
tar --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='*.pyc' \
    --exclude='evidence' \
    --exclude='reports' \
    --exclude='.env' \
    -czf /tmp/v2r_deploy.tar.gz .

echo "2. EC2 서버로 파일 전송 중..."
scp -i "$KEY_FILE" /tmp/v2r_deploy.tar.gz "$USER@$EC2_IP:/tmp/"

echo "3. EC2 서버에서 배포 실행 중..."
ssh -i "$KEY_FILE" "$USER@$EC2_IP" << 'ENDSSH'
    # 디렉토리 생성
    mkdir -p ~/V2R
    cd ~/V2R
    
    # 기존 파일 백업 (있는 경우)
    if [ -d "V2R" ]; then
        mv V2R V2R.backup.$(date +%Y%m%d_%H%M%S)
    fi
    
    # 파일 압축 해제
    tar -xzf /tmp/v2r_deploy.tar.gz
    rm /tmp/v2r_deploy.tar.gz
    
    echo "4. 환경 설정 확인 중..."
    
    # Python 확인
    if ! command -v python3 &> /dev/null; then
        echo "Python3 설치 중..."
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip
    fi
    
    # Docker 확인
    if ! command -v docker &> /dev/null; then
        echo "Docker 설치 중..."
        sudo apt-get update
        sudo apt-get install -y docker.io docker-compose
        sudo systemctl start docker
        sudo systemctl enable docker
        sudo usermod -aG docker $USER
    fi
    
    echo "5. .env 파일 확인..."
    if [ ! -f .env ]; then
        echo "⚠️  .env 파일이 없습니다. 수동으로 생성해주세요."
        echo "   예시: cp .env.example .env"
    fi
    
    echo ""
    echo "=========================================="
    echo "배포 완료!"
    echo "=========================================="
    echo "다음 단계:"
    echo "1. SSH로 접속: ssh -i $KEY_FILE $USER@$EC2_IP"
    echo "2. .env 파일 설정: cd ~/V2R && nano .env"
    echo "3. Docker Compose 실행: docker-compose up -d"
    echo "4. 또는 로컬 설치: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    echo "=========================================="
ENDSSH

echo ""
echo "배포 스크립트 실행 완료!"
echo "EC2 서버에 접속하여 추가 설정을 진행하세요."

