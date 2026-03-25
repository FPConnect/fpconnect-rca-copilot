param(
  [ValidateSet("local", "ollama", "network")]
  [string]$Profile = "local",
  [int]$Loops = 50,
  [string]$PythonExe = "c:/python314/python.exe",
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$includeNetwork = $false
[double]$maxStepSeconds = 0
[double]$maxPytestSeconds = 0

switch ($Profile) {
  "local" {
    $includeNetwork = $false
    $maxStepSeconds = 25
    $maxPytestSeconds = 15
  }
  "ollama" {
    $includeNetwork = $false
    $maxStepSeconds = 90
    $maxPytestSeconds = 60
  }
  "network" {
    $includeNetwork = $true
    $maxStepSeconds = 120
    $maxPytestSeconds = 60
  }
}

$python = $PythonExe
if (-not (Test-Path $python)) {
  $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
  if ($pythonCmd) {
    $python = $pythonCmd.Source
  }
  else {
    throw "Python nao encontrado. Informe -PythonExe com caminho valido."
  }
}

$reviewArgs = @(
  "scripts/qa_review_cycles.py",
  "--loops", $Loops,
  "--max-step-seconds", $maxStepSeconds,
  "--max-pytest-seconds", $maxPytestSeconds
)

if ($includeNetwork) {
  $reviewArgs += "--include-network"
}

Write-Host "[profile] $Profile" -ForegroundColor Cyan
Write-Host "[python]  $python" -ForegroundColor Cyan
Write-Host "[args]    $($reviewArgs -join ' ')" -ForegroundColor Cyan

if ($DryRun) {
  Write-Host "[dry-run] Nenhuma execucao foi iniciada." -ForegroundColor Yellow
  exit 0
}

& $python @reviewArgs
exit $LASTEXITCODE
