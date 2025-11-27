# 데이터베이스 인증 오류 해결 가이드

## 오류 분석

### 오류 메시지
```
psycopg2.OperationalError: connection to server at "postgres" (172.21.0.2), port 5432 failed: 
FATAL: password authentication failed for user "v2r"
```

### 원인
1. **환경 변수 불일치**: `.env` 파일이 없거나 잘못된 비밀번호 설정
2. **기존 볼륨 문제**: PostgreSQL 컨테이너가 이미 다른 비밀번호로 초기화된 볼륨을 사용 중
3. **환경 변수 미전달**: docker-compose가 `.env` 파일을 읽지 못함

## 해결 방법

### 방법 1: .env 파일 생성 및 확인 (권장)

EC2 서버에서 `.env` 파일을 생성하거나 확인:

```bash
cd ~/V2R
cat .env
```

`.env` 파일이 없거나 잘못된 경우:

```bash
cat > .env << 'EOF'
DB_HOST=postgres
DB_PORT=5432
DB_NAME=v2r
DB_USER=v2r
DB_PASSWORD=v2r_password

AWS_REGION=ap-northeast-2
OPENAI_API_KEY=
EOF
```

### 방법 2: 기존 볼륨 삭제 후 재생성

기존 PostgreSQL 볼륨이 다른 비밀번호로 초기화된 경우:

```bash
# 컨테이너 중지
docker-compose down

# 기존 볼륨 삭제 (주의: 데이터가 모두 삭제됩니다)
docker volume rm v2r_postgres_data

# .env 파일 확인/생성 (방법 1 참고)

# 컨테이너 재시작
docker-compose up -d
```

### 방법 3: 환경 변수 직접 확인

컨테이너 내부에서 환경 변수 확인:

```bash
docker-compose exec app env | grep DB_
```

예상 출력:
```
DB_HOST=postgres
DB_PORT=5432
DB_NAME=v2r
DB_USER=v2r
DB_PASSWORD=v2r_password
```

### 방법 4: docker-compose.yml에서 직접 설정

`.env` 파일 없이 docker-compose.yml에서 직접 설정하려면:

```yaml
environment:
  DB_HOST: postgres
  DB_PORT: 5432
  DB_NAME: v2r
  DB_USER: v2r
  DB_PASSWORD: v2r_password  # 기본값으로 직접 설정
```

## 빠른 해결 (EC2에서 실행)

```bash
# 1. .env 파일 생성
cd ~/V2R
cat > .env << 'EOF'
DB_HOST=postgres
DB_PORT=5432
DB_NAME=v2r
DB_USER=v2r
DB_PASSWORD=v2r_password
AWS_REGION=ap-northeast-2
EOF

# 2. 기존 컨테이너 및 볼륨 삭제
docker-compose down -v

# 3. 컨테이너 재시작
docker-compose up -d

# 4. 데이터베이스 연결 확인
docker-compose exec app python -c "from src.database.connection import get_db; db = get_db(); print('DB connected!')"
```

## 확인 사항

1. **.env 파일 위치**: 프로젝트 루트 디렉토리 (`~/V2R/.env`)
2. **docker-compose.yml 위치**: `.env` 파일과 같은 디렉토리
3. **볼륨 상태**: `docker volume ls`로 볼륨 확인
4. **컨테이너 로그**: `docker-compose logs postgres`로 PostgreSQL 로그 확인

## 예방 방법

1. `.env.example` 파일을 프로젝트에 포함
2. `.env` 파일을 `.gitignore`에 추가 (보안)
3. 배포 스크립트에서 `.env` 파일 생성 자동화

