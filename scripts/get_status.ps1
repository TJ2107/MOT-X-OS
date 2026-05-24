try {
    $r = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/status' -TimeoutSec 60
    $r | ConvertTo-Json -Depth 5
} catch {
    Write-Host 'ERROR'
    Write-Host $_.Exception.Message
    exit 2
}