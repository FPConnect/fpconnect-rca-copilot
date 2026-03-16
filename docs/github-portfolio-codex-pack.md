# GitHub Portfolio Codex Pack (Flavio Cruz)

Pacote pronto para colar no Codex e acelerar sua transição para um portfólio com aparência de engenharia sênior em Python/AI.

---

## 1) Prompt mestre (cole primeiro no Codex)

```text
You are my senior software engineering partner.

Goal:
1) Turn my GitHub presence into a senior-level Python/AI portfolio.
2) Refactor my existing repo "meu-agente-ia" into a professional, production-style project.
3) Create 3 new portfolio-grade Python/AI repositories with clean architecture, tests, docs, Docker, and CI.

Context about me:
- My name is Flavio Cruz.
- I have a strong background in field service engineering, medical diagnostics, troubleshooting, automation, and Python.
- I want my GitHub to position me as a Python Automation Engineer / AI Automation Engineer.
- My target audience is recruiters for Python, AI, automation, backend, and HealthTech roles.

General standards for all repos:
- Use Python 3.11+
- Clean architecture and modular folders
- Type hints
- Docstrings
- README.md written in professional English
- requirements.txt
- .env.example when applicable
- tests/ with pytest
- Makefile or simple run commands
- Dockerfile where useful
- GitHub Actions CI for lint + tests
- .gitignore
- MIT License
- Clear example usage
- Good repo description and suggested GitHub topics

Part A — Refactor my existing repo:
Repo: meu-agente-ia

Tasks:
- Remove all “course/fork/tutorial” appearance
- Replace the README with a professional product-style README
- Organize the code into folders like:
  /src
    /agent
    /tools
    /workflows
    /core
  /tests
- Create an executable entry point
- Add a simple but credible architecture:
  - agent orchestration
  - task runner
  - simple tool interface
  - configuration layer
- Add tests
- Add a concise roadmap
- Add repo metadata suggestions:
  description, topics, pinned recommendation

Part B — Create these 3 new repositories:

1) healthtech-log-analyzer
A Python application for parsing diagnostic equipment logs, extracting incidents, detecting recurring patterns, and generating a reliability report.

Must include:
- CLI interface
- sample input logs
- parsing module
- incident classification
- report generation in CSV/JSON
- README with screenshots or sample output
- tests

2) ai-ticket-triage-assistant
A Python service that classifies support tickets, suggests priority, summarizes incidents, and routes them to the right team.

Must include:
- FastAPI backend
- /health endpoint
- /classify endpoint
- structured response model
- prompt or rules layer
- local mock mode if no API key exists
- tests
- Docker support

3) workflow-agent-ops
A Python automation agent for operational workflows:
- receives a task
- selects tools
- executes simple steps
- logs the workflow
- returns final output

Must include:
- modular agent structure
- tool registry
- execution logs
- config file
- tests
- clean README
- architecture explanation

Part C — GitHub profile upgrade recommendations
Create:
- a profile README draft for my GitHub profile
- recommended pinned repos
- one-line repo descriptions
- GitHub topics for each repo
- suggested commit history milestones

Output format:
- First show a plan
- Then propose exact folder structures
- Then generate the README content
- Then generate the code files
- Then generate CI and Docker files
- Then generate GitHub profile README
- Keep everything practical, concise, and recruiter-friendly
```

---

## 2) Prompt específico para o repositório atual (cole em seguida)

```text
Refactor this repository into a professional portfolio project named “AI Automation Agent”.

Deliverables:
- Rewrite README as a real product README
- Remove any course/tutorial traces
- Create this structure:

src/
  agent/
  core/
  tools/
  workflows/
tests/

- Add:
  src/main.py
  src/agent/agent.py
  src/core/config.py
  src/tools/base.py
  src/workflows/runner.py

- Include:
  requirements.txt
  .env.example
  .gitignore
  LICENSE
  GitHub Actions CI
  minimal pytest coverage

The project should look like a credible automation/agent engineering repo for recruiters.
```

---

## 3) README de perfil (pronto para usar)

```md
# Hi, I'm Flavio Cruz

Python Developer | Automation & AI Systems | HealthTech Engineering

I build Python tools for:
- AI agents
- workflow automation
- diagnostic systems support
- log analysis and reliability monitoring

Background:
- 13+ years in medical diagnostics, field engineering, and complex systems support
- Experience with Abbott, ZEISS, and hospital technology environments
- Strong focus on troubleshooting, automation, and data-driven operations

Featured projects:
- AI Automation Agent
- HealthTech Log Analyzer
- AI Ticket Triage Assistant
- Workflow Agent Ops
```

