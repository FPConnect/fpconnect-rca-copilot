param(
  [string]$RequirementsPath = "",
  [string]$LogPath = ""
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$env:PIP_DISABLE_PIP_VERSION_CHECK = "1"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir

if ([string]::IsNullOrWhiteSpace($RequirementsPath)) {
  $RequirementsPath = Join-Path $scriptDir "requirements-all-topics.txt"
}
if ([string]::IsNullOrWhiteSpace($LogPath)) {
  $LogPath = Join-Path $scriptDir "auto-update.log"
}

function Write-Log {
  param([string]$Message)
  $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
  "$stamp $Message" | Out-File -FilePath $LogPath -Append -Encoding utf8
}

if (-not (Test-Path $RequirementsPath)) {
  Write-Log "[ERROR] Requirements file not found: $RequirementsPath"
  exit 1
}

Set-Location $projectRoot

$python = "c:/python314/python.exe"
if (-not (Test-Path $python)) {
  Write-Log "[ERROR] Python executable not found: $python"
  exit 1
}

$lines = Get-Content $RequirementsPath
$ok = 0
$fail = 0

Write-Log "[START] Auto package update"

foreach ($line in $lines) {
  $pkg = $line.Trim()
  if ([string]::IsNullOrWhiteSpace($pkg)) { continue }
  if ($pkg.StartsWith("#")) { continue }

  Write-Log "[INSTALL] $pkg"
  & $python -m pip install --disable-pip-version-check --no-warn-script-location --upgrade --prefer-binary $pkg *> $null
  if ($LASTEXITCODE -eq 0) {
    $ok++
  }
  else {
    $fail++
    Write-Log "[FAIL] $pkg"
  }
}

Write-Log "[DONE] ok=$ok fail=$fail"
exit 0
