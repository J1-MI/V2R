# Nuclei DAST 템플릿 디버깅 가이드

## 문제 상황

Text4Shell 템플릿(`/usr/local/bin/nuclei-templates/dast/cves/2022/CVE-2022-42889.yaml`)을 사용할 때 exit code 2가 발생합니다.

## 직접 테스트

컨테이너 내부에서 직접 명령어를 실행하여 실제 에러를 확인:

```bash
# 컨테이너 접속
docker-compose exec app bash

# 템플릿 파일 확인
ls -la /usr/local/bin/nuclei-templates/dast/cves/2022/CVE-2022-42889.yaml

# 직접 실행 (stderr 확인)
nuclei -u http://3.36.15.26:8080 \
  -json \
  -rate-limit 150 \
  -t /usr/local/bin/nuclei-templates/dast/cves/2022/CVE-2022-42889.yaml \
  -severity critical,high \
  2>&1

# 또는 더 자세한 디버그 정보
nuclei -u http://3.36.15.26:8080 \
  -json \
  -rate-limit 150 \
  -t /usr/local/bin/nuclei-templates/dast/cves/2022/CVE-2022-42889.yaml \
  -severity critical,high \
  -debug \
  2>&1
```

## DAST 템플릿 특성

DAST (Dynamic Application Security Testing) 템플릿은:
- Headless 브라우저를 사용할 수 있음
- 특별한 옵션이 필요할 수 있음
- 템플릿 내용을 확인하여 필요한 옵션 확인

## 템플릿 내용 확인

```bash
# 템플릿 파일 내용 확인
cat /usr/local/bin/nuclei-templates/dast/cves/2022/CVE-2022-42889.yaml

# 템플릿 검증
nuclei -validate -t /usr/local/bin/nuclei-templates/dast/cves/2022/CVE-2022-42889.yaml
```

## 가능한 해결 방법

### 1. 템플릿 검증 오류
템플릿 자체에 문제가 있을 수 있음:
```bash
nuclei -validate -t /usr/local/bin/nuclei-templates/dast/cves/2022/CVE-2022-42889.yaml
```

### 2. DAST 옵션 필요
DAST 템플릿은 특별한 옵션이 필요할 수 있음:
```bash
# headless 옵션 추가
nuclei -u http://3.36.15.26:8080 \
  -t /usr/local/bin/nuclei-templates/dast/cves/2022/CVE-2022-42889.yaml \
  -headless
```

### 3. 템플릿 경로 문제
템플릿 경로가 잘못되었을 수 있음:
```bash
# 상대 경로로 시도
cd /usr/local/bin/nuclei-templates
nuclei -u http://3.36.15.26:8080 \
  -t dast/cves/2022/CVE-2022-42889.yaml
```

### 4. HTTP 템플릿 사용
DAST 대신 HTTP 템플릿을 사용:
```bash
# HTTP 템플릿 검색
find /usr/local/bin/nuclei-templates/http -name "*text4shell*" -o -name "*42889*"
```

## 다음 단계

1. 위 명령어로 실제 에러 메시지 확인
2. 템플릿 내용 확인하여 필요한 옵션 파악
3. 필요시 HTTP 템플릿으로 대체 검토

