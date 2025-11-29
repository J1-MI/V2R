#!/bin/bash
# Nuclei 수동 설치 스크립트 (컨테이너 내부에서 실행)

set -e

echo "=== Nuclei 설치 스크립트 ==="

# 아키텍처 확인
ARCH=$(uname -m)
echo "Architecture: $ARCH"

if [ "$ARCH" != "x86_64" ]; then
    echo "Error: This script only supports x86_64 architecture"
    exit 1
fi

# Nuclei 버전
NUCLEI_VERSION="v3.2.0"
INSTALL_DIR="/usr/local/bin"
TEMP_DIR="/tmp"

echo "Installing Nuclei ${NUCLEI_VERSION}..."

# 기존 파일 확인
if [ -f "$INSTALL_DIR/nuclei" ]; then
    echo "Removing existing Nuclei installation..."
    rm -f "$INSTALL_DIR/nuclei"
fi

# 다운로드 및 설치
cd "$TEMP_DIR"
echo "Downloading Nuclei..."
wget -q "https://github.com/projectdiscovery/nuclei/releases/download/${NUCLEI_VERSION}/nuclei_${NUCLEI_VERSION}_linux_amd64.zip" || {
    echo "Error: Failed to download Nuclei"
    exit 1
}

echo "Extracting..."
unzip -q "nuclei_${NUCLEI_VERSION}_linux_amd64.zip" || {
    echo "Error: Failed to extract Nuclei"
    exit 1
}

echo "Installing to $INSTALL_DIR..."
mv nuclei "$INSTALL_DIR/nuclei"
chmod +x "$INSTALL_DIR/nuclei"

# 정리
rm -f "nuclei_${NUCLEI_VERSION}_linux_amd64.zip"

# 확인
echo "Verifying installation..."
if [ -f "$INSTALL_DIR/nuclei" ]; then
    "$INSTALL_DIR/nuclei" -version
    echo "✓ Nuclei installed successfully!"
    
    # 템플릿 업데이트 시도
    echo "Updating templates..."
    "$INSTALL_DIR/nuclei" -update-templates || echo "Warning: Template update failed (this is optional)"
else
    echo "Error: Installation failed - file not found"
    exit 1
fi

echo "=== Installation complete ==="

