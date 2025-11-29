# Nuclei 설치 문제 최종 해결

## 문제 원인 분석

### 기존 문제
1. **Go 의존성 누락**: `install.sh` 스크립트는 Go를 필요로 하지만 Dockerfile에 Go가 설치되어 있지 않았습니다.
2. **빌드 실패**: `install.sh`는 소스에서 빌드하는 방식이라 실패할 수 있습니다.
3. **경로 문제**: `/root/go/bin/nuclei` 경로에 파일이 생성되지 않았습니다.

### 에러 메시지
```
mv: cannot stat '/root/go/bin/nuclei': No such file or directory
```

## 해결 방법

### 변경 사항
1. **직접 바이너리 다운로드 방식으로 변경**
   - Go 설치 불필요
   - 빌드 과정 없음
   - 더 빠르고 안정적

2. **Dockerfile.dev 수정**
   ```dockerfile
   # unzip 패키지 추가
   RUN apt-get install -y ... unzip ...
   
   # Nuclei 직접 바이너리 다운로드
   RUN if [ "$(uname -m)" = "x86_64" ]; then \
           NUCLEI_VERSION="v3.2.0" && \
           wget -q https://github.com/projectdiscovery/nuclei/releases/download/${NUCLEI_VERSION}/nuclei_${NUCLEI_VERSION}_linux_amd64.zip && \
           unzip -q nuclei_${NUCLEI_VERSION}_linux_amd64.zip -d /tmp && \
           mv /tmp/nuclei /usr/local/bin/nuclei && \
           chmod +x /usr/local/bin/nuclei && \
           rm -f nuclei_${NUCLEI_VERSION}_linux_amd64.zip && \
           nuclei -version && \
           nuclei -update-templates || echo "Warning: Failed to update nuclei templates"; \
       fi
   ```

## 적용 방법

### 1. 컨테이너 재빌드

```bash
# 기존 컨테이너 중지
docker-compose down

# 캐시 없이 재빌드
docker-compose build --no-cache app

# 컨테이너 시작
docker-compose up -d
```

### 2. Nuclei 설치 확인

```bash
# 컨테이너 내부에서 확인
docker-compose exec app which nuclei
docker-compose exec app nuclei -version
docker-compose exec app ls -la /usr/local/bin/nuclei
```

### 3. 예상 출력

```
/usr/local/bin/nuclei
3.2.0
-rwxr-xr-x 1 root root ... /usr/local/bin/nuclei
```

## 비교: 이전 방식 vs 새로운 방식

### 이전 방식 (install.sh)
- ❌ Go 설치 필요
- ❌ 소스 빌드 필요 (느림)
- ❌ 실패 가능성 높음
- ❌ 의존성 복잡

### 새로운 방식 (직접 바이너리)
- ✅ Go 불필요
- ✅ 즉시 사용 가능 (빠름)
- ✅ 안정적
- ✅ 의존성 단순

## 테스트

```bash
# Nuclei 스캔 테스트
docker-compose exec app python -c "
from src.scanner.nuclei_scanner import NucleiScanner
scanner = NucleiScanner()
print('Nuclei path:', scanner.nuclei_path)
result = scanner._check_nuclei_installed()
print('Installed:', result)
"
```

## 문제 해결 체크리스트

- [x] `unzip` 패키지 추가
- [x] 직접 바이너리 다운로드 방식으로 변경
- [x] 버전 확인 로직 추가
- [x] 에러 처리 개선
- [ ] 컨테이너 재빌드 완료
- [ ] Nuclei 설치 확인 완료
- [ ] 스캔 테스트 완료

## 추가 참고사항

### Nuclei 버전 업데이트
필요시 `NUCLEI_VERSION` 변수를 변경하여 다른 버전을 설치할 수 있습니다:
- `v3.2.0` (현재)
- `v3.1.0`
- `latest` (권장하지 않음 - 안정성 문제)

### 다른 아키텍처 지원
현재는 `x86_64`만 지원합니다. 다른 아키텍처가 필요한 경우:
- ARM64: `nuclei_${VERSION}_linux_arm64.zip`
- ARM: `nuclei_${VERSION}_linux_arm.zip`

