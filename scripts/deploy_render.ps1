param(
  [string]$RepoName = "sparta-edupm-copilot",
  [string]$Branch = "main"
)

Write-Host "Render deployment helper" -ForegroundColor Cyan
Write-Host "Ensure your repo is on GitHub and public/private as desired." -ForegroundColor Cyan
Write-Host "This project includes render.yaml for one-click setup." -ForegroundColor Green

Start-Process "https://render.com"
Write-Host "Steps:" -ForegroundColor Cyan
Write-Host "1) Login to Render → New → Web Service" -ForegroundColor Green
Write-Host "2) Select repo: $RepoName (branch: $Branch)" -ForegroundColor Green
Write-Host "3) render.yaml should be auto-detected. Confirm and Create Web Service." -ForegroundColor Green
Write-Host "4) After build, you'll get a permanent URL like https://sparta-edupm-copilot.onrender.com" -ForegroundColor Green
