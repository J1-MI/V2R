#!/bin/bash
set -e

# 로그 설정
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1
echo "Starting user-data script for scanner - $(date)"

# 패키지 업데이트
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get upgrade -y

# 기본 패키지 설치
apt-get install -y \
    curl \
    wget \
    git \
    python3 \
    python3-pip \
    docker.io \
    docker-compose \
    nmap \
    net-tools \
    jq

# Docker 서비스 시작
systemctl enable docker
systemctl start docker

# Python 패키지 설치
pip3 install --upgrade pip
pip3 install \
    requests \
    boto3 \
    python-nmap \
    nuclei-python \
    pandas \
    sqlalchemy \
    psycopg2-binary

# 스캐너 디렉토리 생성
mkdir -p /opt/v2r/scanner
mkdir -p /opt/v2r/scanner/results
mkdir -p /opt/v2r/scanner/logs

# Nuclei 설치
if ! command -v nuclei &> /dev/null; then
    wget -q -O - https://raw.githubusercontent.com/projectdiscovery/nuclei/main/install.sh | bash
    export PATH=$PATH:/root/go/bin
fi

# 작업 디렉토리 설정
cd /opt/v2r/scanner

# 기본 스캔 스크립트 생성
cat > scan.sh << 'EOF'
#!/bin/bash
# 기본 스캔 스크립트

TARGET=$1
RESULTS_DIR="/opt/v2r/scanner/results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$RESULTS_DIR"

echo "Starting scan for $TARGET at $(date)"

# Nmap 스캔
echo "Running Nmap..."
nmap -sV -sC -oA "$RESULTS_DIR/nmap_${TIMESTAMP}" "$TARGET"

# Nuclei 스캔
echo "Running Nuclei..."
nuclei -u "$TARGET" -o "$RESULTS_DIR/nuclei_${TIMESTAMP}.json" -json

echo "Scan completed at $(date)"
EOF
chmod +x scan.sh

# 로그 파일 생성
touch /var/log/v2r-scanner.log
chmod 666 /var/log/v2r-scanner.log

echo "Scanner setup completed - $(date)"

