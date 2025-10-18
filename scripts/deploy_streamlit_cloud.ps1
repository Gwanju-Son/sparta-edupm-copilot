param(
  [string]$RepoName = "sparta-edupm-copilot",
  [string]$Branch = "main"
)

Write-Host "[1/5] Checking git..." -ForegroundColor Cyan
$gitExe = (Get-Command git -ErrorAction SilentlyContinue).Source
if (-not $gitExe) {
  $candidates = @(
    "C:\\Program Files\\Git\\cmd\\git.exe",
    "C:\\Program Files\\Git\\bin\\git.exe",
    "$env:LocalAppData\\Programs\\Git\\cmd\\git.exe"
  )
  foreach ($c in $candidates) { if (Test-Path $c) { $gitExe = $c; break } }
}
if (-not $gitExe) {
  Write-Error "git not found in PATH. Please reopen PowerShell or install Git: https://git-scm.com/downloads"
  exit 1
}
& $gitExe --version > $null 2>&1

Write-Host "[2/5] Initializing repository (if needed)..." -ForegroundColor Cyan
if (-not (Test-Path .git)) {
  & $gitExe init | Out-Null
  & $gitExe add . | Out-Null
  & $gitExe commit -m "init deploy" | Out-Null
  & $gitExe branch -M $Branch | Out-Null
}

Write-Host "[3/5] Checking GitHub CLI (gh)..." -ForegroundColor Cyan
$ghExe = (Get-Command gh -ErrorAction SilentlyContinue).Source
$hasGh = $null -ne $ghExe

if ($hasGh) {
  Write-Host "GitHub CLI found. Checking auth..." -ForegroundColor Green
  & $ghExe auth status > $null 2>&1
  if ($LASTEXITCODE -eq 0) {
    Write-Host "[4/5] Creating GitHub repo and pushing..." -ForegroundColor Cyan
    # If repo already exists, this may fail; handle gracefully
    & $ghExe repo create $RepoName --public --source . --remote origin --push 2>$null
    if ($LASTEXITCODE -ne 0) {
      Write-Host "gh repo create failed (maybe repo exists). Trying push to origin..." -ForegroundColor Yellow
      & $gitExe push -u origin $Branch
    }
  } else {
    Write-Host "GitHub CLI not authenticated. Run: gh auth login" -ForegroundColor Yellow
    Write-Host "Skipping repo creation. Ensure remote is set, then push manually:"
    Write-Host "  $gitExe remote add origin https://github.com/<you>/$RepoName.git" -ForegroundColor DarkGray
    Write-Host "  $gitExe push -u origin $Branch" -ForegroundColor DarkGray
  }
} else {
  Write-Host "GitHub CLI not installed. Proceeding without gh." -ForegroundColor Yellow
  $remotes = (& $gitExe remote) 2>$null
  if (-not $remotes) {
    Write-Host "Set remote and push manually:" -ForegroundColor Yellow
    Write-Host "  $gitExe remote add origin https://github.com/<you>/$RepoName.git" -ForegroundColor DarkGray
  }
  Write-Host "Then:" -ForegroundColor Yellow
  Write-Host "  $gitExe push -u origin $Branch" -ForegroundColor DarkGray
}

Write-Host "[5/5] Opening Streamlit Cloud..." -ForegroundColor Cyan
Start-Process "https://share.streamlit.io"
Write-Host "In Streamlit Cloud: New app → pick your repo → main branch → Main file: edupm_app/app.py" -ForegroundColor Green
Write-Host "On success, you'll get a permanent URL like: https://<app>.streamlit.app" -ForegroundColor Green
