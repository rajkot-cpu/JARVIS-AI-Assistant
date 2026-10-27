param([string]$JarvisRoot = "C:\Users\rajk1\jarvis")
$ErrorActionPreference = "Stop"
Set-Location "$JarvisRoot\apps\windows-panel"
python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw "pip install failed" }
# lib_jarvis + win scripts are imported at runtime via runpy from JARVIS_ROOT\scripts\win;
# hidden imports bundle them (and PyYAML/customtkinter) so frozen imports also resolve.
python -m PyInstaller --noconfirm --clean --onefile --windowed --name Jarvis `
  --paths "$JarvisRoot\scripts\win" `
  --paths "$JarvisRoot\apps\windows-panel" `
  --hidden-import lib_jarvis --hidden-import session_start --hidden-import brief `
  --hidden-import workday_start --hidden-import block_delete `
  --hidden-import yaml --hidden-import runpy --hidden-import argparse `
  --collect-all customtkinter `
  main.py
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed" }
New-Item -ItemType Directory -Force -Path "$JarvisRoot\apps" | Out-Null
Copy-Item -Force ".\dist\Jarvis.exe" "$JarvisRoot\apps\Jarvis.exe"
$desk = [Environment]::GetFolderPath("Desktop")
$ws = New-Object -ComObject WScript.Shell
$sc = $ws.CreateShortcut("$desk\JARVIS.lnk")
$sc.TargetPath = "$JarvisRoot\apps\Jarvis.exe"
$sc.WorkingDirectory = "$JarvisRoot"
$sc.Save()
Write-Output "INSTALLED=$JarvisRoot\apps\Jarvis.exe"
