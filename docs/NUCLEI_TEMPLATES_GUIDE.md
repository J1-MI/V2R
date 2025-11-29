# Nuclei 설치 및 템플릿 관리 가이드

## 개요

이 가이드는 V2R 프로젝트에서 Nuclei를 설치하고, 템플릿을 관리하는 방법을 설명합니다.

## Nuclei 설치

### Dockerfile에서 자동 설치

Nuclei는 `Dockerfile.dev`에서 자동으로 설치됩니다:

```dockerfile
# Go 설치 후 Nuclei 소스에서 빌드
RUN wget -q https://go.dev/dl/go1.21.5.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go1.21.5.linux-amd64.tar.gz && \
    export PATH=$PATH:/usr/local/go/bin && \
    cd /tmp && \
    git clone https://github.com/projectdiscovery/nuclei.git && \
    cd nuclei/v2/cmd/nuclei && \
    go build -o nuclei && \
    mv nuclei /usr/local/bin/nuclei && \
    chmod +x /usr/local/bin/nuclei && \
    cd / && rm -rf /tmp/nuclei && \
    /usr/local/bin/nuclei -version && \
    /usr/local/bin/nuclei -update-templates
```

### 설치 확인

```bash
# 컨테이너 내부에서
docker-compose exec app which nuclei
# 예상 출력: /usr/local/bin/nuclei

# 버전 확인
docker-compose exec app nuclei -version
```

### 수동 설치 (문제 해결 시)

Dockerfile 설치가 실패한 경우, 컨테이너 내부에서 수동 설치:

```bash
# 컨테이너 내부에서 직접 설치
docker-compose exec app bash -c "
ARCH=\$(uname -m)
if [ \"\$ARCH\" = \"x86_64\" ]; then
    NUCLEI_VERSION=\"v3.2.0\"
    cd /tmp
    wget -q https://github.com/projectdiscovery/nuclei/releases/download/\${NUCLEI_VERSION}/nuclei_\${NUCLEI_VERSION}_linux_amd64.zip
    unzip -q nuclei_\${NUCLEI_VERSION}_linux_amd64.zip
    mv nuclei /usr/local/bin/nuclei
    chmod +x /usr/local/bin/nuclei
    rm -f nuclei_\${NUCLEI_VERSION}_linux_amd64.zip
    /usr/local/bin/nuclei -version
fi
"
```

## Nuclei 설치 경로 확인

### 실행 파일 위치

```bash
# 컨테이너 내부에서
docker-compose exec app which nuclei
# 예상 출력: /usr/local/bin/nuclei

# 버전 확인
docker-compose exec app nuclei -version
```

### 템플릿 저장 경로 확인

Nuclei 템플릿은 기본적으로 다음 경로에 저장됩니다:

```bash
# 컨테이너 내부에서 확인
docker-compose exec app bash -c "nuclei -ut 2>&1 | grep -i template"

# 또는 직접 경로 확인
docker-compose exec app bash -c "ls -la ~/.local/share/nuclei/templates/ 2>/dev/null || ls -la ~/.config/nuclei/templates/ 2>/dev/null || echo 'Templates path not found'"
```

일반적인 템플릿 경로:
- `~/.local/share/nuclei/templates/` (Linux, 기본 경로)
- `~/.config/nuclei/templates/` (대체 경로)

### 템플릿 목록 확인

```bash
# 전체 템플릿 개수 확인
docker-compose exec app nuclei -tl

# CVE 템플릿만 확인
docker-compose exec app nuclei -tl -tags cve | head -20

# Text4Shell 관련 템플릿 검색
docker-compose exec app nuclei -tl -tags text4shell

# CVE-2022-42889 템플릿 검색
docker-compose exec app nuclei -tl -id CVE-2022-42889
```

### 템플릿 업데이트

```bash
# 템플릿 업데이트
docker-compose exec app nuclei -update-templates

# 템플릿 업데이트 및 경로 확인
docker-compose exec app nuclei -ut
```

## 템플릿 내용 확인

특정 템플릿의 내용을 확인하려면:

```bash
# 템플릿 파일 직접 확인 (경로를 찾은 후)
docker-compose exec app find ~/.local/share/nuclei/templates -name "*text4shell*" -o -name "*CVE-2022-42889*"

# 템플릿 내용 보기
docker-compose exec app cat ~/.local/share/nuclei/templates/cves/2022/CVE-2022-42889.yaml
```

## 템플릿 검증

```bash
# 템플릿 검증 (런타임 에러 확인)
docker-compose exec app nuclei -validate

# 특정 템플릿만 검증
docker-compose exec app nuclei -validate -t ~/.local/share/nuclei/templates/cves/2022/CVE-2022-42889.yaml
```

## 문제 해결

### 템플릿이 없는 경우

```bash
# 템플릿 강제 재다운로드
docker-compose exec app rm -rf ~/.local/share/nuclei/templates
docker-compose exec app nuclei -update-templates
```

### 템플릿 경로 문제

```bash
# 환경 변수로 템플릿 경로 지정
docker-compose exec app bash -c "export NUCLEI_TEMPLATES_DIR=/custom/path && nuclei -u http://target"
```

## 템플릿 경로 설정

### 기본 템플릿 경로

Nuclei 템플릿은 기본적으로 다음 경로에 저장됩니다:
- `/usr/local/bin/nuclei-templates` (Dockerfile에서 git clone)
- `~/.local/share/nuclei/templates/` (Linux, 기본 경로)
- `~/.config/nuclei/templates/` (대체 경로)

### 환경 변수로 경로 지정

V2R 프로젝트에서는 환경 변수 `NUCLEI_TEMPLATES_PATH`를 사용합니다:

```bash
# .env 파일 또는 docker-compose.yml
NUCLEI_TEMPLATES_PATH=/usr/local/bin/nuclei-templates
```

### 로컬 템플릿 마운트 (선택사항)

로컬 PC의 템플릿 디렉토리를 Docker 컨테이너에 마운트:

```yaml
# docker-compose.yml
volumes:
  - ../nuclei-templates:/app/nuclei-templates:ro
```

그리고 환경 변수 설정:
```yaml
environment:
  NUCLEI_TEMPLATES_PATH: /app/nuclei-templates
```

## 템플릿 디버깅

### DAST 템플릿 문제 해결

DAST (Dynamic Application Security Testing) 템플릿 사용 시 문제가 발생할 수 있습니다:

```bash
# 템플릿 검증
nuclei -validate -t /usr/local/bin/nuclei-templates/dast/cves/2022/CVE-2022-42889.yaml

# 디버그 모드로 실행
nuclei -u http://target:8080 \
  -t /usr/local/bin/nuclei-templates/dast/cves/2022/CVE-2022-42889.yaml \
  -debug \
  2>&1
```

### 템플릿 경로 문제 해결

템플릿을 찾을 수 없는 경우:

```bash
# 템플릿 강제 재다운로드
docker-compose exec app rm -rf ~/.local/share/nuclei/templates
docker-compose exec app nuclei -update-templates

# 또는 환경 변수로 경로 지정
docker-compose exec app bash -c "export NUCLEI_TEMPLATES_DIR=/custom/path && nuclei -u http://target"
```

## 참고

- Nuclei 템플릿 저장소: https://github.com/projectdiscovery/nuclei-templates
- 템플릿 문서: https://docs.nuclei.sh/
- Nuclei 공식 문서: https://docs.nuclei.sh/

