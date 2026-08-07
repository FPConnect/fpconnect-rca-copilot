param(
  [Parameter(Mandatory = $true)]
  [string]$TaskCommand,
  [int]$Loops = 50,
  [switch]$IncludeNetwork,
  [double]$MaxStepSeconds = 0,
  [double]$MaxPytestSeconds = 0,
  [string]$PythonExe = "c:/python314/python.exe"
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

Write-Host "[task] Executando: $TaskCommand" -ForegroundColor Cyan
powershell -NoProfile -ExecutionPolicy Bypass -Command $TaskCommand
if ($LASTEXITCODE -ne 0) {
  Write-Error "[task] Falhou com exit code $LASTEXITCODE"
  exit $LASTEXITCODE
}

$python = $PythonExe
if (-not (Test-Path $python)) {
  $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
  if ($pythonCmd) {
    $python = $pythonCmd.Source
  }
  else {
    Write-Error "[review] Python nao encontrado. Informe -PythonExe com caminho valido."
    exit 1
  }
}

$reviewArgs = @("scripts/qa_review_cycles.py", "--loops", $Loops)
if ($IncludeNetwork) {
  $reviewArgs += "--include-network"
}
if ($MaxStepSeconds -gt 0) {
  $reviewArgs += @("--max-step-seconds", $MaxStepSeconds)
}
if ($MaxPytestSeconds -gt 0) {
  $reviewArgs += @("--max-pytest-seconds", $MaxPytestSeconds)
}

Write-Host "[review] Iniciando revisao ciclica..." -ForegroundColor Yellow
& $python @reviewArgs
if ($LASTEXITCODE -ne 0) {
  Write-Error "[review] Revisao falhou"
  exit $LASTEXITCODE
}

Write-Host "[done] Tarefa e revisao concluidas com sucesso." -ForegroundColor Green
