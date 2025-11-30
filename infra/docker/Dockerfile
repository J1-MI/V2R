# V2R 프로젝트 Docker 이미지
# Python + Conda 환경 구성

FROM continuumio/miniconda3:latest

# 작업 디렉토리 설정
WORKDIR /app

# 메타데이터
LABEL maintainer="V2R Project"
LABEL description="Vulnerability-to-Report Automation System"

# 시스템 패키지 업데이트 및 필수 도구 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    wget \
    git \
    vim \
    nmap \
    postgresql-client \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Conda 환경 설정
RUN conda update -n base -c defaults conda && \
    conda install -y python=3.11 && \
    conda clean -afy

# Python 패키지 설치를 위한 pip 업그레이드
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# requirements.txt 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    pip list --format=freeze > /tmp/installed_packages.txt && \
    echo "Installed packages:" && cat /tmp/installed_packages.txt | head -20

# Nuclei 설치 (보안 스캐너) - 직접 바이너리 다운로드 방식
RUN if [ "$(uname -m)" = "x86_64" ]; then \
        NUCLEI_VERSION="v3.2.0" && \
        wget -q https://github.com/projectdiscovery/nuclei/releases/download/${NUCLEI_VERSION}/nuclei_${NUCLEI_VERSION}_linux_amd64.zip && \
        unzip -q nuclei_${NUCLEI_VERSION}_linux_amd64.zip -d /tmp && \
        mv /tmp/nuclei /usr/local/bin/nuclei && \
        chmod +x /usr/local/bin/nuclei && \
        rm -f nuclei_${NUCLEI_VERSION}_linux_amd64.zip && \
        nuclei -version && \
        nuclei -update-templates || echo "Warning: Failed to update nuclei templates"; \
    else \
        echo "Warning: Nuclei installation skipped for architecture $(uname -m)"; \
    fi

# 프로젝트 파일 복사
COPY . .

# src 디렉토리를 Python 패키지로 인식
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 작업 디렉토리 확인
RUN echo "Python version: $(python --version)" && \
    echo "Pip version: $(pip --version)" && \
    echo "Nmap version: $(nmap --version | head -1)" && \
    nuclei -version || echo "Nuclei not installed"

# 기본 명령어 (docker-compose에서 override 가능)
CMD ["python", "-m", "src.scanner.test_scanner"]

