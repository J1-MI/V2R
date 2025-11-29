# Docker 소켓 접근 확인 스크립트
# Windows PowerShell용

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Docker 소켓 접근 확인" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Docker Desktop 실행 확인
Write-Host "[1/4] Docker Desktop 실행 확인..." -ForegroundColor Yellow
$dockerRunning = docker ps 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Docker Desktop이 실행 중입니다" -ForegroundColor Green
} else {
    Write-Host "❌ Docker Desktop이 실행되지 않았습니다" -ForegroundColor Red
    Write-Host "Docker Desktop을 시작해주세요." -ForegroundColor Yellow
    exit 1
}

# 컨테이너 내부에서 Docker 소켓 확인
Write-Host ""
Write-Host "[2/4] 컨테이너 내부 Docker 소켓 확인..." -ForegroundColor Yellow
$socketCheck = docker exec v2r-app ls -la /var/run/docker.sock 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Docker 소켓이 마운트되어 있습니다" -ForegroundColor Green
    Write-Host $socketCheck -ForegroundColor Gray
} else {
    Write-Host "❌ Docker 소켓이 마운트되지 않았습니다" -ForegroundColor Red
    Write-Host "docker-compose.yml에서 Docker 소켓 마운트를 확인하세요." -ForegroundColor Yellow
}

# 컨테이너 내부에서 Docker 명령어 테스트 (선택사항)
Write-Host ""
Write-Host "[3/4] 컨테이너 내부에서 Docker CLI 확인..." -ForegroundColor Yellow
$dockerCliCheck = docker exec v2r-app which docker 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Docker CLI가 설치되어 있습니다" -ForegroundColor Green
    $dockerTest = docker exec v2r-app docker ps 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Docker 명령어 실행 성공" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Docker CLI는 있지만 실행 실패 (Python 클라이언트는 작동합니다)" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  Docker CLI가 설치되지 않았습니다 (Python 클라이언트는 작동합니다)" -ForegroundColor Yellow
    Write-Host "   Docker CLI는 선택사항이며, Python docker 라이브러리로 충분합니다." -ForegroundColor Gray
}

# Python에서 Docker 클라이언트 테스트
Write-Host ""
Write-Host "[4/4] Python Docker 클라이언트 테스트..." -ForegroundColor Yellow
$pythonTest = docker exec v2r-app python -c "import docker; c = docker.from_env(); c.ping(); print('OK')" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Python Docker 클라이언트 연결 성공" -ForegroundColor Green
} else {
    Write-Host "❌ Python Docker 클라이언트 연결 실패" -ForegroundColor Red
    Write-Host "오류: $pythonTest" -ForegroundColor Gray
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "확인 완료" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 해결 방법 안내
if ($LASTEXITCODE -ne 0) {
    Write-Host "💡 해결 방법:" -ForegroundColor Yellow
    Write-Host "1. Docker Desktop 재시작" -ForegroundColor White
    Write-Host "2. docker-compose down && docker-compose up -d" -ForegroundColor White
    Write-Host "3. Docker Desktop Settings → General → WSL 2 확인" -ForegroundColor White
    Write-Host ""
}

