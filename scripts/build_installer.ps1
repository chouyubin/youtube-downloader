param(
    [string]$Python = ".\.venv\Scripts\python.exe",
    [string]$AppName = "YouTubeDownloader",
    [string]$SetupName = "YouTubeDownloaderSetup.exe"
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Python = Join-Path $Root $Python
$ReleaseDir = Join-Path $Root "release"
$PayloadDir = Join-Path $Root "build\installer_payload"
$DistDir = Join-Path $Root "dist\$AppName"
$SetupPath = Join-Path $ReleaseDir $SetupName

function New-CleanDirectory([string]$Path) {
    if (Test-Path $Path) {
        Remove-Item -LiteralPath $Path -Recurse -Force
    }
    New-Item -ItemType Directory -Path $Path -Force | Out-Null
}

Set-Location $Root
New-Item -ItemType Directory -Path $ReleaseDir -Force | Out-Null

if (-not (Test-Path $Python)) {
    throw "Python not found: $Python. Create .venv first or pass -Python."
}

Write-Host "Installing Python build dependencies"
& $Python -m pip install -r (Join-Path $Root "requirements.txt") pyinstaller

Write-Host "Building PyInstaller app"
& $Python -m PyInstaller `
    --noconfirm `
    --clean `
    --windowed `
    --name $AppName `
    --collect-all yt_dlp `
    --collect-all torf `
    (Join-Path $Root "main.py")

if (-not (Test-Path (Join-Path $DistDir "$AppName.exe"))) {
    throw "PyInstaller output not found: $DistDir\$AppName.exe"
}

Write-Host "Creating installer payload"
New-CleanDirectory $PayloadDir
$ZipPath = Join-Path $PayloadDir "app.zip"
Compress-Archive -Path (Join-Path $DistDir "*") -DestinationPath $ZipPath -Force

Write-Host "Creating installer executable"
& $Python -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --windowed `
    --name ([System.IO.Path]::GetFileNameWithoutExtension($SetupName)) `
    --distpath $ReleaseDir `
    --workpath (Join-Path $Root "build\installer_build") `
    --specpath (Join-Path $Root "build") `
    --add-data "$ZipPath;." `
    (Join-Path $Root "scripts\installer_launcher.py")

if (-not (Test-Path $SetupPath)) {
    throw "Installer was not created: $SetupPath"
}

Write-Host "Installer ready: $SetupPath"
