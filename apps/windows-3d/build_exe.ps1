param([string]$JarvisRoot = "C:\Users\rajk1\jarvis")
$ErrorActionPreference = "Stop"
Set-Location "$JarvisRoot\apps\windows-3d"
python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw "pip install failed" }
# panel_api/voice come from ..\windows-panel; lib_jarvis + win scripts from scripts\win.
# Hidden imports bundle them (and PyYAML/pywebview) so frozen imports also resolve.
python -m PyInstaller --noconfirm --clean --onefile --windowed --name Jarvis3D `
  --paths "$JarvisRoot\scripts\win" `
  --paths "$JarvisRoot\apps\windows-panel" `
  --paths "$JarvisRoot\apps\windows-3d" `
  --hidden-import panel_api --hidden-import bridge_api --hidden-import voice `
  --hidden-import lib_jarvis --hidden-import session_start --hidden-import brief `
  --hidden-import workday_start --hidden-import block_delete `
  --hidden-import yaml --hidden-import runpy --hidden-import argparse `
  --hidden-import webview --hidden-import pyttsx3 --hidden-import pyttsx3.drivers --hidden-import pyttsx3.drivers.sapi5 `
  --hidden-import win32com.client --hidden-import pythoncom `
  --icon "$JarvisRoot\apps\windows-panel\assets\jarvis.ico" --add-data "ui;ui" `
  --collect-all webview `
  host_main.py
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed" }
New-Item -ItemType Directory -Force -Path "$JarvisRoot\apps" | Out-Null
Copy-Item -Force ".\dist\Jarvis3D.exe" "$JarvisRoot\apps\Jarvis3D.exe"
$desk = [Environment]::GetFolderPath("Desktop")
$ws = New-Object -ComObject WScript.Shell
$sc = $ws.CreateShortcut("$desk\JARVIS 3D.lnk")
$sc.TargetPath = "$JarvisRoot\apps\Jarvis3D.exe"
$sc.WorkingDirectory = "$JarvisRoot"
$sc.IconLocation = "$JarvisRoot\apps\Jarvis3D.exe,0"
$sc.Save()
Write-Output "INSTALLED=$JarvisRoot\apps\Jarvis3D.exe"