---

## 4) Estruturas recomendadas dos 3 projetos

### 4.1 `healthtech-log-analyzer`

```text
healthtech-log-analyzer/
  src/
    log_analyzer/
      __init__.py
      cli.py
      parser.py
      classifier.py
      report.py
      models.py
  data/
    sample_logs.txt
  tests/
    test_parser.py
    test_classifier.py
    test_report.py
  .github/workflows/ci.yml
  .env.example
  .gitignore
  Dockerfile
  LICENSE
  Makefile
  README.md
  requirements.txt
```

### 4.2 `ai-ticket-triage-assistant`

```text
ai-ticket-triage-assistant/
  src/
    app/
      __init__.py
      main.py
      api.py
      models.py
      triage_service.py
      rules.py
      settings.py
  tests/
    test_health.py
    test_classify.py
  .github/workflows/ci.yml
  .env.example
  .gitignore
  Dockerfile
  LICENSE
  Makefile
  README.md
  requirements.txt
```

### 4.3 `workflow-agent-ops`

```text
workflow-agent-ops/
  src/
    workflow_agent/
      __init__.py
      main.py
      agent.py
      registry.py
      tools.py
      executor.py
      config.py
      logger.py
  config/
    settings.yaml
  tests/
    test_registry.py
    test_executor.py
  .github/workflows/ci.yml
  .env.example
  .gitignore
  Dockerfile
  LICENSE
  Makefile
  README.md
  requirements.txt
```

---

## 5) Arquivos iniciais prontos (starter snippets)

### 5.1 `healthtech-log-analyzer/src/log_analyzer/cli.py`

```python
from pathlib import Path
import typer
from .parser import parse_logs
from .classifier import classify_incidents
from .report import export_reports

app = typer.Typer(help="Parse diagnostic logs and generate reliability reports.")


@app.command()
def run(input_file: Path, output_dir: Path = Path("outputs")) -> None:
    records = parse_logs(input_file)
    incidents = classify_incidents(records)
    export_reports(incidents, output_dir)
    typer.echo(f"Processed {len(records)} records. Reports saved to {output_dir}")


if __name__ == "__main__":
    app()
```

### 5.2 `ai-ticket-triage-assistant/src/app/main.py`

```python
from fastapi import FastAPI
from .models import TicketRequest, TicketResponse
from .triage_service import classify_ticket

app = FastAPI(title="AI Ticket Triage Assistant", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/classify", response_model=TicketResponse)
def classify(payload: TicketRequest) -> TicketResponse:
    return classify_ticket(payload)
```

### 5.3 `workflow-agent-ops/src/workflow_agent/agent.py`

```python
from .registry import ToolRegistry
from .executor import Executor


class WorkflowAgent:
    def __init__(self, registry: ToolRegistry, executor: Executor) -> None:
        self.registry = registry
        self.executor = executor

    def run(self, task: str) -> dict:
        tool = self.registry.select(task)
        result = self.executor.execute(tool, task)
        return {"task": task, "tool": tool.name, "result": result}
```

---

## 6) Descrições curtas + topics (para GitHub)

| Repositório | Descrição | Topics |
|---|---|---|
| `meu-agente-ia` | AI automation agent for task orchestration, tool execution, and workflow control in Python. | `python`, `ai`, `automation`, `agents`, `backend`, `workflow` |
| `healthtech-log-analyzer` | Python tool to parse diagnostic equipment logs, detect incident patterns, and generate reliability reports. | `python`, `healthtech`, `log-analysis`, `automation`, `diagnostics`, `reliability` |
| `ai-ticket-triage-assistant` | FastAPI service for AI-assisted support ticket classification, prioritization, and routing. | `python`, `fastapi`, `ai`, `ticketing`, `backend`, `automation` |
| `workflow-agent-ops` | Modular Python agent for operational workflow automation with tool orchestration and execution logging. | `python`, `agents`, `automation`, `llm`, `workflow`, `backend` |

---

## 7) Ordem de execução recomendada

1. Refatorar `meu-agente-ia`
2. Criar `healthtech-log-analyzer`
3. Criar `ai-ticket-triage-assistant`
4. Criar `workflow-agent-ops`
5. Publicar README de perfil
6. Ajustar descrição, topics e pinagem

---

## 8) Milestones de commits sugeridos

1. `chore: scaffold clean architecture and project metadata`
2. `feat: implement core orchestration and configuration layers`
3. `feat: add CLI/API entrypoints and workflow execution`
4. `test: add pytest coverage for core modules`
5. `ci: add GitHub Actions for lint and tests`
6. `docs: rewrite README and add architecture + roadmap`

