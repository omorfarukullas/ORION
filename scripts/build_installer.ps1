# ==============================================================================
# ORION One-Click Windows Build & Installer Pipeline
# ==============================================================================
# Usage:
#   powershell -ExecutionPolicy Bypass -File .\scripts\build_installer.ps1
# ==============================================================================

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "  ORION — Building Standalone Windows Executable & Installer" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir
Set-Location $RootDir

# 1. Activate Python Environment
$VenvPy = "$RootDir\venv\Scripts\python.exe"
$VenvPip = "$RootDir\venv\Scripts\pip.exe"

if (-Not (Test-Path $VenvPy)) {
    Write-Host "[!] Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv venv
    & $VenvPip install -r requirements.txt
}

# 2. Verify PyInstaller
Write-Host "[1/4] Ensuring PyInstaller is available..." -ForegroundColor Green
& $VenvPip install pyinstaller --upgrade

# 3. Clean previous builds
Write-Host "[2/4] Cleaning previous build artifacts..." -ForegroundColor Green
if (Test-Path "$RootDir\build") { Remove-Item -Recurse -Force "$RootDir\build" }
if (Test-Path "$RootDir\dist\ORION") { Remove-Item -Recurse -Force "$RootDir\dist\ORION" }

# 4. Run PyInstaller
Write-Host "[3/4] Running PyInstaller build..." -ForegroundColor Green
& "$RootDir\venv\Scripts\pyinstaller.exe" "$RootDir\scripts\orion.spec" --noconfirm

# 5. Compile Inno Setup Installer (if ISCC is installed)
Write-Host "[4/4] Checking for Inno Setup compiler (ISCC.exe)..." -ForegroundColor Green
$ISCC_Paths = @(
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles}\Inno Setup 6\ISCC.exe",
    "${env:LOCALAPPDATA}\Programs\Inno Setup 6\ISCC.exe"
)

$FoundISCC = $null
foreach ($path in $ISCC_Paths) {
    if (Test-Path $path) {
        $FoundISCC = $path
        break
    }
}

if ($FoundISCC) {
    Write-Host "[+] Compiling Inno Setup package using: $FoundISCC" -ForegroundColor Cyan
    & $FoundISCC "$RootDir\scripts\orion_installer.iss"
    Write-Host "`nSUCCESS! Installer created in dist\installer\ORION-Setup-v2.0.0.exe" -ForegroundColor Green
} else {
    Write-Host "`n[NOTE] Inno Setup compiler not found in standard paths." -ForegroundColor Yellow
    Write-Host "Standalone distribution folder created at: dist\ORION\ORION.exe" -ForegroundColor Green
    Write-Host "To create the single-file setup wizard, install Inno Setup 6 and run this script again." -ForegroundColor Yellow
}

Write-Host "`nBuild complete!" -ForegroundColor Cyan
