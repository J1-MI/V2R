# CVE-Lab 전체 서비스 스캔 스크립트 (통합 버전)
# 사용법: .\scripts\scan_cve_lab.ps1

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "CVE-Lab 전체 스캔 시작" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# V2R 프로젝트 디렉토리 확인
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "❌ 오류: docker-compose.yml 파일을 찾을 수 없습니다." -ForegroundColor Red
    Write-Host "V2R 프로젝트 루트 디렉토리에서 실행해주세요." -ForegroundColor Red
    exit 1
}

# Docker 컨테이너 확인
Write-Host "🔍 CVE-Lab 컨테이너 확인 중..." -ForegroundColor Yellow
$cveLabContainers = docker ps --format "{{.Names}}" | Select-String "cve-lab"
if (-not $cveLabContainers) {
    Write-Host "⚠️  경고: CVE-Lab 컨테이너를 찾을 수 없습니다." -ForegroundColor Yellow
    Write-Host "CVE-Lab 프로젝트를 먼저 실행해주세요." -ForegroundColor Yellow
    Write-Host ""
}

# 통합 스캔 스크립트 실행
Write-Host ""
Write-Host "🚀 통합 스캔 스크립트 실행" -ForegroundColor Green
Write-Host ""

# DB 리셋 옵션 확인
$resetDb = Read-Host "데이터베이스를 리셋하시겠습니까? (y/N)"
if ($resetDb -eq "y" -or $resetDb -eq "Y") {
    Write-Host "데이터베이스 리셋 중..." -ForegroundColor Yellow
    docker exec v2r-app python scripts/utils/reset_db.py
    Write-Host ""
}

docker exec v2r-app python scripts/test/scan_cve_lab_full.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ CVE-Lab 전체 스캔 완료" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "❌ CVE-Lab 스캔 실패" -ForegroundColor Red
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "📊 대시보드에서 결과 확인:" -ForegroundColor Yellow
Write-Host "  docker-compose exec app streamlit run src/dashboard/app.py" -ForegroundColor Gray
Write-Host ""

