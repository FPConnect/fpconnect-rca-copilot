# Agente Autônomo Local

Agente de linha de comando focado em automatizar tarefas **no seu próprio computador**,
com ferramentas explícitas e sempre sob seu controle.

> Importante: este projeto **não** faz logins automáticos, nem se inscreve em
> vagas “sozinho”. Ele oferece comandos e atalhos que você dispara
> conscientemente.

## Recursos atuais

- `terminal: <comando>` – executa um comando de terminal local e mostra a saída.
- `abrir url: <url>` – abre uma URL no navegador padrão (útil para vagas, aulas, vídeos etc.).
- `rdp[: caminho.rdp]` – abre o cliente de Área de Trabalho Remota (Windows, `mstsc`).
- `falar: <texto>` – lê o texto em voz alta usando TTS local (`pyttsx3`).
- Memória simples da sessão (histórico salvo em um arquivo JSON na sua home).
- Planejador determinístico por regras: mesmo **sem LLM**, ele tenta converter
  pedidos comuns ("listar arquivos", "abrir https://...", "ler em voz alta...")
  em comandos estruturados.

Se você configurar backends de LLM, pode escrever frases soltas (por exemplo,
"quero revisar vagas de data engineer") e o agente **só sugere** um comando
estruturado (`terminal: ...`, `abrir url: ...`, etc). A execução continua sob
seu controle.

Backends suportados para sugestão de comandos (planejamento):

- OpenAI / APIs compatíveis (via cliente `openai`):
  - `OPENAI_API_KEY` – obrigatório
  - `OPENAI_MODEL` – opcional, padrão `gpt-4.1-mini`
  - `OPENAI_BASE_URL` – opcional para provedores compatíveis (Azure, OpenRouter,
    servidores locais, etc.).
- Anthropic (Claude):
  - `ANTHROPIC_API_KEY`
  - `ANTHROPIC_MODEL` – opcional, padrão `claude-3-haiku-20240307`.
- Google Gemini:
  - `GEMINI_API_KEY` ou `GOOGLE_API_KEY`
  - `GEMINI_MODEL` – opcional, padrão `gemini-1.5-flash`.

Seleção de backend via variável de ambiente:

- `AGENTE_AUTONOMO_BACKEND` aceita:
  - `ollama` – usa Ollama local (API compatível OpenAI) com defaults locais.
  - `openai` – usa apenas OpenAI / base compatível.
  - `anthropic` – usa apenas Claude.
  - `gemini` ou `google` – usa apenas Gemini.
  - `auto` ou `ensemble` (padrão) – tenta **todos** na ordem:
    OpenAI → Anthropic → Gemini. Sempre com fallback para as regras locais.

## Como rodar

Na pasta `agente-autonomo`:

```bash
python -m pip install -e .
# depois
agente-autonomo
```

Ou, sem instalar como script:

```bash
python -m agent_core.cli
```

## Revisao ciclica 50x (pos-tarefa)

Para validar repetidamente ao final de cada bloco de trabalho, rode:

```bash
python scripts/qa_review_cycles.py --loops 50
```

Isso executa em cada ciclo:

- `pytest -q`
- `python scripts/_smoke_check.py --fail-fast`

Se quiser incluir validacao de rede no bot de mercado em todos os ciclos:

```bash
python scripts/qa_review_cycles.py --loops 50 --include-network
```

Os logs ficam em `scripts/qa_loop_reports/review_cycles_*.log`.

Se quiser automatizar "tarefa + revisao 50x" em um unico comando:

```bash
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_task_with_review.ps1 -TaskCommand "python -m pytest -q" -Loops 50 -IncludeNetwork
```

Para ativar o modo com sugestões em linguagem natural usando OpenAI:

```bash
set OPENAI_API_KEY=SUACHAVE   # PowerShell: $env:OPENAI_API_KEY="SUACHAVE"
set OPENAI_MODEL=gpt-4.1-mini # opcional
```

Para ativar o modo "ensemble" com vários LLMs ao mesmo tempo:

```bash
set AGENTE_AUTONOMO_BACKEND=auto
set OPENAI_API_KEY=...        # opcional, se quiser usar OpenAI/compatível
set ANTHROPIC_API_KEY=...     # opcional, se quiser usar Claude
set GEMINI_API_KEY=...        # ou GOOGLE_API_KEY=..., opcional, se quiser Gemini
```

O agente sempre tenta primeiro as **regras locais**; se elas não cobrirem o
pedido, ele consulta os LLMs configurados na ordem definida pelo backend.

## Modo local (modelo IBM: Ollama + Granite + Continue)

Se voce quiser seguir o fluxo do artigo da IBM para simplificar operacao local,
este projeto ja suporta isso via endpoint compativel OpenAI do Ollama.

### 1) Instale o Ollama

- Download: https://ollama.com/download

### 2) Puxe os modelos Granite sugeridos

Opcao manual:

```bash
ollama pull granite4:tiny-h
ollama pull granite4:350m-h
ollama pull granite-embedding:30m
```

Opcao automatica (Windows PowerShell):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/setup_local_ollama_granite.ps1
```

### 3) Aponte o agente para o Ollama local

No `.env` (ou variaveis de ambiente), configure:

```env
AGENTE_AUTONOMO_BACKEND=ollama
OLLAMA_BASE_URL=http://127.0.0.1:11434/v1
OLLAMA_API_KEY=ollama
OLLAMA_MODEL=granite4:tiny-h
```

Observacoes:

- O Ollama expoe API compativel OpenAI em `http://127.0.0.1:11434/v1`.
- `OLLAMA_API_KEY=ollama` e apenas placeholder para clientes que exigem chave.
- Se preferir, voce pode continuar usando `OPENAI_BASE_URL/OPENAI_MODEL` para o mesmo endpoint local.

