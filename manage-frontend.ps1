# Chess Insight AI Frontend Management Script

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("start", "stop", "status", "restart")]
    [string]$Action
)

function Start-Frontend {
    Write-Host "Starting Chess Insight AI frontend..." -ForegroundColor Green
    $process = Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WorkingDirectory "frontend" -WindowStyle Hidden -PassThru
    Start-Sleep -Seconds 8
    
    $listening = netstat -an | findstr ":3000"
    if ($listening) {
        Write-Host "[SUCCESS] Frontend is running at http://localhost:3000" -ForegroundColor Green
        Write-Host "[INFO] Dashboard available for Chess.com analysis" -ForegroundColor Cyan
    } else {
        Write-Host "[ERROR] Failed to start frontend" -ForegroundColor Red
    }
}

function Stop-Frontend {
    Write-Host "Stopping frontend servers..." -ForegroundColor Yellow
    $nodeProcesses = Get-Process -Name "node" -ErrorAction SilentlyContinue
    if ($nodeProcesses) {
        $nodeProcesses | Where-Object { $_.ProcessName -eq "node" } | Stop-Process -Force
        Write-Host "[SUCCESS] Frontend processes stopped" -ForegroundColor Green
    } else {
        Write-Host "[INFO] No frontend processes found" -ForegroundColor Gray
    }
}

function Get-FrontendStatus {
    Write-Host "Chess Insight AI Service Status:" -ForegroundColor Cyan
    Write-Host "=================================" -ForegroundColor Cyan
    
    # Check frontend
    $listening = netstat -an | findstr ":3000"
    if ($listening) {
        Write-Host "[RUNNING] Frontend: http://localhost:3000" -ForegroundColor Green
    } else {
        Write-Host "[STOPPED] Frontend" -ForegroundColor Red
    }
    
    # Check backend
    $backendListening = netstat -an | findstr ":8000"
    if ($backendListening) {
        Write-Host "[RUNNING] Backend: http://localhost:8000" -ForegroundColor Green
    } else {
        Write-Host "[STOPPED] Backend" -ForegroundColor Red
    }
    
    # Check Docker services
    try {
        $dockerServices = docker ps --format "table {{.Names}}\t{{.Status}}" | Select-String "chess-insight"
        if ($dockerServices) {
            Write-Host "[RUNNING] Docker Services:" -ForegroundColor Green
            $dockerServices | ForEach-Object { Write-Host "   $($_.Line)" -ForegroundColor Gray }
        }
    } catch {
        Write-Host "[ERROR] Docker: Not accessible" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "Quick Actions:" -ForegroundColor Cyan
    Write-Host "- Visit: http://localhost:3000 (Frontend)"
    Write-Host "- API: http://localhost:8000/docs (Backend API docs)"
    Write-Host "- Manage: .\manage-frontend.ps1 [start|stop|status|restart]"
}

function Restart-Frontend {
    Write-Host "Restarting frontend..." -ForegroundColor Yellow
    Stop-Frontend
    Start-Sleep -Seconds 3
    Start-Frontend
}

# Execute the requested action
switch ($Action) {
    "start" { Start-Frontend }
    "stop" { Stop-Frontend }
    "status" { Get-FrontendStatus }
    "restart" { Restart-Frontend }
}
