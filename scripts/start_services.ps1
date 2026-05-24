# start_services.ps1 - Launch backend and frontend for MOT-X OS
# Stop any leftover processes and free ports

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir

# Robustly stop any process listening on a given TCP port
function Stop-ListeningOnPort($port) {
    try {
        $procId = (Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue).OwningProcess
        if ($procId) {
            Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
        }
    } catch {
        # Fallback to netstat parsing if Get-NetTCPConnection unavailable
        $lines = netstat -ano | findstr ":$port"
        foreach ($line in $lines) {
            if ($line -match 'LISTENING\s+(\d+)$') {
                $processId = $matches[1]
                Stop-Process -Id [int]$processId -Force -ErrorAction SilentlyContinue
            }
        }
    }
}

# Ensure ports are free
Stop-ListeningOnPort 8000
Stop-ListeningOnPort 5173

# Start Backend
Write-Host "[Backend] Starting..." -ForegroundColor Yellow
$env:PYTHONPATH = Join-Path $projectRoot "src"
$backendExe = Join-Path $projectRoot ".venv\Scripts\python.exe"
$backendArgs = @('-m','uvicorn','motx_os_bridge.api.fastapi_server:app','--host','127.0.0.1','--port','8000','--log-level','info')
$backend = Start-Process -FilePath $backendExe -ArgumentList $backendArgs -WorkingDirectory $projectRoot -PassThru -WindowStyle Normal
Write-Host "Backend PID: $($backend.Id)" -ForegroundColor Yellow

# Wait for backend to become reachable
Write-Host "Waiting for backend (port 8000) to be ready..." -ForegroundColor Cyan
$deadline = [DateTime]::UtcNow.AddSeconds(120)
while ([DateTime]::UtcNow -lt $deadline) {
    if ((Test-NetConnection -ComputerName 127.0.0.1 -Port 8000 -WarningAction SilentlyContinue).TcpTestSucceeded) { break }
    Start-Sleep -Seconds 2
}
if (-not (Test-NetConnection -ComputerName 127.0.0.1 -Port 8000 -WarningAction SilentlyContinue).TcpTestSucceeded) {
    Write-Host "ERREUR: Backend non accessible apres 120s. Abandon." -ForegroundColor Red
    exit 1
}
Write-Host "Backend is ready." -ForegroundColor Green

# Start Frontend
Write-Host "[Frontend] Starting..." -ForegroundColor Yellow
$frontendCommand = "cd /d `"$projectRoot\motx-frontend`" && npm run dev -- --host 127.0.0.1 --port 5173 --strictPort"
$frontend = Start-Process -FilePath "cmd.exe" -ArgumentList "/c", $frontendCommand -WorkingDirectory $projectRoot -PassThru -WindowStyle Normal
Write-Host "Frontend PID: $($frontend.Id)" -ForegroundColor Yellow

# Wait for frontend to become reachable
Write-Host "Waiting for frontend (port 5173) to be ready..." -ForegroundColor Cyan
$deadline = [DateTime]::UtcNow.AddSeconds(120)
while ([DateTime]::UtcNow -lt $deadline) {
    if ((Test-NetConnection -ComputerName 127.0.0.1 -Port 5173 -WarningAction SilentlyContinue).TcpTestSucceeded) { break }
    Start-Sleep -Seconds 2
}
if (-not (Test-NetConnection -ComputerName 127.0.0.1 -Port 5173 -WarningAction SilentlyContinue).TcpTestSucceeded) {
    Write-Host "ERREUR: Frontend non accessible apres 120s. Abandon." -ForegroundColor Red
    exit 1
}
Write-Host "Frontend is ready." -ForegroundColor Green

# Run API integration test
Write-Host "Running API integration tests..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
& "$projectRoot\scripts\test_api.ps1"

# Script ends; services continue running in background.
