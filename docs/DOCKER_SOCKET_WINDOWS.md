# Windows Docker 소켓 접근 문제 해결 가이드

## 개요

이 가이드는 Windows 환경에서 Docker 컨테이너 내부에서 호스트의 Docker 소켓에 접근하는 방법과 문제 해결 방법을 설명합니다.

## 현재 상태 확인

### Docker 소켓 마운트 확인

```powershell
# 컨테이너 내부에서 확인
docker exec v2r-app ls -la /var/run/docker.sock

# 예상 출력: srw-rw---- 1 root root
```

✅ **정상 상태**: `/var/run/docker.sock`이 컨테이너에 마운트되어 있고, Python Docker 클라이언트가 정상 작동하면 PoC 재현 기능이 사용 가능합니다.

⚠️ **Docker CLI**: 컨테이너 내부에 `docker` 명령어가 없어도 됩니다. Python `docker` 라이브러리만으로도 모든 기능이 작동합니다.

## 문제 상황

Windows에서 Docker 컨테이너 내부에서 호스트의 Docker 소켓에 접근할 때 다음 오류가 발생할 수 있습니다:

```
Error while fetching server API version: ('Connection aborted.', FileNotFoundError(2, 'No such file or directory'))
```

## 원인

Windows Docker Desktop은 Linux와 다른 방식으로 Docker 소켓을 관리합니다:

1. **WSL2 백엔드**: WSL2 내부의 Linux 환경에서 Docker가 실행됩니다
2. **Hyper-V 백엔드**: Windows의 named pipe를 사용합니다 (`\\.\pipe\docker_engine`)
3. **컨테이너 내부**: Linux 컨테이너 내부에서는 `/var/run/docker.sock` 경로를 기대합니다

## 해결 방법

### 방법 1: Docker Desktop 설정 확인 (권장)

1. **Docker Desktop 실행**
2. **Settings → General**에서 다음 확인:
   - ✅ "Use the WSL 2 based engine" 활성화
   - ✅ "Expose daemon on tcp://localhost:2375 without TLS" (선택사항, 보안 주의)

3. **Settings → Resources → WSL Integration**에서:
   - ✅ "Enable integration with my default WSL distro" 활성화

### 방법 2: docker-compose.yml 확인

`docker-compose.yml`에서 Docker 소켓 마운트가 올바르게 설정되어 있는지 확인:

```yaml
volumes:
  - /var/run/docker.sock:/var/run/docker.sock:ro
```

### 방법 3: Docker Desktop 재시작

Docker Desktop을 완전히 재시작:

```powershell
# Docker Desktop 종료
# 시작 메뉴에서 "Docker Desktop" 재시작

# 또는 PowerShell에서
Stop-Process -Name "Docker Desktop" -Force
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
```

### 방법 4: 컨테이너 재시작

Docker 소켓 마운트를 적용하기 위해 컨테이너를 재시작:

```powershell
docker-compose down
docker-compose up -d
```

### 방법 5: WSL2 내부에서 확인

WSL2를 사용하는 경우, WSL2 내부에서 Docker 소켓 경로 확인:

```bash
# WSL2 터미널에서
ls -la /var/run/docker.sock
```

WSL2 내부에서도 소켓이 없다면 Docker Desktop의 WSL2 통합이 제대로 설정되지 않은 것입니다.

### 방법 6: Docker Desktop TCP 포트 사용 (고급)

보안 주의: 이 방법은 로컬 네트워크에서만 사용하세요.

1. **Docker Desktop Settings → General**:
   - ✅ "Expose daemon on tcp://localhost:2375 without TLS" 활성화

2. **docker-compose.yml 수정**:
   ```yaml
   environment:
     DOCKER_HOST: tcp://host.docker.internal:2375
   ```

3. **src/poc/isolation.py**가 자동으로 `DOCKER_HOST` 환경 변수를 사용합니다.

### 방법 7: Docker-in-Docker (DinD) 사용 (대안)

Docker 소켓 접근이 불가능한 경우, Docker-in-Docker를 사용할 수 있습니다:

```yaml
# docker-compose.yml
app:
  # ...
  volumes:
    - .:/app
    - ./evidence:/app/evidence
    # DinD 사용 (권장하지 않음, 성능 저하)
  # privileged: true  # DinD 사용 시 필요
```

## 확인 방법

컨테이너 내부에서 Docker 접근 확인:

```powershell
# 컨테이너 접속
docker exec -it v2r-app bash

# Docker 소켓 확인
ls -la /var/run/docker.sock

# Docker 명령어 테스트
docker ps
```

## 문제 해결 체크리스트

- [ ] Docker Desktop이 실행 중인가?
- [ ] WSL2 백엔드가 활성화되어 있는가?
- [ ] `docker-compose.yml`에 Docker 소켓 마운트가 있는가?
- [ ] 컨테이너를 재시작했는가?
- [ ] 컨테이너 내부에서 `/var/run/docker.sock` 파일이 존재하는가?
- [ ] 파일 권한이 올바른가? (`ls -la /var/run/docker.sock`)

## Windows 특이사항

### WSL2 백엔드 사용 시

- Docker 소켓은 WSL2 내부의 Linux 환경에 있습니다
- 컨테이너는 WSL2 내부에서 실행되므로 `/var/run/docker.sock`이 정상 작동해야 합니다
- 문제가 있다면 WSL2 통합 설정을 확인하세요

### Hyper-V 백엔드 사용 시

- Windows의 named pipe를 사용하므로 Linux 컨테이너에서 직접 접근이 어렵습니다
- WSL2 백엔드로 전환하는 것을 권장합니다

## 추가 리소스

- [Docker Desktop WSL 2 백엔드](https://docs.docker.com/desktop/wsl/)
- [Docker 소켓 마운트](https://docs.docker.com/engine/reference/commandline/dockerd/#daemon-socket-option)

