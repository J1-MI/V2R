# EC2 서버 배포 스크립트 (PowerShell)
# 사용법: .\deploy_to_ec2.ps1 -EC2IP "1.2.3.4" -KeyFile "C:\path\to\key.pem" -User "ubuntu"

param(
    [Parameter(Mandatory=$true)]
    [string]$EC2IP,
    
    [Parameter(Mandatory=$true)]
    [string]$KeyFile,
    
    [Parameter(Mandatory=$false)]
    [string]$User = "ubuntu"
)

if (-not (Test-Path $KeyFile)) {
    Write-Host "Error: Key file not found: $KeyFile" -ForegroundColor Red
    exit 1
}

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "V2R EC2 배포 스크립트" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "EC2 IP: $EC2IP"
Write-Host "User: $User"
Write-Host "Key File: $KeyFile"
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 프로젝트 루트 확인
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)

Write-Host "1. 프로젝트 파일 압축 중..." -ForegroundColor Yellow
$TempFile = [System.IO.Path]::GetTempFileName() + ".tar.gz"

# 7-Zip 또는 tar 사용 (Windows 10 이상에는 tar 내장)
$ExcludeItems = @('venv', '__pycache__', '.git', '*.pyc', 'evidence', 'reports', '.env')
$ExcludeArgs = $ExcludeItems | ForEach-Object { "--exclude=$_" }

# tar 명령어 실행 (Windows 10+)
Push-Location $ProjectRoot
try {
    & tar -czf $TempFile @ExcludeArgs .
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: tar 명령어 실패. 7-Zip을 사용하거나 수동으로 압축하세요." -ForegroundColor Red
        exit 1
    }
} finally {
    Pop-Location
}

Write-Host "2. EC2 서버로 파일 전송 중..." -ForegroundColor Yellow
# SCP를 사용한 파일 전송 (WSL 또는 Git Bash 필요)
$SCPCommand = "scp -i `"$KeyFile`" `"$TempFile`" ${User}@${EC2IP}:/tmp/v2r_deploy.tar.gz"
Write-Host "실행할 명령어: $SCPCommand" -ForegroundColor Gray

# WSL 또는 Git Bash에서 실행
if (Get-Command wsl -ErrorAction SilentlyContinue) {
    wsl bash -c "scp -i `"$KeyFile`" `"$TempFile`" ${User}@${EC2IP}:/tmp/v2r_deploy.tar.gz"
} elseif (Get-Command bash -ErrorAction SilentlyContinue) {
    bash -c "scp -i `"$KeyFile`" `"$TempFile`" ${User}@${EC2IP}:/tmp/v2r_deploy.tar.gz"
} else {
    Write-Host "⚠️  SCP를 사용할 수 없습니다. 다음 중 하나를 설치하세요:" -ForegroundColor Yellow
    Write-Host "   - WSL (Windows Subsystem for Linux)" -ForegroundColor Yellow
    Write-Host "   - Git Bash" -ForegroundColor Yellow
    Write-Host "   - WinSCP (GUI 도구)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "또는 수동으로 파일을 전송하세요:" -ForegroundColor Yellow
    Write-Host "   파일 위치: $TempFile" -ForegroundColor Gray
    exit 1
}

Write-Host "3. EC2 서버에서 배포 실행 중..." -ForegroundColor Yellow
$SSHCommand = @"
    mkdir -p ~/V2R
    cd ~/V2R
    if [ -d "V2R" ]; then
        mv V2R V2R.backup.`$(date +%Y%m%d_%H%M%S)
    fi
    tar -xzf /tmp/v2r_deploy.tar.gz
    rm /tmp/v2r_deploy.tar.gz
    echo '배포 완료!'
    echo '다음 단계:'
    echo '1. .env 파일 설정: cd ~/V2R && nano .env'
    echo '2. Docker Compose 실행: docker-compose up -d'
"@

if (Get-Command wsl -ErrorAction SilentlyContinue) {
    wsl bash -c "ssh -i `"$KeyFile`" ${User}@${EC2IP} `"$SSHCommand`""
} elseif (Get-Command bash -ErrorAction SilentlyContinue) {
    bash -c "ssh -i `"$KeyFile`" ${User}@${EC2IP} `"$SSHCommand`""
} else {
    Write-Host "⚠️  SSH를 사용할 수 없습니다. WSL 또는 Git Bash를 설치하세요." -ForegroundColor Yellow
}

# 임시 파일 삭제
Remove-Item $TempFile -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "배포 스크립트 실행 완료!" -ForegroundColor Green
Write-Host "EC2 서버에 접속하여 추가 설정을 진행하세요." -ForegroundColor Green

