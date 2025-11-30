# EC2 배포 빠른 테스트 스크립트 (Windows PowerShell)
# EC2 서버에서 실행

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "V2R 빠른 테스트 스크립트" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 서비스 상태 확인
Write-Host "1. Docker 서비스 상태 확인..." -ForegroundColor Yellow
docker-compose ps

# 2. API 서버 확인
Write-Host ""
Write-Host "2. API 서버 확인..." -ForegroundColor Yellow
try {
    $apiResponse = Invoke-RestMethod -Uri "http://localhost:5000/api/agents" -Method Get
    Write-Host "응답: $($apiResponse | ConvertTo-Json)" -ForegroundColor Gray
    if ($apiResponse.success) {
        Write-Host "✅ API 서버 정상 동작" -ForegroundColor Green
    } else {
        Write-Host "❌ API 서버 오류" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ API 서버 연결 실패: $_" -ForegroundColor Red
    Write-Host "로그 확인: docker-compose logs api" -ForegroundColor Yellow
    exit 1
}

# 3. 데이터베이스 확인
Write-Host ""
Write-Host "3. 데이터베이스 테이블 확인..." -ForegroundColor Yellow
$tables = docker exec v2r-postgres psql -U v2r -d v2r -c "\dt" 2>&1
if ($tables -match "agents|agent_tasks") {
    Write-Host "✅ 테이블 존재 확인" -ForegroundColor Green
} else {
    Write-Host "⚠️  테이블이 없을 수 있습니다. init_db.py를 실행하세요." -ForegroundColor Yellow
}

# 4. Agent 등록 확인
Write-Host ""
Write-Host "4. 등록된 Agent 확인..." -ForegroundColor Yellow
$agentCount = if ($apiResponse.agents) { $apiResponse.agents.Count } else { 0 }
Write-Host "등록된 Agent 수: $agentCount" -ForegroundColor Cyan

# 5. Streamlit 대시보드 확인
Write-Host ""
Write-Host "5. Streamlit 대시보드 확인..." -ForegroundColor Yellow
$streamlitProcess = docker exec v2r-app ps aux 2>&1 | Select-String "streamlit"
if ($streamlitProcess) {
    Write-Host "✅ Streamlit 대시보드 실행 중" -ForegroundColor Green
} else {
    Write-Host "⚠️  Streamlit 대시보드가 실행되지 않았습니다." -ForegroundColor Yellow
    Write-Host "실행: docker exec -d v2r-app streamlit run src/dashboard/app.py --server.port 8501 --server.address 0.0.0.0" -ForegroundColor Gray
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "테스트 완료" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "다음 단계:" -ForegroundColor Yellow
Write-Host "1. 로컬 PC에서 Agent 실행" -ForegroundColor White
Write-Host "2. 브라우저에서 http://EC2-IP:8501 접속" -ForegroundColor White
Write-Host "3. 'Agent & Local Scanner' 페이지에서 작업 생성" -ForegroundColor White
Write-Host "==========================================" -ForegroundColor Cyan

