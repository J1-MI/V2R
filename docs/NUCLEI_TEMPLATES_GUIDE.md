# Nuclei 템플릿 확인 및 관리 가이드

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

## 참고

- Nuclei 템플릿 저장소: https://github.com/projectdiscovery/nuclei-templates
- 템플릿 문서: https://docs.nuclei.sh/