### 4) Suba o painel web normalmente

```powershell
./start_web.ps1
```

### 5) (Opcional) Continue com Granite local

O template inspirado no artigo esta em:

- `docs/continue-granite-local-config.yaml`

Copie para seu `~/.continue/config.yaml` e ajuste os modelos conforme hardware.

## Painel Web

Além da CLI, você pode usar um painel web em modo chat.

### Setup rapido com .env (recomendado)

1) Copie o template e preencha suas chaves:

```bash
copy .env.example .env
```

2) Edite `agente-autonomo/.env` e preencha:

- `AGENTE_AUTONOMO_BACKEND=all` (ou `auto`)
- `OPENAI_API_KEY=...`
- `ANTHROPIC_API_KEY=...`
- `GEMINI_API_KEY=...`

3) Rode o script de inicializacao (ele carrega `.env` automaticamente):

```bash
./start_web.ps1
```

ou no cmd:

```bash
start_web.bat
```

Os scripts tambem instalam o `playwright` e o Chromium usado pela janela
interna, para a area remota subir pronta sem setup manual adicional.

O loop oculto de QA em segundo plano fica desativado por padrao para nao saturar
o painel web logo na inicializacao. Se voce quiser ligar esse diagnostico,
adicione no `.env`:

```bash
AGENTE_AUTONOMO_BACKGROUND_QA=1
AGENTE_AUTONOMO_BACKGROUND_QA_COUNT=40
AGENTE_AUTONOMO_BACKGROUND_QA_INTERVAL=3600
```

Na pasta `agente-autonomo`:

```bash
python -m pip install -e .[llms]  # opcional, se quiser ativar Anthropic/Gemini
python -m uvicorn web.server:app --reload --port 8000
```

Depois acesse em `http://127.0.0.1:8000/`. O painel envia requisições para
`/api/command`, exatamente como a CLI, incluindo o modo de confirmação de
comandos sugeridos pelo LLM.

## Exemplos de uso

- Abrir uma vaga de emprego em um site:

```text
Comando> abrir url: https://www.linkedin.com/jobs/
```

- Rodar um comando de diagnóstico:

```text
Comando> terminal: ping google.com
```

- Ler uma descrição de vaga em voz alta (copie/cole o texto):

```text
Comando> falar: Vaga para engenheiro de software com foco em saúde digital...
```

- Abrir o cliente de Área de Trabalho Remota no Windows:

```text
Comando> rdp
```

Se você tiver um arquivo `.rdp` configurado, pode passar o caminho:

```text
Comando> rdp: C:\Users\SeuUsuario\Desktop\meu-servidor.rdp
```

## Próximos passos sugeridos

- Adicionar integrações específicas (por exemplo, script Playwright para
  navegar em um site de vagas que você usar, sempre com revisão humana).
- Evoluir o painel web para dashboards específicos (status de tarefas,
  logs de comandos, etc.).

## Modulo de mercado

O agente agora tambem tem um modulo de analise tecnica e paper trading para
acoes, forex e cripto usando dados publicos de mercado.

Comandos principais:

```text
mercado: help
mercado: analisar AAPL
mercado: plano NVDA
mercado: comprar BTC-USD
mercado: carteira
mercado: atualizar
mercado: vender BTC-USD
mercado: universo
mercado: ranking AAPL,MSFT,NVDA,TSM,PETR4.SA
mercado: trilha iniciante
mercado: trilha fundamentalista
mercado: trilha trader
```

Arquitetura implementada:

- Coleta de cotacoes e historico diario via endpoints publicos do Yahoo Finance.
- Conversao de risco e alvo para BRL via taxa cambial atual, para aplicar a mesma
  politica em acoes, forex e cripto.
- Camada de analise tecnica com SMA20, SMA50, RSI14, ATR14, momentum e
  volatilidade.
- Camada de risco que so aprova paper trades quando o modelo consegue montar um
  alvo >= R$ 100 e uma perda modelada <= R$ 50 em BRL.
- Carteira simulada persistida em `~/.agente_autonomo/market_state.json`, com
  sincronizacao de stop e alvo.
- Base curada local de conhecimento financeiro persistida no `knowledge.db`, para
  cobrir topicos recorrentes como debentures, duration, curva de juros, opcoes,
  futuros, marcacao a mercado e leitura de balanco.
- Trilhas de estudo guiado para tres perfis: iniciante, fundamentalista e trader.

Limitacoes importantes:

- Mercado real nao permite garantir lucro minimo nem perda maxima absoluta.
- Gaps, slippage, latencia, fila, liquidez e falhas de rede podem violar qualquer
  limite teorico em execucao real.
- Por isso, esta versao implementa apenas analise e paper trading. Roteamento para
  corretora real deve ser uma camada separada, opt-in, com confirmacao humana e
  adaptadores especificos para a corretora escolhida.

Camadas de resposta do dominio financeiro:

- Respostas locais deterministicas para perguntas amplas e educativas.
- Base curada persistida no banco local para topicos tecnicos recorrentes.
- Pesquisa complementar na web quando a pergunta financeira excede a cobertura local.
