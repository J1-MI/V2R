# PowerShell 스크립트: Docker 환경에서 테스트 실행

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "V2R 통합 테스트 실행" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Docker Compose 상태 확인
Write-Host "[1/4] Docker 컨테이너 상태 확인..." -ForegroundColor Yellow
$containers = docker-compose ps
Write-Host $containers
Write-Host ""

# 컨테이너가 실행 중이 아니면 시작
if ($containers -notmatch "Up") {
    Write-Host "[2/4] Docker 컨테이너 시작 중..." -ForegroundColor Yellow
    docker-compose up -d
    Start-Sleep -Seconds 5
} else {
    Write-Host "[2/4] Docker 컨테이너가 이미 실행 중입니다." -ForegroundColor Green
}
Write-Host ""

# 데이터베이스 연결 확인
Write-Host "[3/4] 데이터베이스 연결 확인..." -ForegroundColor Yellow
docker-compose exec -T app python -c "from src.database import get_db; db = get_db(); print('✓ 연결 성공' if db.test_connection() else '✗ 연결 실패')"
Write-Host ""

# 통합 테스트 실행
Write-Host "[4/4] 통합 테스트 실행..." -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
docker-compose exec app python scripts/test/test_integration.py
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "테스트 완료!" -ForegroundColor Green

