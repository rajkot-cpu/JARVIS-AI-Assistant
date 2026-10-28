# Build Command Center Jarvis.exe (run on Windows / chandan)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
if (-not (Test-Path (Join-Path $Root "STATE.md"))) {
  $Root = "C:\Users\rajk1\jarvis"
}
Set-Location $PSScriptRoot
python -m pip install -r requirements.txt
python -m pip install -r ..\windows-panel\requirements.txt
$Icon = Join-Path $PSScriptRoot "..\windows-panel\assets\jarvis.ico"
python -m PyInstaller --noconfirm --windowed --name Jarvis `
  --icon $Icon `
  --add-data "ui;ui" `
  --paths ..\windows-panel `
  --paths ..\..\scripts\win `
  host_main.py
$OutDir = Join-Path $Root "apps"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
Copy-Item -Force ".\dist\Jarvis\Jarvis.exe" (Join-Path $OutDir "Jarvis.exe")
$Desk = [Environment]::GetFolderPath("Desktop")
$Wsh = New-Object -ComObject WScript.Shell
$Sc = $Wsh.CreateShortcut((Join-Path $Desk "JARVIS.lnk"))
$Sc.TargetPath = (Join-Path $OutDir "Jarvis.exe")
$Sc.WorkingDirectory = $OutDir
$Sc.IconLocation = $Icon
$Sc.Save()
Write-Host "Installed $($OutDir)\Jarvis.exe + Desktop shortcut"
