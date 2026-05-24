param(
    [string]$RepoName,
    [string]$Description = "MOT-X OS repository created from local workspace",
    [switch]$Private,
    [string]$Owner
)

$token = $env:GITHUB_TOKEN
if (-not $token) {
    Write-Host "ERROR: GITHUB_TOKEN is not set. Set it in PowerShell with:`n  $env:GITHUB_TOKEN = 'YOUR_TOKEN'`" -ForegroundColor Red
    exit 1
}

if (-not $RepoName) {
    $pwdName = (Get-Location).Path | Split-Path -Leaf
    $RepoName = $pwdName -replace ' ', '-' -replace '[^A-Za-z0-9_.-]', ''
    Write-Host "No RepoName provided. Using derived name: $RepoName" -ForegroundColor Yellow
}

$body = @{ name = $RepoName; description = $Description; private = $Private.IsPresent }
$uri = if ($Owner) { "https://api.github.com/orgs/$Owner/repos" } else { "https://api.github.com/user/repos" }

try {
    $headers = @{ Authorization = "token $token"; Accept = "application/vnd.github+json"; "User-Agent" = "MOT-X OS" }
    $response = Invoke-RestMethod -Uri $uri -Method Post -Headers $headers -Body ($body | ConvertTo-Json -Depth 5) -ContentType "application/json"
} catch {
    Write-Host "ERROR: Failed to create GitHub repository." -ForegroundColor Red
    Write-Host $_.Exception.Message
    exit 2
}

$cloneUrl = $response.clone_url
$sshUrl = $response.ssh_url
Write-Host "Created GitHub repo: $($response.full_name)" -ForegroundColor Green
Write-Host "Clone URL: $cloneUrl"
Write-Host "SSH URL: $sshUrl"

$existing = git remote
if ($existing -match 'origin') {
    Write-Host "Remote 'origin' already exists. Skipping git remote add." -ForegroundColor Yellow
} else {
    git remote add origin $cloneUrl
    Write-Host "Added origin remote pointing to $cloneUrl" -ForegroundColor Green
}

try {
    git push -u origin master
    Write-Host "Pushed local master to origin." -ForegroundColor Green
} catch {
    Write-Host "WARNING: Failed to push to origin automatically." -ForegroundColor Yellow
    Write-Host $_.Exception.Message
    Write-Host "You can push manually with: git push -u origin master"
}
