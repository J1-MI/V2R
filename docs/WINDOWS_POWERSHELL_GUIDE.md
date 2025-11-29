# Windows PowerShell 사용 가이드

## PowerShell 명령어 작성 방법

### 줄바꿈 문제

PowerShell에서는 백슬래시(`\`)로 줄바꿈을 하면 안 됩니다. 대신 백틱(`` ` ``)을 사용하거나 한 줄로 작성하세요.

### ❌ 잘못된 방법

```powershell
# 백슬래시 사용 (작동하지 않음)
docker-compose exec app python scripts/test/run_full_test.py \
  --scan-target http://dvwa:80
```

### ✅ 올바른 방법

#### 방법 1: 백틱 사용

```powershell
docker-compose exec app python scripts/test/run_full_test.py `
  --scan-target http://dvwa:80
```

#### 방법 2: 한 줄로 작성

```powershell
docker-compose exec app python scripts/test/run_full_test.py --scan-target http://dvwa:80
```

#### 방법 3: 변수 사용

```powershell
$target = "http://dvwa:80"
docker-compose exec app python scripts/test/run_full_test.py --scan-target $target
```

## 포트 충돌 문제

### 포트 80이 이미 사용 중인 경우

Windows에서 포트 80은 종종 다른 서비스(예: IIS, Skype)에서 사용 중입니다.

### 해결 방법

#### 1. DVWA 포트 변경 (권장)

`docker-compose.yml`에서 DVWA 포트를 8080으로 변경했습니다:

```yaml
dvwa:
  ports:
    - "0.0.0.0:8080:80"  # 호스트 포트 8080, 컨테이너 포트 80
```

이제 DVWA는 `http://localhost:8080`으로 접속합니다.

#### 2. 포트 80 사용 중인 프로세스 확인

```powershell
# 포트 80 사용 중인 프로세스 확인
netstat -ano | findstr :80

# 프로세스 ID로 프로세스 확인
tasklist | findstr <PID>
```

#### 3. 포트 80 사용 중인 서비스 중지 (선택사항)

```powershell
# IIS 중지 (관리자 권한 필요)
Stop-Service W3SVC

# 또는 서비스 관리자에서 "World Wide Web Publishing Service" 중지
```

## DVWA 실행 및 접속

### 실행

```powershell
# DVWA 실행 (포트 8080 사용)
docker-compose --profile test up -d dvwa

# 상태 확인
docker-compose ps dvwa
```

### 접속

- 로컬: `http://localhost:8080`
- EC2에서: `http://<로컬PC-공인IP>:8080`

### 기본 계정

- ID: `admin`
- Password: `password`

## 테스트 실행 예시

### 로컬 PC에서 DVWA 스캔

```powershell
# 방법 1: 한 줄로
docker-compose exec app python scripts/test/run_full_test.py --scan-target http://dvwa:80

# 방법 2: 백틱 사용
docker-compose exec app python scripts/test/run_full_test.py `
  --scan-target http://dvwa:80

# 방법 3: 변수 사용
$target = "http://dvwa:80"
docker-compose exec app python scripts/test/run_full_test.py --scan-target $target
```

### 외부 IP로 스캔 (EC2에서 접속 시)

```powershell
# 로컬 PC에서 실행
docker-compose exec app python scripts/test/run_full_test.py --scan-target http://122.39.191.139:8080
```

## 일반적인 PowerShell 팁

### 1. 환경 변수 설정

```powershell
# PowerShell에서
$env:DB_HOST = "localhost"
$env:DB_PORT = "5432"

# 확인
echo $env:DB_HOST
```

### 2. 여러 명령어 실행

```powershell
# 세미콜론으로 구분
docker-compose up -d; docker-compose ps

# 또는 줄바꿈 (Enter 키)
docker-compose up -d
docker-compose ps
```

### 3. 출력 리다이렉션

```powershell
# 파일로 저장
docker-compose logs app > app.log

# 추가 모드
docker-compose logs app >> app.log
```

### 4. 조건부 실행

```powershell
# 이전 명령어 성공 시에만 실행
docker-compose up -d; if ($?) { docker-compose ps }
```

## 문제 해결

### 명령어 인식 오류

```powershell
# PowerShell에서 백슬래시가 인식되지 않음
# 해결: 백틱 사용 또는 한 줄로 작성
```

### 포트 바인딩 오류

```powershell
# Error: ports are not available
# 해결: docker-compose.yml에서 포트 변경 또는 기존 서비스 중지
```

### 컨테이너 이름 충돌

```powershell
# 기존 컨테이너 제거 후 재시작
docker-compose down
docker-compose --profile test up -d dvwa
```

## 참고

- PowerShell은 Linux/Mac의 bash와 다른 문법을 사용합니다
- 줄바꿈: bash는 `\`, PowerShell은 `` ` ``
- 환경 변수: bash는 `$VAR`, PowerShell은 `$env:VAR`
- 경로 구분자: bash는 `/`, PowerShell은 `\` 또는 `/` (둘 다 가능)



