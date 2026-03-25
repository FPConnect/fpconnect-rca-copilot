param(
  [switch]$SkipPull
)

$ErrorActionPreference = "Stop"

Write-Host "[local-granite] Preparando setup local com Ollama + Granite..." -ForegroundColor Cyan

$ollamaCmd = Get-Command ollama -ErrorAction SilentlyContinue
if (-not $ollamaCmd) {
  throw "Ollama nao encontrado no PATH. Instale em https://ollama.com/download e tente novamente."
}

try {
  & ollama list *> $null
} catch {
  throw "Ollama instalado, mas o servico nao respondeu. Abra o Ollama e tente de novo."
}

if (-not $SkipPull) {
  $models = @(
    "granite4:tiny-h",
    "granite4:350m-h",
    "granite-embedding:30m"
  )

  foreach ($model in $models) {
    Write-Host "[local-granite] Baixando modelo: $model" -ForegroundColor Yellow
    & ollama pull $model
    if ($LASTEXITCODE -ne 0) {
      throw "Falha ao baixar modelo $model"
    }
  }
}

Write-Host "" 
Write-Host "[local-granite] Setup base concluido." -ForegroundColor Green
Write-Host "Use estas variaveis no .env para este projeto:" -ForegroundColor Green
Write-Host "AGENTE_AUTONOMO_BACKEND=openai"
Write-Host "OPENAI_BASE_URL=http://127.0.0.1:11434/v1"
Write-Host "OPENAI_API_KEY=ollama"
Write-Host "OPENAI_MODEL=granite4:tiny-h"
Write-Host ""
Write-Host "Depois suba com: ./start_web.ps1" -ForegroundColor Cyan
