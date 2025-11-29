# 전체 시스템 통합 테스트 가이드

## 개요

V2R 프로젝트의 모든 주요 기능을 순차적으로 테스트하는 통합 테스트 스크립트입니다.

## 테스트 항목

1. **데이터베이스 연결** - PostgreSQL 연결 및 초기화
2. **Nmap 스캐너** - 포트 스캔 기능
3. **Nuclei 스캐너** - 취약점 스캔 기능
4. **스캐너 파이프라인** - 전체 스캔 프로세스
5. **PoC 재현 파이프라인** - 취약점 재현
6. **신뢰도 점수 계산** - PoC 신뢰도 평가
7. **리포트 생성** - 자동 리포트 생성

## 실행 방법

### 방법 1: Makefile 사용 (권장)

```bash
# 전체 테스트 실행
make test-full

# 통합 테스트만 실행
make test-integration

# 파이프라인 테스트만 실행
make test-pipeline

# 기본 스캐너 테스트
make test
```

### 방법 2: 직접 실행

```bash
# Docker 컨테이너 내부에서
docker-compose exec app python scripts/test/run_full_test.py

# 또는 컨테이너에 접속 후
docker-compose exec app bash
python scripts/test/run_full_test.py
```

### 방법 3: 스크립트 사용

```bash
# EC2에서 실행
bash scripts/test/run_full_test.sh
```

## 예상 출력

```
============================================================
V2R 전체 시스템 통합 테스트
============================================================

============================================================
[1/7] 데이터베이스 연결 테스트
============================================================
✓ 데이터베이스 연결 성공
✓ 데이터베이스 초기화 완료

============================================================
[2/7] Nmap 스캐너 테스트
============================================================
✓ Nmap 스캔 성공: 3개 발견

============================================================
[3/7] Nuclei 스캐너 테스트
============================================================
✓ Nuclei 스캐너 초기화 성공

...

============================================================
테스트 결과 요약
============================================================
  database            : ✓ 통과
  nmap                : ✓ 통과
  nuclei              : ✓ 통과
  pipeline            : ✓ 통과
  poc                 : ✓ 통과
  reliability         : ✓ 통과
  report              : ✓ 통과

------------------------------------------------------------
총 7개 테스트 중 7개 통과 (100%)
============================================================
🎉 모든 테스트 통과!
```

## 문제 해결

### 데이터베이스 연결 실패

```bash
# 데이터베이스 상태 확인
docker-compose ps postgres

# 데이터베이스 로그 확인
docker-compose logs postgres

# 데이터베이스 재시작
docker-compose restart postgres
```

### Nuclei 설치 확인

```bash
# Nuclei 설치 확인
docker-compose exec app which nuclei
docker-compose exec app nuclei -version
```

### PoC 재현 실패

PoC 재현은 Docker 소켓 접근이 필요합니다. Docker 소켓이 마운트되어 있는지 확인:

```bash
# docker-compose.yml에서 확인
# volumes에 /var/run/docker.sock:/var/run/docker.sock:ro 가 있어야 함
```

## 개별 테스트 실행

특정 기능만 테스트하려면:

```bash
# Nmap만 테스트
docker-compose exec app python -c "
from src.scanner.nmap_scanner import NmapScanner
s = NmapScanner()
print(s.scan('127.0.0.1', ports='22,80'))
"

# Nuclei만 테스트
docker-compose exec app python -c "
from src.scanner.nuclei_scanner import NucleiScanner
s = NucleiScanner()
print('Installed:', s._check_nuclei_installed())
"
```

## 다음 단계

테스트가 모두 통과하면:
1. CCE 점검 스크립트 개발 진행
2. 실제 취약한 웹 서버 대상 테스트
3. 전체 워크플로우 검증

