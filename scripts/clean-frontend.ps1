# Clean frontend build artifacts

Write-Host "🧹 Cleaning frontend build artifacts..." -ForegroundColor Cyan

# Stop any running node processes
Write-Host "`nStopping Node.js processes..." -ForegroundColor Yellow
Get-Process -Name node -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

# Navigate to frontend
Set-Location -Path "$PSScriptRoot\..\frontend"

# Remove build artifacts
Write-Host "`nRemoving build artifacts..." -ForegroundColor Yellow
$foldersToRemove = @(".next", "node_modules\.cache", "out")

foreach ($folder in $foldersToRemove) {
    if (Test-Path $folder) {
        Write-Host "  Removing $folder..." -ForegroundColor Gray
        Remove-Item -Path $folder -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "`n✅ Frontend cleaned successfully!" -ForegroundColor Green
Write-Host "`nYou can now run:" -ForegroundColor Cyan
Write-Host "  npm run dev    # Start development server" -ForegroundColor White
Write-Host "  npm run build  # Create production build" -ForegroundColor White
