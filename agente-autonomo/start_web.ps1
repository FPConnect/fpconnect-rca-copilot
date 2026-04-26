param(
  [int]$Port = 8012,
  [string]$ListenHost = "127.0.0.1"
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$env:PIP_DISABLE_PIP_VERSION_CHECK = "1"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$PythonExe = $env:AGENTE_AUTONOMO_PYTHON
if (-not $PythonExe) {
  $cmd = Get-Command python -ErrorAction SilentlyContinue
  if ($cmd) {
    $PythonExe = $cmd.Source
  }
}
if (-not $PythonExe) {
  throw "Python nao encontrado. Instale Python 3.10+ ou defina AGENTE_AUTONOMO_PYTHON."
}

function Test-PythonImport([string]$Module) {
  & $PythonExe -W ignore -c "import $Module" *> $null
  return $LASTEXITCODE -eq 0
}

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
  if ($env:AGENTE_AUTONOMO_HOST -and -not $PSBoundParameters.ContainsKey("ListenHost")) {
    $ListenHost = $env:AGENTE_AUTONOMO_HOST
  }
}

Write-Host "[agente-autonomo] Iniciando servidor web em $ListenHost`:$Port..." -ForegroundColor Cyan

# Ativa venv se existir (opcional)
if (Test-Path ".venv/Scripts/Activate.ps1") {
  . .\.venv\Scripts\Activate.ps1
}

if (-not $env:AGENTE_AUTONOMO_DISABLE_EMBEDDED_BROWSER) {
  $env:AGENTE_AUTONOMO_DISABLE_EMBEDDED_BROWSER = "0"
}

# Garante dependências mínimas
if (-not (Test-PythonImport "agent_core")) {
  & $PythonExe -m pip install --disable-pip-version-check --no-warn-script-location --no-build-isolation -q -e . *> $null
  if ($LASTEXITCODE -ne 0) { throw "Falha ao instalar dependencias base." }
}

if ((-not (Test-PythonImport "anthropic")) -or (-not (Test-PythonImport "google.generativeai"))) {
  & $PythonExe -m pip install --disable-pip-version-check --no-warn-script-location --no-build-isolation -q -e .[llms] *> $null
  if ($LASTEXITCODE -ne 0) { throw "Falha ao instalar dependencias opcionais de LLM." }
}

if ((-not (Test-PythonImport "fastapi")) -or (-not (Test-PythonImport "uvicorn"))) {
  & $PythonExe -m pip install --disable-pip-version-check --no-warn-script-location -q fastapi uvicorn *> $null
  if ($LASTEXITCODE -ne 0) { throw "Falha ao instalar dependencias do servidor web." }
}

if (-not (Test-PythonImport "playwright")) {
  & $PythonExe -m pip install --disable-pip-version-check --no-warn-script-location -q playwright *> $null
  if ($LASTEXITCODE -ne 0) { throw "Falha ao instalar Playwright." }
}

$playwrightRoot = Join-Path $env:LOCALAPPDATA "ms-playwright"
if (-not (Test-Path $playwrightRoot)) {
  & $PythonExe -m playwright install chromium *> $null
  if ($LASTEXITCODE -ne 0) { throw "Falha ao instalar o Chromium do Playwright." }
}

& $PythonExe -m uvicorn web.server:app --host $ListenHost --port $Port
