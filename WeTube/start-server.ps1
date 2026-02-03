# WeTube 서버 시작 – 5000 포트 정리 후 실행
# 사용: .\start-server.ps1
# 404 나오면: 기존 Flask 터미널에서 Ctrl+C 후 이 스크립트만 실행하세요.

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

# 5000 포트 사용 프로세스 종료
try {
    $conn = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue
    if ($conn) {
        $pids = $conn.OwningProcess | Sort-Object -Unique
        foreach ($pid in $pids) {
            Write-Host "5000 포트 사용 프로세스 종료: PID $pid"
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        }
        Start-Sleep -Seconds 2
    }
} catch {
    $line = netstat -ano | Select-String "LISTENING" | Select-String ":5000 "
    if ($line) {
        $parts = $line -split '\s+'
        $pid = $parts[-1]
        if ($pid -match '^\d+$') {
            Write-Host "5000 포트 사용 프로세스 종료: PID $pid"
            taskkill /F /PID $pid 2>$null
            Start-Sleep -Seconds 2
        }
    }
}

Set-ExecutionPolicy Bypass -Scope Process -Force
& .\venv\Scripts\Activate.ps1
python -m app
