# OpenAI API 키 설정 확인 스크립트

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "OpenAI API 키 설정 확인" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 1. .env 파일 확인
Write-Host "[1/4] .env 파일 확인" -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "  ✅ .env 파일 존재" -ForegroundColor Green
    $envContent = Get-Content .env -ErrorAction SilentlyContinue
    $hasKey = $envContent | Select-String "OPENAI_API_KEY"
    if ($hasKey) {
        Write-Host "  ✅ OPENAI_API_KEY 설정됨" -ForegroundColor Green
    } else {
        Write-Host "  ❌ OPENAI_API_KEY 설정 안됨" -ForegroundColor Red
        Write-Host "     .env 파일에 다음을 추가하세요:" -ForegroundColor Yellow
        Write-Host "     OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" -ForegroundColor Gray
    }
} else {
    Write-Host "  ⚠️  .env 파일 없음" -ForegroundColor Yellow
    Write-Host "     .env 파일을 생성하고 OPENAI_API_KEY를 설정하세요" -ForegroundColor Yellow
}
Write-Host ""

# 2. Docker 환경 변수 확인
Write-Host "[2/4] Docker 컨테이너 환경 변수 확인" -ForegroundColor Yellow
$dockerEnv = docker-compose exec -T app env 2>$null | Select-String "OPENAI_API_KEY"
if ($dockerEnv) {
    $keyValue = $dockerEnv -replace "OPENAI_API_KEY=", ""
    if ($keyValue -and $keyValue -ne "") {
        $keyLength = $keyValue.Length
        $maskedKey = $keyValue.Substring(0, [Math]::Min(7, $keyLength)) + "..." + $keyValue.Substring([Math]::Max(0, $keyLength - 4))
        Write-Host "  ✅ OPENAI_API_KEY 설정됨: $maskedKey" -ForegroundColor Green
    } else {
        Write-Host "  ❌ OPENAI_API_KEY가 비어있음" -ForegroundColor Red
    }
} else {
    Write-Host "  ❌ OPENAI_API_KEY 환경 변수 없음" -ForegroundColor Red
}
Write-Host ""

# 3. Python 코드에서 확인
Write-Host "[3/4] Python 코드에서 확인" -ForegroundColor Yellow
$pythonCheck = @"
from src.config import OPENAI_API_KEY
if OPENAI_API_KEY:
    print('OK: ' + str(len(OPENAI_API_KEY)) + ' chars')
else:
    print('ERROR: Not set')
"@

$result = docker-compose exec -T app python -c $pythonCheck 2>&1
if ($result -match "OK:") {
    Write-Host "  ✅ Python에서 API 키 인식됨" -ForegroundColor Green
} else {
    Write-Host "  ❌ Python에서 API 키 인식 안됨" -ForegroundColor Red
}
Write-Host ""

# 4. LLM 클라이언트 초기화 확인
Write-Host "[4/4] LLM 클라이언트 초기화 확인" -ForegroundColor Yellow
$llmCheck = @"
from src.llm.report_generator import LLMReportGenerator
generator = LLMReportGenerator()
if generator.client:
    print('OK: Client initialized')
else:
    print('ERROR: Client not initialized')
"@

$llmResult = docker-compose exec -T app python -c $llmCheck 2>&1
if ($llmResult -match "OK:") {
    Write-Host "  ✅ OpenAI 클라이언트 초기화 성공" -ForegroundColor Green
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "✅ GPT 연동 정상 작동 중" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Cyan
} else {
    Write-Host "  ❌ OpenAI 클라이언트 초기화 실패" -ForegroundColor Red
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "❌ GPT 연동 실패 - API 키 설정 필요" -ForegroundColor Red
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "해결 방법:" -ForegroundColor Yellow
    Write-Host "1. .env 파일에 OPENAI_API_KEY 설정" -ForegroundColor Gray
    Write-Host "2. docker-compose restart app" -ForegroundColor Gray
    Write-Host "3. 자세한 내용: docs/OPENAI_API_SETUP.md" -ForegroundColor Gray
}
Write-Host ""




