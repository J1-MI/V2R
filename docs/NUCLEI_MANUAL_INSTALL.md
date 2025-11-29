# Nuclei 수동 설치 가이드

## 문제

Dockerfile.dev에서 Nuclei 설치가 실패했습니다. 컨테이너 내부에서 수동으로 설치해야 합니다.

## 즉시 해결 방법

### EC2에서 실행

```bash
# 컨테이너 내부에서 직접 설치
docker-compose exec app bash -c "
ARCH=\$(uname -m)
echo 'Architecture: '\$ARCH

if [ \"\$ARCH\" = \"x86_64\" ]; then
    NUCLEI_VERSION=\"v3.2.0\"
    cd /tmp
    wget -q https://github.com/projectdiscovery/nuclei/releases/download/\${NUCLEI_VERSION}/nuclei_\${NUCLEI_VERSION}_linux_amd64.zip
    unzip -q nuclei_\${NUCLEI_VERSION}_linux_amd64.zip
    mv nuclei /usr/local/bin/nuclei
    chmod +x /usr/local/bin/nuclei
    rm -f nuclei_\${NUCLEI_VERSION}_linux_amd64.zip
    /usr/local/bin/nuclei -version
    echo '✓ Nuclei installed successfully!'
else
    echo 'Error: Unsupported architecture: '\$ARCH
fi
"
```

### 또는 스크립트 사용

```bash
# 스크립트를 컨테이너에 복사하고 실행
docker cp scripts/fix_nuclei_install.sh v2r-app:/tmp/fix_nuclei.sh
docker-compose exec app bash /tmp/fix_nuclei.sh
```

## 확인

```bash
docker-compose exec app which nuclei
docker-compose exec app nuclei -version
```

## 예상 출력

```
/usr/local/bin/nuclei
3.2.0
```

## 근본 원인 해결

빌드 로그를 확인하여 왜 설치가 실패했는지 확인:

```bash
# 빌드 로그 확인 (이전 빌드)
docker-compose build app 2>&1 | grep -A 20 "Nuclei"

# 또는 컨테이너 내부에서 아키텍처 확인
docker-compose exec app uname -m
```

## 영구 해결

컨테이너를 재빌드하되, 빌드 로그를 자세히 확인:

```bash
docker-compose build --no-cache app 2>&1 | tee build.log
```

빌드 로그에서 Nuclei 설치 부분을 확인하고, 실패 원인을 파악하세요.

