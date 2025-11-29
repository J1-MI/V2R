# EC2 파일 동기화 가이드

## 문제 상황

로컬에서 Dockerfile.dev를 수정했지만, EC2 서버의 파일은 아직 업데이트되지 않았습니다.

## 해결 방법

### 방법 1: Git을 통한 동기화 (권장)

```bash
# EC2 서버에서 실행
cd ~/V2R
git pull origin main
docker-compose build --no-cache app
docker-compose up -d
```

### 방법 2: 수동으로 파일 복사

로컬에서:
```bash
# SCP로 파일 전송
scp Dockerfile.dev ec2-user@YOUR_EC2_IP:~/V2R/Dockerfile.dev
```

EC2에서:
```bash
cd ~/V2R
docker-compose build --no-cache app
docker-compose up -d
```

### 방법 3: GitHub Actions 사용

1. 로컬에서 변경사항 커밋 및 푸시:
```bash
git add Dockerfile.dev
git commit -m "Fix: Nuclei installation using direct binary download"
git push origin main
```

2. GitHub Actions가 자동으로 EC2에 배포합니다.

## 확인 방법

```bash
# EC2에서 실행
docker-compose exec app which nuclei
docker-compose exec app nuclei -version
```

## 예상 출력

```
/usr/local/bin/nuclei
3.2.0
```

