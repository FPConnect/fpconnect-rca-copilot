# Agente Autonomo Local

Agente local com painel web, navegador embutido, terminal, memoria simples e comandos deterministas. O projeto continua sob controle humano: ele executa o que voce pedir, mas nao faz logins ou acoes sensiveis escondidas.

## O que ele faz

- executa comandos locais com `terminal: ...`
- abre URLs e navega pela area web do agente
- extrai texto de pagina
- abre RDP no Windows
- fala texto via TTS local
- usa LLMs para planejar quando houver chaves configuradas
- conecta Google Drive e OneDrive por OAuth para listar, ler, escrever, subir, mover, renomear e deletar arquivos

## Requisitos

- Python 3.10+
- Windows para o fluxo RDP
- Playwright Chromium para a area web embutida
- credenciais OAuth se voce quiser operar Google Drive ou OneDrive

## Instalacao

Na pasta `agente-autonomo`:

```bash
python -m pip install -e .
```

Se quiser habilitar Anthropic e Gemini:

```bash
python -m pip install -e .[llms]
```

## Configuracao rapida

Copie o template:

```bash
copy .env.example .env
```

Campos principais do `.env`:

- `AGENTE_AUTONOMO_BACKEND=auto|all|openai|anthropic|gemini`
- `OPENAI_API_KEY=...`
- `ANTHROPIC_API_KEY=...`
- `GEMINI_API_KEY=...`
- `AGENTE_AUTONOMO_HOST=127.0.0.1`
- `PORT=8012`
- `AGENTE_AUTONOMO_PUBLIC_BASE_URL=http://127.0.0.1:8012`
- `GOOGLE_DRIVE_CLIENT_ID=...`
- `GOOGLE_DRIVE_CLIENT_SECRET=...`
- `ONEDRIVE_CLIENT_ID=...`
- `ONEDRIVE_CLIENT_SECRET=...`

## Rodando

PowerShell:

```bash
./start_web.ps1
```

CMD:

```bash
start_web.bat
```

Manual:

```bash
python -m uvicorn web.server:app --host 127.0.0.1 --port 8012
```

Depois abra:

```text
http://127.0.0.1:8012/
```

## Cloud drives

Os cards de conexao aparecem no topo do painel. Tambem da para operar pelo chat.

Comandos suportados:

```text
drive status
drive connect google
drive connect onedrive
drive disconnect google
drive list google /
drive mkdir google /Projetos/2026
drive read google /Projetos/nota.txt
drive write google /Projetos/nota.txt => conteudo
drive upload onedrive C:\arquivo.txt => /Destino/arquivo.txt
drive rename google /Projetos/nota.txt => nota-final.txt
drive move google /Projetos/nota-final.txt => /Projetos/Arquivo
drive delete onedrive /Destino/arquivo.txt
```

### Escopos usados

- Google Drive: `https://www.googleapis.com/auth/drive`
- OneDrive: `Files.ReadWrite offline_access User.Read`

### Redirect URIs OAuth

Configure exatamente estas URLs no provedor:

- Google Drive:
  - `https://SEU-DOMINIO/api/cloud/oauth/google/callback`
- OneDrive:
  - `https://SEU-DOMINIO/api/cloud/oauth/onedrive/callback`

Se voce estiver rodando localmente:

- Google Drive:
  - `http://127.0.0.1:8012/api/cloud/oauth/google/callback`
- OneDrive:
  - `http://127.0.0.1:8012/api/cloud/oauth/onedrive/callback`

## Colocando em dominio proprio

Para expor o painel em um dominio seu, voce precisa de tres coisas:

1. DNS apontando para a maquina onde o agente roda.
2. TLS/HTTPS no dominio final.
3. `AGENTE_AUTONOMO_PUBLIC_BASE_URL` com a URL publica exata.

Configuracao recomendada:

```text
AGENTE_AUTONOMO_HOST=127.0.0.1
PORT=8012
AGENTE_AUTONOMO_PUBLIC_BASE_URL=https://agente.seudominio.com
```

Nesse modelo, o Uvicorn fica local e um proxy reverso publica o dominio. Ha um exemplo de Nginx em:

```text
deploy/nginx/agente-autonomo.conf.example
```

Se voce for expor o Uvicorn diretamente na rede, troque o bind:

```text
AGENTE_AUTONOMO_HOST=0.0.0.0
```

Mas, para producao, o modelo com proxy reverso e TLS continua sendo o melhor caminho.

## Health check

O projeto expone um endpoint simples para deploy e monitoramento:

```text
GET /healthz
```

Resposta:

```json
{"status":"ok"}
```

## Observacoes

- O navegador embutido depende do Playwright local e pode ser bloqueado por politica do ambiente.
- A conexao com Google Drive e OneDrive depende de rede externa disponivel.
- O estado das conexoes OAuth e salvo ao lado da memoria local do agente.
