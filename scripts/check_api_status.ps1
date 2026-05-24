param(
    [string]$Url = "http://127.0.0.1:8000/api/status",
    [int]$TimeoutSec = 120
)

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

Write-Host "[background] Vérification de l'endpoint $Url" -ForegroundColor Yellow
if (Wait-ForHttp -url $Url -timeoutSec $TimeoutSec) {
    Write-Host "[background] OK: $Url répond." -ForegroundColor Green
    exit 0
}
Write-Host "[background] WARN: $Url n'a pas répondu après $TimeoutSec secondes." -ForegroundColor Yellow
exit 1
