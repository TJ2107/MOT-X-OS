$endpoints = @(
    @{ name = "Health Status"; method = "GET"; url = "http://127.0.0.1:8000/api/status" },
    @{ name = "Analytics Dashboard"; method = "GET"; url = "http://127.0.0.1:8000/api/analytics/dashboard" },
    @{ name = "Cognitive State Detection"; method = "POST"; url = "http://127.0.0.1:8000/api/cognitive/state"; body = @{ apps = @("visual studio code", "powershell") } },
    @{ name = "Demo Magic Sequence"; method = "GET"; url = "http://127.0.0.1:8000/api/demo/magic" },
    @{ name = "Eye Tracking Status"; method = "GET"; url = "http://127.0.0.1:8000/api/eye/status" },
    @{ name = "Voice Engine Status"; method = "GET"; url = "http://127.0.0.1:8000/api/voice/status" },
    @{ name = "Shadow Mode Start"; method = "POST"; url = "http://127.0.0.1:8000/api/shadow/start" },
    @{ name = "Shadow Mode Stop"; method = "POST"; url = "http://127.0.0.1:8000/api/shadow/stop" }
)

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "   MOT-X OS - INTEGRAL API SYSTEM TEST REPORT" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan

foreach ($ep in $endpoints) {
    Write-Host "Testing: $($ep.name) ... " -NoNewline
    try {
        $params = @{ Uri = $ep.url; Method = $ep.method; TimeoutSec = 30 }
        if ($ep.body) {
            $params.Body = ($ep.body | ConvertTo-Json)
            $params.ContentType = "application/json"
        }
        $res = Invoke-RestMethod @params
        Write-Host "OK" -ForegroundColor Green
        $res | ConvertTo-Json -Depth 4 | Write-Host -ForegroundColor Gray
    } catch {
        Write-Host "FAILED" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
    }
    Write-Host "---------------------------------------------------" -ForegroundColor DarkGray
}
