# ============================================
#  MOT-X OS - Lancement Automatique
# ============================================
# Double-cliquez sur ce fichier ou lancez-le
# dans PowerShell pour demarrer l'application.
# ============================================

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   MOT-X OS - Demarrage en cours..." -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Se placer dans le bon dossier
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir

function Stop-MOTXProcesses {
    $patterns = @('src\.motx_os_bridge\.main','uvicorn motx_os_bridge.api.server_v2:app','uvicorn motx_os_bridge.api.fastapi_server:app','src\.motx_os_bridge\.ui\.native_launcher','npm run dev','ollama')
    $procs = Get-CimInstance Win32_Process | Where-Object {
        $cmd = $_.CommandLine
        $cmd -and (($patterns | ForEach-Object { $cmd -match $_ }) -contains $true)
    }
    foreach ($proc in $procs) {
        try {
            Stop-Process -Id $proc.ProcessId -Force -ErrorAction Stop
        } catch {
        }
    }
}

function Start-Ollama {
    $ollamaPort = 11434
    Write-Host "[0/3] Demarrage d'Ollama..." -ForegroundColor Yellow

    $ollamaPullLog = Join-Path $projectRoot "logs\ollama_pull.log"
    $ollamaServeLog = Join-Path $projectRoot "logs\ollama_serve.log"
    $ollamaErr = Join-Path $projectRoot "logs\ollama_err.log"
    New-Item -ItemType Directory -Path (Split-Path $ollamaPullLog) -Force | Out-Null
    if (Test-Path $ollamaPullLog) { Remove-Item $ollamaPullLog -Force }
    if (Test-Path $ollamaServeLog) { Remove-Item $ollamaServeLog -Force }
    if (Test-Path $ollamaErr) { Remove-Item $ollamaErr -Force }

    Write-Host "   Vérification de la présence du modèle llama2..." -ForegroundColor Yellow
    $needPull = $true
    try {
        $modelsOutput = & ollama list 2>&1
        if ($modelsOutput -and ($modelsOutput -match 'llama2')) {
            Write-Host "   Modèle llama2 déjà présent, saut du pull." -ForegroundColor Green
            $needPull = $false
        }
    } catch {
        # Si la commande échoue, on tombera sur le pull
        $needPull = $true
    }

    if ($needPull) {
        Write-Host "   Pull du modèle llama2..." -ForegroundColor Yellow
        $pullProcess = Start-Process -FilePath "ollama" -ArgumentList @("pull","llama2") -WorkingDirectory $projectRoot -RedirectStandardOutput $ollamaPullLog -RedirectStandardError $ollamaErr -NoNewWindow -Wait -PassThru
        if ($pullProcess.ExitCode -ne 0) {
            Write-Host "   ERREUR : impossible de télécharger le modèle Ollama." -ForegroundColor Red
            Write-Host "   Voir $ollamaErr" -ForegroundColor Red
            exit 1
        }
    }

    Write-Host "   Démarrage du serveur Ollama..." -ForegroundColor Yellow
    $ollama = Start-Process -FilePath "ollama" -ArgumentList @("serve","--port","$ollamaPort") -WorkingDirectory $projectRoot -RedirectStandardOutput $ollamaServeLog -RedirectStandardError $ollamaErr -PassThru -WindowStyle Normal

    Write-Host "   Ollama PID: $($ollama.Id)" -ForegroundColor Yellow
    Write-Host "   Vérification d'Ollama sur http://127.0.0.1:$ollamaPort ..." -ForegroundColor Yellow
    if (-not (Wait-ForPort -hostname "127.0.0.1" -port $ollamaPort -timeoutSec 120)) {
        Write-Host "   ERREUR : Ollama n'est pas accessible sur http://127.0.0.1:$ollamaPort" -ForegroundColor Red
        if ($ollama) { Stop-Process -Id $ollama.Id -Force -ErrorAction SilentlyContinue }
        exit 1
    }
    Write-Host "   Ollama démarré et accessible sur http://127.0.0.1:$ollamaPort (PID: $($ollama.Id))" -ForegroundColor Green
    return $ollama
}

