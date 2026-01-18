# Pre-Flight Checklist
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "   Pencil Draw - Pre-Flight Check" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

$passed = 0
$failed = 0

function Test-Check {
    param([string]$Name, [scriptblock]$Test, [string]$Fix = "")
    Write-Host "Checking: $Name..." -NoNewline
    try {
        if (& $Test) {
            Write-Host " PASS" -ForegroundColor Green
            $script:passed++
        }
        else {
            Write-Host " FAIL" -ForegroundColor Red
            if ($Fix) { Write-Host "  Fix: $Fix" -ForegroundColor Yellow }
            $script:failed++
        }
    }
    catch {
        Write-Host " ERROR" -ForegroundColor Red
        if ($Fix) { Write-Host "  Fix: $Fix" -ForegroundColor Yellow }
        $script:failed++
    }
}

Write-Host "PREREQUISITES" -ForegroundColor Yellow
Test-Check "Docker installed" { Get-Command docker -ErrorAction SilentlyContinue } "Install Docker Desktop"
Test-Check "Docker running" { docker ps 2>$null; $? } "Start Docker Desktop"

Write-Host ""
Write-Host "FILE STRUCTURE" -ForegroundColor Yellow
Test-Check "Backend directory" { Test-Path ".\backend" }
Test-Check "Frontend directory" { Test-Path ".\frontend" }
Test-Check "docker-compose.yml" { Test-Path ".\docker-compose.yml" }

Write-Host ""
Write-Host "BACKEND FILES" -ForegroundColor Yellow
Test-Check "backend/Dockerfile" { Test-Path ".\backend\Dockerfile" }
Test-Check "backend/requirements.txt" { Test-Path ".\backend\requirements.txt" }
Test-Check "backend/app/main.py" { Test-Path ".\backend\app\main.py" }
Test-Check "backend/.env" { Test-Path ".\backend\.env" } "Copy-Item backend\.env.example backend\.env"

Write-Host ""
Write-Host "FRONTEND FILES" -ForegroundColor Yellow
Test-Check "frontend/Dockerfile" { Test-Path ".\frontend\Dockerfile" }
Test-Check "frontend/package.json" { Test-Path ".\frontend\package.json" }
Test-Check "frontend/app/page.tsx" { Test-Path ".\frontend\app\page.tsx" }
Test-Check "frontend/.env.local" { Test-Path ".\frontend\.env.local" } "Copy-Item frontend\.env.example frontend\.env.local"

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Passed: $passed | Failed: $failed" -ForegroundColor $(if ($failed -eq 0) { "Green" } else { "Red" })
Write-Host "=========================================" -ForegroundColor Cyan

if ($failed -eq 0) {
    Write-Host ""
    Write-Host "ALL CHECKS PASSED!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Ready to start! Run:" -ForegroundColor Cyan
    Write-Host "  docker-compose up --build" -ForegroundColor White
}
else {
    Write-Host ""
    Write-Host "Please fix the issues above" -ForegroundColor Red
    exit 1
}
