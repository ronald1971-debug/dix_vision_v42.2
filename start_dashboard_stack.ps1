# DIX VISION v42.2 - Complete Dashboard Stack Launcher
# Starts all required services together: PostgreSQL, Redis, FastAPI Backend, React Dashboard

$ErrorActionPreference = "Stop"

Write-Host "🚀 DIX VISION v42.2 - Complete Dashboard Stack Launcher" -ForegroundColor Green
Write-Host "=======================================================" -ForegroundColor Green

# Set project root
$projectRoot = "c:/dix_vision_v42.2/containers/user_interfaces"
Set-Location $projectRoot

# Check if Docker is available
$dockerAvailable = Get-Command docker -ErrorAction SilentlyContinue

if ($dockerAvailable) {
    Write-Host "✅ Docker found - using Docker for infrastructure services" -ForegroundColor Green
} else {
    Write-Host "⚠️  Docker not found - will use local Python/Node services" -ForegroundColor Yellow
}

# Function to check if a port is in use
function Test-Port($port) {
    $connection = Test-NetConnection -ComputerName localhost -Port $port -WarningAction SilentlyContinue
    return $connection.TcpTestSucceeded
}

# Function to start PostgreSQL (if Docker not available)
function Start-PostgreSQL {
    Write-Host "🗄️  Starting PostgreSQL on port 5432..." -ForegroundColor Cyan
    if ($dockerAvailable) {
        docker run -d `
            --name dix-dashboard-postgres `
            -e POSTGRES_DB=dixvision `
            -e POSTGRES_USER=dixvision `
            -e POSTGRES_PASSWORD=dixvision_secure_password `
            -p 5432:5432 `
            postgres:15-alpine
    } else {
        Write-Host "⚠️  Docker not available - please install PostgreSQL manually" -ForegroundColor Red
        Write-Host "   Expected connection: postgresql://dixvision:dixvision_secure_password@localhost:5432/dixvision" -ForegroundColor Yellow
    }
}

