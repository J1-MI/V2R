# Text4Shell 템플릿 사용 가이드

## 템플릿 위치 확인

Nuclei 템플릿은 `/usr/local/bin/nuclei-templates/` 경로에 있습니다.

### Text4Shell (CVE-2022-42889) 템플릿 찾기

```bash
# 컨테이너 내부에서
docker-compose exec app bash

# Text4Shell 관련 템플릿 검색
find /usr/local/bin/nuclei-templates -name "*text4shell*" -o -name "*CVE-2022-42889*" -o -name "*42889*"

# 또는 CVE JSON에서 확인
grep -i "CVE-2022-42889\|text4shell" /usr/local/bin/nuclei-templates/cves.json

# HTTP 템플릿 폴더에서 검색
find /usr/local/bin/nuclei-templates/http -name "*text4shell*" -o -name "*42889*"
```

### 템플릿 파일 확인

```bash
# 템플릿 파일이 있다면 내용 확인
cat /usr/local/bin/nuclei-templates/http/cves/2022/CVE-2022-42889.yaml

# 또는 모든 CVE 템플릿 목록
ls -la /usr/local/bin/nuclei-templates/http/cves/2022/ | grep -i "42889\|text4shell"
```

## 템플릿 직접 사용

### 방법 1: 특정 템플릿 파일 지정

```bash
# 단일 템플릿 파일 사용
docker-compose exec app nuclei \
  -u http://3.36.15.26:8080 \
  -t /usr/local/bin/nuclei-templates/http/cves/2022/CVE-2022-42889.yaml \
  -json

# 여러 템플릿 파일 사용
docker-compose exec app nuclei \
  -u http://3.36.15.26:8080 \
  -t /usr/local/bin/nuclei-templates/http/cves/2022/CVE-2022-42889.yaml,/usr/local/bin/nuclei-templates/http/cves/2022/CVE-2022-42889-alt.yaml \
  -json
```

### 방법 2: 템플릿 디렉토리 지정

```bash
# 전체 템플릿 디렉토리 사용
docker-compose exec app nuclei \
  -u http://3.36.15.26:8080 \
  -templates /usr/local/bin/nuclei-templates \
  -severity critical,high \
  -json

# 특정 폴더만 사용 (예: CVE 템플릿만)
docker-compose exec app nuclei \
  -u http://3.36.15.26:8080 \
  -templates /usr/local/bin/nuclei-templates/http/cves \
  -json
```

### 방법 3: 태그 기반 필터링

```bash
# Text4Shell 태그가 있는 템플릿만 사용
docker-compose exec app nuclei \
  -u http://3.36.15.26:8080 \
  -templates /usr/local/bin/nuclei-templates \
  -tags text4shell \
  -json

# CVE 태그와 특정 CVE ID
docker-compose exec app nuclei \
  -u http://3.36.15.26:8080 \
  -templates /usr/local/bin/nuclei-templates \
  -tags cve \
  -id CVE-2022-42889 \
  -json
```

## V2R 코드에서 사용

### ScannerPipeline에서 템플릿 경로 지정

```python
from src.pipeline.scanner_pipeline import ScannerPipeline

# 기본 템플릿 경로 사용 (자동으로 /usr/local/bin/nuclei-templates 사용)
scanner = ScannerPipeline()

# 또는 커스텀 템플릿 경로 지정
scanner = ScannerPipeline(nuclei_templates_path="/custom/path/to/templates")

# 스캔 실행 (템플릿 경로가 자동으로 적용됨)
result = scanner.run_nuclei_scan(
    target="http://3.36.15.26:8080",
    severity=["critical", "high"],
    save_to_db=True
)
```

### 특정 템플릿 파일만 사용

`NucleiScanner`를 직접 사용하여 특정 템플릿 파일을 지정할 수 있습니다:

```python
from src.scanner.nuclei_scanner import NucleiScanner

scanner = NucleiScanner(
    templates_path="/usr/local/bin/nuclei-templates"
)

# 특정 템플릿 파일만 사용
result = scanner.scan(
    target="http://3.36.15.26:8080",
    template_types=["/usr/local/bin/nuclei-templates/http/cves/2022/CVE-2022-42889.yaml"]
)
```

## 템플릿이 없는 경우

만약 Text4Shell 템플릿이 공식 저장소에 없다면:

### 옵션 1: 커뮤니티 템플릿 사용

```bash
# 커뮤니티 템플릿 검색
docker-compose exec app bash -c "
  cd /tmp && \
  git clone https://github.com/projectdiscovery/nuclei-templates.git && \
  find nuclei-templates -name '*text4shell*' -o -name '*42889*'
"
```

### 옵션 2: 직접 템플릿 작성

Text4Shell 템플릿을 직접 작성하여 `/usr/local/bin/nuclei-templates/http/cves/2022/CVE-2022-42889.yaml`에 추가할 수 있습니다.

템플릿 작성 가이드: https://docs.nuclei.sh/templating-guide/

## 문제 해결

### 템플릿 경로 오류

```bash
# 템플릿 경로 확인
docker-compose exec app ls -la /usr/local/bin/nuclei-templates/

# 템플릿 재다운로드
docker-compose exec app bash -c "
  rm -rf /usr/local/bin/nuclei-templates/* && \
  cd /usr/local/bin/nuclei-templates && \
  git clone --depth 1 https://github.com/projectdiscovery/nuclei-templates.git .
"
```

### 템플릿 검증

```bash
# 템플릿 검증
docker-compose exec app nuclei -validate -templates /usr/local/bin/nuclei-templates

# 특정 템플릿 검증
docker-compose exec app nuclei -validate -t /usr/local/bin/nuclei-templates/http/cves/2022/CVE-2022-42889.yaml
```

## 참고

- Nuclei 템플릿 저장소: https://github.com/projectdiscovery/nuclei-templates
- 템플릿 작성 가이드: https://docs.nuclei.sh/templating-guide/
- CVE 템플릿 목록: `/usr/local/bin/nuclei-templates/cves.json`