function Stop-ListeningOnPort($port) {
    $lines = netstat -ano | findstr ":$port"
    foreach ($line in $lines) {
        if ($line -match 'LISTENING') {
            $portProcessId = ($line.Trim() -split '\s+')[-1]
            if ($portProcessId -and $portProcessId -match '^[0-9]+$') {
                try {
                    Stop-Process -Id [int]$portProcessId -Force -ErrorAction Stop
                } catch {
                }
            }
        }
    }
}

function Wait-ForPort($hostname, $port, $timeoutSec = 120) {
    $deadline = [DateTime]::UtcNow.AddSeconds($timeoutSec)
    while ([DateTime]::UtcNow -lt $deadline) {
        try {
            $result = Test-NetConnection -ComputerName $hostname -Port $port -WarningAction SilentlyContinue
            if ($result.TcpTestSucceeded) {
                return $true
            }
        } catch {
        }
        Start-Sleep -Seconds 1
    }
    return $false
}

function Wait-ForHttp($url, $timeoutSec = 120) {
    $deadline = [DateTime]::UtcNow.AddSeconds($timeoutSec)
    while ([DateTime]::UtcNow -lt $deadline) {
        try {
            $response = Invoke-WebRequest -Uri $url -UseBasicParsing -Method Get -TimeoutSec 10 -ErrorAction Stop
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 300) {
                return $true
            }
        } catch {
        }
        Start-Sleep -Seconds 1
    }
    return $false
}

Stop-MOTXProcesses
Stop-ListeningOnPort 11434
Stop-ListeningOnPort 8000
Stop-ListeningOnPort 5173
Start-Sleep -Seconds 2
$ollama = Start-Ollama

# 1. Demarrer le Backend (FastAPI + Moteur Cognitif)
Write-Host "[1/2] Demarrage du Backend..." -ForegroundColor Yellow
$env:PYTHONPATH = Join-Path $projectRoot "src"
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"
$backendPort = 8000
$backendLog = Join-Path $projectRoot "logs\backend_start.log"
$backendErr = Join-Path $projectRoot "logs\backend_start.err"
New-Item -ItemType Directory -Path (Split-Path $backendLog) -Force | Out-Null
if (Test-Path $backendLog) { Remove-Item $backendLog -Force -ErrorAction SilentlyContinue }
if (Test-Path $backendErr) { Remove-Item $backendErr -Force -ErrorAction SilentlyContinue }
$backendExe = Join-Path $projectRoot ".venv\Scripts\python.exe"
$backendArgs = @(
    "-m",
    "uvicorn",
    "motx_os_bridge.api.server_v2:app",
    "--host",
    "127.0.0.1",
    "--port",
    "$backendPort",
    "--log-level",
    "info"
)
Write-Host "   Backend log: $backendLog" -ForegroundColor Yellow
Write-Host "   Backend err: $backendErr" -ForegroundColor Yellow
$backend = Start-Process -FilePath $backendExe `
    -ArgumentList $backendArgs `
    -WorkingDirectory $projectRoot `
    -RedirectStandardOutput $backendLog `
    -RedirectStandardError $backendErr `
    -PassThru -WindowStyle Normal
Write-Host "   Backend PID: $($backend.Id)" -ForegroundColor Yellow

Write-Host "   Vérification du backend FastAPI sur http://127.0.0.1:$backendPort ..." -ForegroundColor Yellow
if (-not (Wait-ForPort -hostname "127.0.0.1" -port $backendPort -timeoutSec 120)) {
    Write-Host "   ERREUR : le backend FastAPI n'est pas accessible sur http://127.0.0.1:$backendPort" -ForegroundColor Red
    if ($backend) { Stop-Process -Id $backend.Id -Force -ErrorAction SilentlyContinue }
    exit 1
}
Write-Host "   Backend socket ouvert sur http://127.0.0.1:$backendPort" -ForegroundColor Green

$backendStatusMonitorOut = Join-Path $projectRoot "logs\backend_status_check.out"
$backendStatusMonitorErr = Join-Path $projectRoot "logs\backend_status_check.err"
$backendStatusMonitorScript = Join-Path $projectRoot "scripts\check_api_status.ps1"
Get-Content -Path "logs\frontend_start.log" -Wait -Tail 50 = Start-Process -FilePath "powershell.exe" `
    -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "$backendStatusMonitorScript", "-Url", "http://127.0.0.1:$backendPort/api/status", "-TimeoutSec", "120" `
    -WorkingDirectory $projectRoot `
    -RedirectStandardOutput $backendStatusMonitorOut `
    -RedirectStandardError $backendStatusMonitorErr `
    -PassThru -WindowStyle Hidden
