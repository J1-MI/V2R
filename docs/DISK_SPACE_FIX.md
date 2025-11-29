# 디스크 공간 부족 문제 해결

## 문제

Docker 빌드 중 `nvidia-nccl-cu12` 패키지(296.8MB) 설치 시 디스크 공간 부족 오류 발생.

## 해결 방법

### 1. 즉시 해결 (EC2에서 실행)

```bash
# Docker 시스템 정리
docker system prune -a --volumes -f

# 디스크 공간 확인
df -h

# 사용하지 않는 이미지/컨테이너 삭제
docker images
docker ps -a
docker rm $(docker ps -a -q) 2>/dev/null || true
docker rmi $(docker images -q) 2>/dev/null || true
```

### 2. xgboost GPU 의존성 제거

`requirements.txt`에서 xgboost를 조건부로 설치하도록 수정했습니다:
- GPU가 없는 환경에서는 GPU 의존성 설치 안 함
- CPU 버전만 설치

### 3. Dockerfile.dev 개선

- 빌드 후 자동으로 캐시 및 임시 파일 정리
- 디스크 공간 절약

### 4. 대안: xgboost 제거 (필요 없는 경우)

ML 우선순위 모델을 사용하지 않는다면:

```bash
# requirements.txt에서 xgboost 라인 제거 또는 주석 처리
# xgboost>=2.0.0
```

## 확인

```bash
# 디스크 공간 확인
df -h

# Docker 디스크 사용량 확인
docker system df

# 빌드 재시도
docker-compose build --no-cache app
```

## 예방 조치

1. 정기적인 Docker 정리:
```bash
docker system prune -a --volumes
```

2. 불필요한 패키지 제거
3. 빌드 캐시 모니터링

