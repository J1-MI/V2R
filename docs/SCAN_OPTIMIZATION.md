# 스캔 최적화 가이드

## 개요

CVE-Lab 스캔 속도를 최적화하기 위한 설정 및 방법을 안내합니다.

## 최적화 내용

### 1. Nmap 스캔 최적화

- **기본 타임아웃**: 300초 → 60초
- **빠른 모드**: 단일 포트 스캔 시 버전 감지 제외 (`-sS` 사용)
- **단일 포트 스캔**: 포트 범위 대신 특정 포트만 스캔

### 2. Nuclei 스캔 최적화

- **Rate Limit 증가**: 150 → 300 (초당 요청 수)
- **심각도 필터**: Critical/High만 스캔
- **타임아웃**: 10분 (600초)

### 3. 병렬 스캔

- **HTTP 서비스**: 최대 3개 동시 스캔
- **비HTTP 서비스**: 최대 2개 동시 스캔
- **빠른 모드에서만 활성화**

### 4. 무인증 체크 최적화

- **타임아웃**: 5초
- **소켓 레벨 체크**: 빠른 연결 확인

## 사용 방법

### 기본 실행 (빠른 모드 + 병렬 스캔)

```bash
docker exec v2r-app python scripts/test/scan_cve_lab_full.py
```

### DB 리셋 후 스캔

```bash
# DB 리셋
docker exec v2r-app python scripts/utils/reset_db.py

# 스캔 실행
docker exec v2r-app python scripts/test/scan_cve_lab_full.py
```

### 옵션 사용

```bash
# DB 리셋과 함께 실행
docker exec v2r-app python scripts/test/scan_cve_lab_full.py --reset-db

# 빠른 모드 비활성화 (상세 스캔)
docker exec v2r-app python scripts/test/scan_cve_lab_full.py --no-fast

# 병렬 스캔 비활성화 (순차 스캔)
docker exec v2r-app python scripts/test/scan_cve_lab_full.py --no-parallel

# DB 초기화만 (리셋 아님)
docker exec v2r-app python scripts/test/scan_cve_lab_full.py --init-db
```

## 예상 소요 시간

### 빠른 모드 (기본)

- **HTTP 서비스 3개**: 약 2-3분 (병렬)
- **비HTTP 서비스 2개**: 약 10-20초 (병렬)
- **총 소요 시간**: 약 3-4분

### 상세 모드 (--no-fast)

- **HTTP 서비스 3개**: 약 5-8분 (순차)
- **비HTTP 서비스 2개**: 약 30초 (순차)
- **총 소요 시간**: 약 6-9분

## 성능 비교

| 모드 | 병렬 | Nmap 타임아웃 | Nuclei Rate Limit | 예상 시간 |
|------|------|---------------|-------------------|-----------|
| 빠른 모드 (기본) | ✅ | 60초 | 300 | 3-4분 |
| 상세 모드 | ❌ | 300초 | 150 | 6-9분 |

## 추가 최적화 팁

### 1. 특정 서비스만 스캔

스크립트를 수정하여 특정 서비스만 스캔하도록 설정할 수 있습니다:

```python
# scripts/test/scan_cve_lab_full.py 수정
# self.services에서 원하는 서비스만 남기기
```

### 2. Nuclei 템플릿 필터링

특정 CVE 템플릿만 사용하여 스캔 속도 향상:

```python
nuclei_result = self.scanner_pipeline.run_nuclei_scan(
    target=url,
    severity=["critical", "high"],
    template_files=["/path/to/specific/template.yaml"],  # 특정 템플릿만
    save_to_db=True
)
```

### 3. Nmap 스캔 타입 조정

더 빠른 스캔을 위해 스캔 타입 변경:

- `-sS`: SYN 스캔 (가장 빠름, 버전 감지 없음)
- `-sV`: 버전 감지 (느리지만 상세)
- `-sT`: TCP 연결 스캔 (중간)

## 문제 해결

### 스캔이 여전히 느린 경우

1. **네트워크 지연 확인**
   ```bash
   docker exec v2r-app ping -c 3 host.docker.internal
   ```

2. **타임아웃 조정**
   - `src/scanner/nmap_scanner.py`에서 `scan_timeout` 조정
   - `src/scanner/nuclei_scanner.py`에서 `timeout` 조정

3. **병렬 스캔 비활성화**
   ```bash
   docker exec v2r-app python scripts/test/scan_cve_lab_full.py --no-parallel
   ```

### 메모리 부족 오류

병렬 스캔 시 메모리 사용량이 증가할 수 있습니다. 순차 스캔으로 전환:

```bash
docker exec v2r-app python scripts/test/scan_cve_lab_full.py --no-parallel
```



