# Script pour relancer le backend FastAPI et mesurer le temps de démarrage
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
Set-Location $projectRoot

function Stop-BackendProcesses {
    $patterns = @('uvicorn','motx_os_bridge.api.fastapi_server','src.motx_os_bridge.main')
    $procs = Get-CimInstance Win32_Process | Where-Object {
        $cmd = $_.CommandLine
        $cmd -and (($patterns | ForEach-Object { $cmd -match $_ }) -contains $true)
    }
    foreach ($proc in $procs) {
        try { Stop-Process -Id $proc.ProcessId -Force -ErrorAction Stop } catch {}
    }
}

function Stop-ListeningOnPort($port) {
    $lines = netstat -ano | findstr ":$port"
    foreach ($line in $lines) {
        if ($line -match 'LISTENING') {
            $portProcessId = ($line.Trim() -split '\s+')[-1]
            if ($portProcessId -and $portProcessId -match '^[0-9]+$') {
                try { Stop-Process -Id [int]$portProcessId -Force -ErrorAction Stop } catch {}
            }
        }
    }
}

function Wait-ForHttp($url, $timeoutSec = 300) {
    $deadline = [DateTime]::UtcNow.AddSeconds($timeoutSec)
    while ([DateTime]::UtcNow -lt $deadline) {
        try {
            $response = Invoke-WebRequest -Uri $url -UseBasicParsing -Method Get -TimeoutSec 10 -ErrorAction Stop
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 300) { return $true }
        } catch {}
        Start-Sleep -Seconds 1
    }
    return $false
}

$logDir = Join-Path $projectRoot "logs"
New-Item -ItemType Directory -Path $logDir -Force | Out-Null
$backendLog = Join-Path $logDir "backend_start_measure.log"
$backendErr = Join-Path $logDir "backend_start_measure.err"
if (Test-Path $backendLog) { Remove-Item $backendLog -Force }
if (Test-Path $backendErr) { Remove-Item $backendErr -Force }

Write-Host "Stopping backend processes..." -ForegroundColor Yellow
Stop-BackendProcesses
Stop-ListeningOnPort 8000
Start-Sleep -Seconds 1

$backendExe = Join-Path $projectRoot ".venv\Scripts\python.exe"
$backendArgs = @(
    "-m",
    "uvicorn",
    "motx_os_bridge.api.fastapi_server:app",
    "--host",
    "127.0.0.1",
    "--port",
    "8000",
    "--log-level",
    "info"
)
Write-Host "Starting backend with $backendExe ..." -ForegroundColor Yellow
$start = Get-Date
$backend = Start-Process -FilePath $backendExe -ArgumentList $backendArgs -WorkingDirectory $projectRoot -RedirectStandardOutput $backendLog -RedirectStandardError $backendErr -PassThru -WindowStyle Hidden
Write-Host "Backend PID: $($backend.Id)" -ForegroundColor Yellow

$ok = Wait-ForHttp -url "http://127.0.0.1:8000/api/status" -timeoutSec 300
$elapsed = (Get-Date) - $start
if ($ok) {
    Write-Host "OK: /api/status responded in $($elapsed.TotalSeconds) seconds" -ForegroundColor Green
    Write-Host "Logs: $backendLog and $backendErr"
    exit 0
} else {
    Write-Host "ERROR: /api/status did not respond within 300s (elapsed $($elapsed.TotalSeconds)s)" -ForegroundColor Red
    Write-Host "Logs: $backendLog and $backendErr"
    exit 2
}