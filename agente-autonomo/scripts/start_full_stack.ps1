param(
  [ValidateSet("local", "ollama", "network")]
  [string]$Profile = "local",
  [int]$Loops = 1,
  [int]$Port = 8012,
  [string]$PythonExe = "c:/python314/python.exe",
  [switch]$SkipReview,
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

Write-Host "[stack] root: $root" -ForegroundColor Cyan
Write-Host "[stack] profile=$Profile loops=$Loops port=$Port" -ForegroundColor Cyan

if (-not $SkipReview) {
  $reviewParams = @{
    Profile = $Profile
    Loops = $Loops
    PythonExe = $PythonExe
  }

  if ($DryRun) {
    Write-Host "[dry-run] .\\scripts\\run_review_profile.ps1 -Profile $Profile -Loops $Loops -PythonExe $PythonExe" -ForegroundColor Yellow
  }
  else {
    Write-Host "[stack] Rodando revisao ciclica..." -ForegroundColor Yellow
    & .\scripts\run_review_profile.ps1 @reviewParams
    if ($LASTEXITCODE -ne 0) {
      Write-Error "[stack] Revisao falhou. Stack abortada."
      exit $LASTEXITCODE
    }
  }
}
else {
  Write-Host "[stack] Revisao ignorada por -SkipReview" -ForegroundColor Yellow
}

if ($DryRun) {
  Write-Host "[dry-run] .\\start_web.ps1 -Port $Port" -ForegroundColor Yellow
  exit 0
}

Write-Host "[stack] Subindo servidor web..." -ForegroundColor Green
& .\start_web.ps1 -Port $Port
exit $LASTEXITCODE