Write-Host "   Vérification de /api/status en arrière-plan (logs: $backendStatusMonitorOut, $backendStatusMonitorErr)" -ForegroundColor Yellow

# 2. Demarrer le Frontend (React)
Write-Host "[2/2] Demarrage du Frontend..." -ForegroundColor Yellow
$frontendPort = 5173
$frontendLog = Join-Path $projectRoot "logs\frontend_start.log"
$frontendErr = Join-Path $projectRoot "logs\frontend_start.err"
New-Item -ItemType Directory -Path (Split-Path $frontendLog) -Force | Out-Null
if (Test-Path $frontendLog) { Remove-Item $frontendLog -Force -ErrorAction SilentlyContinue }
if (Test-Path $frontendErr) { Remove-Item $frontendErr -Force -ErrorAction SilentlyContinue }
$frontendCommand = "cd /d `"$projectRoot\motx-frontend`" && npm run dev -- --host 127.0.0.1 --port $frontendPort --strictPort > `"$frontendLog`" 2> `"$frontendErr`""
Write-Host "   Frontend log: $frontendLog" -ForegroundColor Yellow
Write-Host "   Frontend err: $frontendErr" -ForegroundColor Yellow
$frontend = Start-Process -FilePath "cmd.exe" `
    -ArgumentList "/c", $frontendCommand `
    -WorkingDirectory $projectRoot `
    -PassThru -WindowStyle Normal
Write-Host "   Frontend PID: $($frontend.Id)" -ForegroundColor Yellow

Write-Host "   Vérification du frontend sur http://127.0.0.1:$frontendPort ..." -ForegroundColor Yellow
if (-not (Wait-ForPort -hostname "127.0.0.1" -port $frontendPort -timeoutSec 120)) {
    Write-Host "   ERREUR : le frontend n'est pas accessible sur http://127.0.0.1:$frontendPort" -ForegroundColor Red
    if ($frontend) { Stop-Process -Id $frontend.Id -Force -ErrorAction SilentlyContinue }
    if ($backend) { Stop-Process -Id $backend.Id -Force -ErrorAction SilentlyContinue }
    exit 1
}
Write-Host "   Frontend démarré et accessible sur http://127.0.0.1:$frontendPort (PID: $($frontend.Id))" -ForegroundColor Green

# 3. Demarrer l'UI Native de bureau (PyWebView)
Write-Host "[3/3] Demarrage de l'UI Native de bureau..." -ForegroundColor Yellow
$ui = Start-Process -FilePath "$projectRoot\.venv\Scripts\python.exe" `
    -ArgumentList "-m", "src.motx_os_bridge.ui.native_launcher" `
    -WorkingDirectory $projectRoot `
    -PassThru -WindowStyle Normal

Start-Sleep -Seconds 2
Write-Host "   UI Native demarree (PID: $($ui.Id))" -ForegroundColor Green

Write-Host "Fermez la fenetre native de l'application MOT-X OS pour l'arreter..." -ForegroundColor Yellow
$ui.WaitForExit()
 
# Arreter proprement
Write-Host ""
Write-Host "============================================" -ForegroundColor Red
Write-Host "   Arret en cours de tous les processus..." -ForegroundColor Red
Write-Host "============================================" -ForegroundColor Red
Stop-Process -Id $backend.Id -Force -ErrorAction SilentlyContinue
Stop-Process -Id $frontend.Id -Force -ErrorAction SilentlyContinue
Stop-Process -Id $ui.Id -Force -ErrorAction SilentlyContinue
Write-Host "MOT-X OS est arrete. Au revoir!" -ForegroundColor Cyan
