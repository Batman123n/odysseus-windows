#Requires -Version 5.1
<#
  Odysseus - Desktop Launcher.
  Starts the native Python backend and the Electron wrapper.
#>

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

function Write-Step($msg) { Write-Host ""; Write-Host ("==> " + $msg) -ForegroundColor Cyan }

# 1. Ensure venv exists
$venvPy = Join-Path $PSScriptRoot "venv\Scripts\python.exe"
if (-not (Test-Path $venvPy)) {
    Write-Host "Python environment missing. Running setup first..." -ForegroundColor Yellow
    & powershell -ExecutionPolicy Bypass -File .\launch-windows.ps1
    # Exit after setup, user can run this again or it will just continue if it didn't block
}

# 2. Check for node_modules in desktop folder
$desktopDir = Join-Path $PSScriptRoot "desktop"
$nodeModules = Join-Path $desktopDir "node_modules"

if (-not (Test-Path $nodeModules)) {
    Write-Step "Installing Desktop dependencies..."
    Set-Location -Path $desktopDir
    npm install
    Set-Location -Path $PSScriptRoot
}


