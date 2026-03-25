param(
  [string]$TaskName = "AgenteAutonomo-AutoUpdatePackages",
  [int]$IntervalMinutes = 15
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$updateScript = Join-Path $scriptDir "update_all_topics.ps1"

if (-not (Test-Path $updateScript)) {
  Write-Error "Update script not found: $updateScript"
  exit 1
}

$powerShellExe = "$env:WINDIR\System32\WindowsPowerShell\v1.0\powershell.exe"
$action = ('"{0}" -NoProfile -NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File "{1}"' -f $powerShellExe, $updateScript)

schtasks /Create /F /SC MINUTE /MO $IntervalMinutes /TN $TaskName /TR $action /RL LIMITED | Out-Null
if ($LASTEXITCODE -ne 0) {
  Write-Error "Failed to create scheduled task."
  exit 1
}

schtasks /Run /TN $TaskName | Out-Null

Write-Output "Task created and started."
Write-Output "Task: $TaskName"
Write-Output "Interval: every $IntervalMinutes minutes"
Write-Output "Action: $action"
