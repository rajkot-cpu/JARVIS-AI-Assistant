param(
  [switch]$Dry,
  [ValidateSet("session","workday","brief","install")]
  [string]$Cmd = "workday"
)
$J = "C:\Users\rajk1\jarvis"
$py = (Get-Command python -ErrorAction Stop).Source
Set-Location $J
switch ($Cmd) {
  "session" { & $py "$J\scripts\win\session_start.py" }
  "brief"   {
      if ($Dry) { & $py "$J\scripts\win\brief.py" }
      else { & $py "$J\scripts\win\brief.py" "--write" }
    }
  "workday" {
      if ($Dry) { & $py "$J\scripts\win\workday_start.py" "--dry" }
      else { & $py "$J\scripts\win\workday_start.py" }
    }
  "install" { & powershell -NoProfile -ExecutionPolicy Bypass -File "$J\scripts\install_user.ps1" }
}
