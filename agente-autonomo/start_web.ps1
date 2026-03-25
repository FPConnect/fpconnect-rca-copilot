param(
  [int]$Port = 8012
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$env:PIP_DISABLE_PIP_VERSION_CHECK = "1"
if (Get-Variable -Name PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) {
  $PSNativeCommandUseErrorActionPreference = $false
}

Write-Host "[agente-autonomo] Iniciando servidor web na porta $Port..." -ForegroundColor Cyan

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

# Carrega variaveis de ambiente a partir de .env (se existir)
if (Test-Path ".env") {
  Get-Content ".env" | ForEach-Object {
    $line = $_.Trim()
    if (-not $line -or $line.StartsWith("#")) { return }
    $parts = $line -split "=", 2
    if ($parts.Count -eq 2) {
      $key = $parts[0].Trim()
      $value = $parts[1].Trim().Trim('"').Trim("'")
      if ($key) {
        [Environment]::SetEnvironmentVariable($key, $value, "Process")
      }
    }
  }
  if ($env:PORT -and -not $PSBoundParameters.ContainsKey("Port")) {
    [int]$Port = $env:PORT
  }
}

# Ativa venv se existir (opcional)
if (Test-Path ".venv/Scripts/Activate.ps1") {
  . .\.venv\Scripts\Activate.ps1
}

$pythonExe = "c:/python314/python.exe"
if (-not (Test-Path $pythonExe)) {
  $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
  if ($pythonCmd) {
    $pythonExe = $pythonCmd.Source
  }
  else {
    throw "Python nao encontrado. Configure c:/python314/python.exe ou instale python no PATH."
  }
}

function Invoke-NativeInstallStep {
  param(
    [Parameter(Mandatory = $true)]
    [string[]]$Args,
    [Parameter(Mandatory = $true)]
    [string]$FailureMessage
  )

  $previousPreference = $ErrorActionPreference
  $ErrorActionPreference = "Continue"
  try {
    & $pythonExe @Args 1> $null 2> $null
  }
  finally {
    $ErrorActionPreference = $previousPreference
  }

  if ($LASTEXITCODE -ne 0) {
    throw $FailureMessage
  }
}

# Garante dependências mínimas
Invoke-NativeInstallStep -Args @("-m", "pip", "install", "--disable-pip-version-check", "--no-warn-script-location", "-q", "-e", ".") -FailureMessage "Falha ao instalar dependencias base."
Invoke-NativeInstallStep -Args @("-m", "pip", "install", "--disable-pip-version-check", "--no-warn-script-location", "-q", "-e", ".[llms]") -FailureMessage "Falha ao instalar dependencias opcionais de LLM."
Invoke-NativeInstallStep -Args @("-m", "pip", "install", "--disable-pip-version-check", "--no-warn-script-location", "-q", "fastapi", "uvicorn") -FailureMessage "Falha ao instalar dependencias do servidor web."
Invoke-NativeInstallStep -Args @("-m", "pip", "install", "--disable-pip-version-check", "--no-warn-script-location", "-q", "playwright") -FailureMessage "Falha ao instalar Playwright."
Invoke-NativeInstallStep -Args @("-m", "playwright", "install", "chromium") -FailureMessage "Falha ao instalar o Chromium do Playwright."

& $pythonExe -m uvicorn web.server:app --host 127.0.0.1 --port $Port
