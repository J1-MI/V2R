# EC2 테스트 오류 수정 내역

**수정 일자:** 2025-11-27

## 발견된 오류

### 1. Docker 클라이언트 초기화 실패
**오류 메시지:**
```
ERROR:src.poc.isolation:Failed to initialize Docker client: Error while fetching server API version: ('Connection aborted.', FileNotFoundError(2, 'No such file or directory'))
```

**원인:**
- Docker 컨테이너 내에서 Docker 소켓에 접근할 수 없음 (Docker-in-Docker 문제)
- 테스트 환경에서 Docker가 사용 불가능한 경우

**수정 내용:**
- `IsolationEnvironment` 클래스에 `allow_docker_failure` 파라미터 추가
- Docker 클라이언트 초기화 실패 시 예외 대신 경고 로그 출력
- Docker가 없을 때 graceful하게 처리하도록 수정

**수정 파일:**
- `src/poc/isolation.py`
- `src/poc/reproduction.py`
- `src/pipeline/poc_pipeline.py`

### 2. SQLAlchemy DetachedInstanceError
**오류 메시지:**
```
sqlalchemy.orm.exc.DetachedInstanceError: Instance <ScanResult at 0x7f8772909510> is not bound to a Session; attribute refresh operation cannot proceed
```

**원인:**
- 데이터베이스 세션이 닫힌 후 객체의 속성에 접근하려고 시도
- `to_dict()` 메서드를 세션 외부에서 호출

**수정 내용:**
- 세션 내에서 `to_dict()` 호출하도록 수정
- 세션이 닫히기 전에 필요한 데이터를 모두 추출

**수정 파일:**
- `scripts/test/test_integration.py`

## 수정된 코드

### 1. Docker 클라이언트 초기화 (isolation.py)
```python
def __init__(self, base_image: str = "python:3.11-slim", allow_docker_failure: bool = False):
    # ...
    try:
        self.client = docker.from_env()
        logger.info("Docker client initialized")
    except Exception as e:
        if allow_docker_failure:
            logger.warning(f"Docker client initialization failed (will skip Docker operations): {str(e)}")
        else:
            logger.error(f"Failed to initialize Docker client: {str(e)}")
            raise
```

### 2. PoC 재현 시 Docker 체크 (reproduction.py)
```python
# Docker가 사용 불가능한 경우 스킵
if self.isolation.client is None:
    logger.warning("Docker is not available, skipping PoC isolation. Using mock result.")
    return {
        "reproduction_id": self.reproduction_id,
        "status": "skipped",
        # ... 모의 결과 반환
    }
```

### 3. 세션 내에서 to_dict() 호출 (test_integration.py)
```python
with db.get_session() as session:
    # ...
    scan_results = scan_repo.get_recent(days=7, limit=10)
    poc_reproductions = poc_repo.get_successful_reproductions()
    
    # 세션 내에서 to_dict() 호출
    scan_results_dict = [s.to_dict() for s in scan_results]
    poc_reproductions_dict = [p.to_dict() for p in poc_reproductions]

# 세션 외부에서 사용
report_result = report_generator.generate_report(
    scan_results=scan_results_dict,
    poc_reproductions=poc_reproductions_dict
)
```

## 테스트 방법

### 수정 후 테스트 실행
```bash
python scripts/test/test_integration.py
```

**예상 결과:**
- Docker가 없어도 테스트가 계속 진행됨
- PoC 재현은 "skipped" 상태로 처리되지만 테스트는 완료됨
- 리포트 생성이 정상적으로 동작함

## 참고사항

### Docker-in-Docker 해결 방법 (선택적)

실제 PoC 격리 재현을 사용하려면:

1. **Docker 소켓 마운트** (docker-compose.yml에 추가):
```yaml
volumes:
  - /var/run/docker.sock:/var/run/docker.sock
```

2. **또는 Docker-in-Docker 사용**:
```yaml
services:
  app:
    image: docker:dind
    privileged: true
```

현재는 테스트 환경에서 Docker 없이도 동작하도록 수정되었으므로, 실제 PoC 재현이 필요할 때만 Docker 설정을 추가하면 됩니다.