# Function to start Redis (if Docker not available)
function Start-Redis {
    Write-Host "🔴 Starting Redis on port 6379..." -ForegroundColor Cyan
    if ($dockerAvailable) {
        docker run -d `
            --name dix-dashboard-redis `
            -p 6379:6379 `
            redis:alpine
    } else {
        Write-Host "⚠️  Docker not available - please install Redis manually" -ForegroundColor Yellow
        Write-Host "   Expected connection: redis://localhost:6379" -ForegroundColor Yellow
    }
}

# Function to start FastAPI Backend
function Start-FastAPI {
    Write-Host "⚡ Starting FastAPI Backend on port 8000..." -ForegroundColor Cyan
    
    # Create a log file for backend
    $backendLog = "$projectRoot/backend.log"
    
    # Start backend in background
    $env:PYTHONPATH = "$projectRoot"
    $env:DATABASE_URL = "postgresql://dixvision:dixvision_secure_password@localhost:5432/dixvision"
    $env:REDIS_URL = "redis://localhost:6379"
    
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectRoot'; python -m uvicorn ui.server:app --host 0.0.0.0 --port 8000 --reload | Tee-Object -FilePath '$backendLog'" -WindowStyle Minimized
    
    Write-Host "✅ Backend started (logs: $backendLog)" -ForegroundColor Green
    
    # Wait for backend to be ready
    Write-Host "⏳ Waiting for backend to be ready..." -ForegroundColor Yellow
    $maxWait = 30
    $waited = 0
    while ($waited -lt $maxWait) {
        if (Test-Port 8000) {
            Write-Host "✅ Backend is ready!" -ForegroundColor Green
            return
        }
        Start-Sleep 2
        $waited += 2
    }
    Write-Host "⚠️  Backend did not start within expected time" -ForegroundColor Yellow
}

# Function to start React Dashboard
function Start-Dashboard {
    Write-Host "🎨 Starting React Dashboard on port 5173..." -ForegroundColor Cyan
    
    $dashboardPath = "$projectRoot/dashboard2026"
    
    # Create a log file for dashboard
    $dashboardLog = "$projectRoot/dashboard.log"
    
    # Start dashboard in background
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$dashboardPath'; npm run dev | Tee-Object -FilePath '$dashboardLog'" -WindowStyle Minimized
    
    Write-Host "✅ Dashboard started (logs: $dashboardLog)" -ForegroundColor Green
    
    # Wait for dashboard to be ready
    Write-Host "⏳ Waiting for dashboard to be ready..." -ForegroundColor Yellow
    $maxWait = 30
    $waited = 0
    while ($waited -lt $maxWait) {
        if (Test-Port 5173) {
            Write-Host "✅ Dashboard is ready!" -ForegroundColor Green
            return
        }
        Start-Sleep 2
        $waited += 2
    }
    Write-Host "⚠️  Dashboard did not start within expected time" -ForegroundColor Yellow
}

# Function to stop all services
function Stop-AllServices {
    Write-Host "🛑 Stopping all services..." -ForegroundColor Red
    
    # Kill backend process
    Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like "*uvicorn*"} | Stop-Process -Force
    Get-Process node -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like "*vite*"} | Stop-Process -Force
    
    # Stop Docker containers if running
    if ($dockerAvailable) {
        docker stop dix-dashboard-postgres -ErrorAction SilentlyContinue
        docker stop dix-dashboard-redis -ErrorAction SilentlyContinue
        docker rm dix-dashboard-postgres -ErrorAction SilentlyContinue
        docker rm dix-dashboard-redis -ErrorAction SilentlyContinue
    }
    
    Write-Host "✅ All services stopped" -ForegroundColor Green
}

# Main execution
try {
    # Check if ports are already in use
    Write-Host "🔍 Checking port availability..." -ForegroundColor Cyan
    $portsInUse = @()
    
    if (Test-Port 5432) { $portsInUse += "PostgreSQL (5432)" }
    if (Test-Port 6379) { $portsInUse += "Redis (6379)" }
    if (Test-Port 8000) { $portsInUse += "FastAPI Backend (8000)" }
    if (Test-Port 5173) { $portsInUse += "React Dashboard (5173)" }
    
    if ($portsInUse.Count -gt 0) {
        Write-Host "⚠️  The following ports are already in use:" -ForegroundColor Yellow
        $portsInUse | ForEach-Object { Write-Host "   - $_" -ForegroundColor Yellow }
        Write-Host "   Services may already be running or you need to stop conflicting processes." -ForegroundColor Yellow
        
        $response = Read-Host "Do you want to continue anyway? (y/n)"
        if ($response -ne "y") {
            exit
        }
    }
    
    # Start infrastructure services
    if ($dockerAvailable) {
        Start-PostgreSQL
        Start-Redis
        
        Write-Host "⏳ Waiting for infrastructure services to be ready..." -ForegroundColor Yellow
        Start-Sleep 10
    }
    
    # Start application services
    Start-FastAPI
    Start-Dashboard
    
    Write-Host ""
    Write-Host "🎉 Complete Dashboard Stack Started Successfully!" -ForegroundColor Green
    Write-Host "=================================================" -ForegroundColor Green
    Write-Host "📊 Dashboard:  http://localhost:5173/dash2/" -ForegroundColor Cyan
    Write-Host "⚡ Backend:    http://localhost:8000" -ForegroundColor Cyan
    Write-Host "🗄️  Database:   postgresql://localhost:5432/dixvision" -ForegroundColor Cyan
    Write-Host "🔴 Redis:      redis://localhost:6379" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📋 Logs:" -ForegroundColor Cyan
    Write-Host "   Backend:  $projectRoot/backend.log" -ForegroundColor Yellow
    Write-Host "   Dashboard: $projectRoot/dashboard.log" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "🛑 To stop all services, run: Stop-AllServices" -ForegroundColor Yellow
    Write-Host "=================================================" -ForegroundColor Green
    
} catch {
    Write-Host "❌ Error starting services: $_" -ForegroundColor Red
    Stop-AllServices
    exit 1
}
