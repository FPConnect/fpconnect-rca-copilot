from __future__ import annotations

import os
import platform
import subprocess
import webbrowser
import base64
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


_browser_ctx = {
    "authorized": False,
    "playwright": None,
    "browser": None,
    "page": None,
    "last_url": None,
    "zoom": 1.2,
}

_BROWSER_MIN_ZOOM = 0.75
_BROWSER_MAX_ZOOM = 2.0

_browser_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="agent-browser")

_BROWSER_STOPWORDS = {
    "a",
    "o",
    "os",
    "as",
    "de",
    "do",
    "da",
    "dos",
    "das",
    "para",
    "por",
    "com",
    "sem",
    "em",
    "na",
    "no",
    "nas",
    "nos",
    "the",
    "and",
}

_BROWSER_TOKEN_ALIASES = {
    "gratis": {"gratis", "grátis", "free"},
    "free": {"gratis", "grátis", "free"},
    "download": {"download", "baixar", "baixe", "baixando"},
    "baixar": {"download", "baixar", "baixe", "baixando"},
    "browser": {"browser", "navegador"},
    "navegador": {"browser", "navegador"},
    "entrar": {"entrar", "login", "signin", "sign", "in"},
    "login": {"entrar", "login", "signin", "sign", "in"},
    "vaga": {"vaga", "vagas", "job", "jobs"},
    "jobs": {"vaga", "vagas", "job", "jobs"},
}


def _normalize_browser_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip().lower())


def _browser_tokens(value: str) -> list[str]:
    normalized = _normalize_browser_text(value)
    return [
        token
        for token in re.split(r"[^a-z0-9áàâãéêíóôõúç]+", normalized)
        if len(token) >= 2 and token not in _BROWSER_STOPWORDS
    ]


def _expand_browser_token(token: str) -> set[str]:
    return set(_BROWSER_TOKEN_ALIASES.get(token, {token}))


def _expanded_browser_token_sets(value: str) -> list[set[str]]:
    return [_expand_browser_token(token) for token in _browser_tokens(value)]


def _click_locator_with_fallback(page, item) -> None:
    try:
        item.click(timeout=5000)
        return
    except Exception:
        pass

    try:
        item.focus()
        page.keyboard.press("Enter")
        return
    except Exception:
        pass

    item.evaluate("el => el.click()")


def _result_candidate_score(label: str, href: str, target_text: str) -> int:
    normalized_target = _normalize_browser_text(target_text)
    normalized_label = _normalize_browser_text(label)
    normalized_href = _normalize_browser_text(href)
    haystack = f"{normalized_label} {normalized_href}".strip()
    if not normalized_target or not haystack:
        return 0

    score = 0
    if normalized_target in haystack:
        score += 120

    target_tokens = _expanded_browser_token_sets(normalized_target)
    candidate_tokens = set(_browser_tokens(haystack))
    for token_group in target_tokens:
        if candidate_tokens.intersection(token_group):
            score += 20
            continue
        if any(alias in haystack for alias in token_group):
            score += 8

    if target_tokens:
        overlap = sum(1 for token_group in target_tokens if candidate_tokens.intersection(token_group))
        if overlap == len(target_tokens):
            score += 25
        elif overlap >= max(1, len(target_tokens) - 1):
            score += 12

    if normalized_label.startswith(normalized_target):
        score += 30
    if normalized_target and normalized_target in normalized_href:
        score += 15
    return score


def _clear_browser_runtime() -> None:
    _browser_ctx["playwright"] = None
    _browser_ctx["browser"] = None
    _browser_ctx["page"] = None


def _clear_browser_session() -> None:
    _clear_browser_runtime()
    _browser_ctx["authorized"] = False


def _normalize_browser_zoom(value: float) -> float:
    return max(_BROWSER_MIN_ZOOM, min(_BROWSER_MAX_ZOOM, round(float(value), 2)))


def _apply_browser_zoom(page) -> None:
    zoom = _normalize_browser_zoom(float(_browser_ctx.get("zoom") or 1.0))
    _browser_ctx["zoom"] = zoom
    page.evaluate(
        """(zoomValue) => {
            const zoomText = String(zoomValue);
            document.documentElement.style.zoom = zoomText;
            if (document.body) {
                document.body.style.zoom = zoomText;
            }
        }""",
        zoom,
    )


def _is_browser_session_alive() -> bool:
    page = _browser_ctx.get("page")
    browser = _browser_ctx.get("browser")
    if page is None or browser is None:
        return False
    try:
        if hasattr(browser, "is_connected") and not browser.is_connected():
            return False
    except Exception:
        return False
    try:
        if hasattr(page, "is_closed") and page.is_closed():
            return False
    except Exception:
        return False
    return True


def _call_browser_worker(fn, *args):
    """Executa operações do Playwright em thread dedicada para evitar conflito com asyncio."""

    try:
        future = _browser_executor.submit(fn, *args)
        return future.result(timeout=90)
    except Exception as exc:
        return {"ok": False, "error": f"Falha na thread do navegador interno: {exc}"}


def _start_browser_runtime() -> tuple[bool, str]:
    """Inicializa o navegador interno do agente via Playwright (sem janela externa)."""

    if _is_browser_session_alive():
        return True, "Janela do agente ja esta ativa."

    if not _browser_ctx.get("authorized"):
        return False, "Acesso web ainda nao concedido. Use: browser enable"

    # Estado inconsistente (objetos fechados/mortos): limpamos antes de recriar.
    _clear_browser_runtime()

    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except Exception:
        return (
            False,
            "Playwright nao esta instalado. Instale com: pip install playwright e depois python -m playwright install chromium",
        )

    try:
        p = sync_playwright().start()
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 720})
        _apply_browser_zoom(page)
        _browser_ctx["playwright"] = p
        _browser_ctx["browser"] = browser
        _browser_ctx["page"] = page
        return True, "Navegador interno do agente iniciado. Acesso concedido para automacao web nesta sessao."
    except Exception as exc:
        return False, f"Nao foi possivel abrir a janela interna do agente: {exc}"


def _worker_open_url(url: str) -> dict:
    ok, msg = _start_browser_runtime()
    if not ok:
        return {"ok": False, "error": msg}

    page = _browser_ctx["page"]
    assert page is not None

    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    _browser_ctx["last_url"] = url

    try:
        page.goto(url, wait_until="domcontentloaded", timeout=20000)
        _apply_browser_zoom(page)
        return {"ok": True, "message": f"Janela interna navegou para: {url}"}
    except Exception as exc:
        if "has been closed" in str(exc).lower() or "target page" in str(exc).lower():
            ok2, _ = _start_browser_runtime()
            if ok2:
                try:
                    _browser_ctx["page"].goto(url, wait_until="domcontentloaded", timeout=20000)
                    _apply_browser_zoom(_browser_ctx["page"])
                    return {"ok": True, "message": f"Janela interna navegou para: {url}"}
                except Exception as exc2:
                    return {"ok": False, "error": f"Erro ao navegar na janela interna: {exc2}"}
        return {"ok": False, "error": f"Erro ao navegar na janela interna: {exc}"}


def _worker_bootstrap_runtime() -> dict:
        _browser_ctx["authorized"] = True

        ok, msg = _start_browser_runtime()
        if not ok:
                return {"ok": False, "error": msg}

        page = _browser_ctx.get("page")
        if page is None:
                return {"ok": False, "error": "A sessao remota nao iniciou corretamente."}

        last_url = _browser_ctx.get("last_url")

        try:
                current_url = ""
                try:
                        current_url = page.url or ""
                except Exception:
                        current_url = ""

                if isinstance(last_url, str) and last_url.strip() and current_url in {"", "about:blank"}:
                        page.goto(last_url, wait_until="domcontentloaded", timeout=20000)
                        _apply_browser_zoom(page)
                        return {"ok": True, "message": f"Area remota restaurada com a ultima URL: {last_url}"}

                if current_url in {"", "about:blank"}:
                        page.set_content(
                                """
                                <!doctype html>
                                <html lang=\"pt-BR\">
                                    <head>
                                        <meta charset=\"utf-8\" />
                                        <title>Workspace remota pronta</title>
                                        <style>
                                            :root { color-scheme: dark; }
                                            * { box-sizing: border-box; }
                                            body {
                                                margin: 0;
                                                min-height: 100vh;
                                                display: grid;
                                                place-items: center;
                                                font-family: "Segoe UI", sans-serif;
                                                background:
                                                    radial-gradient(circle at top, rgba(59, 130, 246, 0.32), transparent 28%),
                                                    linear-gradient(180deg, #09111f 0%, #050914 100%);
                                                color: #eff6ff;
                                            }
                                            .card {
                                                width: min(86vw, 820px);
                                                padding: 32px;
                                                border-radius: 24px;
                                                border: 1px solid rgba(148, 163, 184, 0.22);
                                                background: rgba(15, 23, 42, 0.78);
                                                box-shadow: 0 28px 80px rgba(2, 6, 23, 0.45);
                                            }
                                            .eyebrow {
                                                font-size: 12px;
                                                letter-spacing: 0.22em;
                                                text-transform: uppercase;
                                                color: #93c5fd;
                                                margin-bottom: 14px;
                                            }
                                            h1 {
                                                margin: 0 0 12px;
                                                font-size: 36px;
                                                line-height: 1.1;
                                            }
                                            p {
                                                margin: 0;
                                                font-size: 16px;
                                                line-height: 1.7;
                                                color: rgba(226, 232, 240, 0.9);
                                            }
                                        </style>
                                    </head>
                                    <body>
                                        <main class=\"card\">
                                            <div class=\"eyebrow\">Workspace Remota</div>
                                            <h1>A area de trabalho remota ja esta ativa.</h1>
                                            <p>Digite uma URL no painel ao lado para navegar sem depender do prompt do agente. Se preferir, o agente ainda pode assumir o controle pela conversa.</p>
                                        </main>
                                    </body>
                                </html>
                                """,
                                wait_until="domcontentloaded",
                        )
                        _apply_browser_zoom(page)
                        return {"ok": True, "message": "Area remota inicializada e pronta para receber uma URL diretamente pela interface."}
        except Exception as exc:
                return {"ok": False, "error": f"Erro ao preparar a area remota: {exc}"}

        return {"ok": True, "message": msg}


def _worker_stop_runtime() -> dict:
    page = _browser_ctx.get("page")
    browser = _browser_ctx.get("browser")
    p = _browser_ctx.get("playwright")

    try:
        if page is not None:
            try:
                page.close()
            except Exception:
                pass
        if browser is not None:
            browser.close()
        if p is not None:
            p.stop()
        _clear_browser_session()
        return {"ok": True, "message": "Sessao web do agente encerrada."}
    except Exception as exc:
        _clear_browser_session()
        return {"ok": False, "error": f"Erro ao fechar sessao web do agente: {exc}"}


def _worker_click_selector(selector: str) -> dict:
    if not _is_browser_session_alive():
        return {"ok": False, "error": "Nenhuma pagina ativa na janela interna. Informe uma URL primeiro."}
    try:
        _browser_ctx["page"].locator(selector).first.click(timeout=15000)
        return {"ok": True, "message": f"Clique executado no seletor: {selector}"}
    except Exception as exc:
        return {"ok": False, "error": f"Erro ao clicar no seletor '{selector}': {exc}"}


def _worker_click_text(label: str) -> dict:
    if not _is_browser_session_alive():
        return {"ok": False, "error": "Nenhuma pagina ativa na janela interna. Informe uma URL primeiro."}
    try:
        _browser_ctx["page"].get_by_text(label, exact=False).first.click(timeout=15000)
        return {"ok": True, "message": f"Clique executado no texto visivel: {label}"}
    except Exception as exc:
        return {"ok": False, "error": f"Erro ao clicar no texto '{label}': {exc}"}


def _worker_click_first_result() -> dict:
    if not _is_browser_session_alive():
        return {"ok": False, "error": "Nenhuma pagina ativa na janela interna. Informe uma URL primeiro."}

    page = _browser_ctx["page"]
    selectors = [
        "[data-testid='result-title-a']",
        "article[data-testid='result'] a[href]",
        ".result__title a[href]",
        "main article a[href]",
        "a:has(h3)",
        "main a[href]",
        "article a[href]",
        "a[href]",
    ]

    try:
        for selector in selectors:
            locator = page.locator(selector)
            count = min(locator.count(), 8)
            for index in range(count):
                item = locator.nth(index)
                href = (item.get_attribute("href") or "").strip()
                if not href or href.startswith(("#", "javascript:", "mailto:", "tel:", "/?", "/settings")):
                    continue
                try:
                    if not item.is_visible():
                        continue
                except Exception:
                    continue

                try:
                    text = " ".join(item.inner_text(timeout=2000).split())[:160]
                except Exception:
                    text = href[:160]

                _click_locator_with_fallback(page, item)

                label = text or href[:160] or "link"
                return {"ok": True, "message": f"Primeiro resultado aberto na janela interna: {label}"}
    except Exception as exc:
        return {"ok": False, "error": f"Erro ao abrir o primeiro resultado na janela interna: {exc}"}

    return {"ok": False, "error": "Nao encontrei um resultado clicavel na pagina aberta."}


def _worker_click_best_result(target_text: str) -> dict:
    if not _is_browser_session_alive():
        return {"ok": False, "error": "Nenhuma pagina ativa na janela interna. Informe uma URL primeiro."}

    page = _browser_ctx["page"]
    selectors = [
        "[data-testid='result-title-a']",
        "article[data-testid='result'] a[href]",
        ".result__title a[href]",
        "main article a[href]",
        "a:has(h3)",
        "main a[href]",
        "article a[href]",
        "a[href]",
    ]
    best_candidate = None

    try:
        for selector in selectors:
            locator = page.locator(selector)
            count = min(locator.count(), 12)
            for index in range(count):
                item = locator.nth(index)
                href = (item.get_attribute("href") or "").strip()
                if not href or href.startswith(("#", "javascript:", "mailto:", "tel:", "/?", "/settings")):
                    continue
                try:
                    if not item.is_visible():
                        continue
                except Exception:
                    continue

                try:
                    text = " ".join(item.inner_text(timeout=2000).split())[:160]
                except Exception:
                    text = href[:160]
                if not text:
                    text = " ".join(
                        filter(
                            None,
                            [
                                (item.get_attribute("aria-label") or "").strip(),
                                (item.get_attribute("title") or "").strip(),
                            ],
                        )
                    )[:160]

                score = _result_candidate_score(text, href, target_text)
                if score <= 0:
                    continue

                if best_candidate is None or score > best_candidate[0]:
                    best_candidate = (score, item, text, href)

        if best_candidate is None:
            text_locator = page.get_by_text(target_text, exact=False)
            visible_matches = min(text_locator.count(), 6)
            for index in range(visible_matches):
                item = text_locator.nth(index)
                try:
                    if not item.is_visible():
                        continue
                except Exception:
                    continue

                try:
                    text = " ".join(item.inner_text(timeout=2000).split())[:160]
                except Exception:
                    text = target_text

                _click_locator_with_fallback(page, item)
                return {"ok": True, "message": f"Resultado relacionado a '{target_text}' aberto na janela interna: {text or target_text}"}

            return {"ok": False, "error": f"Nao encontrei um resultado relacionado a '{target_text}' na pagina aberta."}

        _, item, text, href = best_candidate
        _click_locator_with_fallback(page, item)
        label = text or href[:160] or target_text
        return {"ok": True, "message": f"Resultado relacionado a '{target_text}' aberto na janela interna: {label}"}
    except Exception as exc:
        return {"ok": False, "error": f"Erro ao abrir resultado relacionado na janela interna: {exc}"}


def _worker_type_selector(selector: str, text: str) -> dict:
    if not _is_browser_session_alive():
        return {"ok": False, "error": "Nenhuma pagina ativa na janela interna. Informe uma URL primeiro."}
    try:
        field = _browser_ctx["page"].locator(selector).first
        field.click(timeout=15000)
        field.fill(text)
        return {"ok": True, "message": f"Texto preenchido no seletor {selector}."}
    except Exception as exc:
        return {"ok": False, "error": f"Erro ao digitar no seletor '{selector}': {exc}"}


def _worker_extract_selector(selector: str) -> dict:
    if not _is_browser_session_alive():
        return {"ok": False, "error": "Nenhuma pagina ativa na janela interna. Informe uma URL primeiro."}
    try:
        txt = _browser_ctx["page"].locator(selector).first.inner_text(timeout=15000)
        return {"ok": True, "message": f"Texto extraido de {selector}: {txt[:2000]}"}
    except Exception as exc:
        return {"ok": False, "error": f"Erro ao extrair texto do seletor '{selector}': {exc}"}


def _worker_wait(seconds: float) -> dict:
    if not _is_browser_session_alive():
        return {"ok": False, "error": "Nenhuma pagina ativa na janela interna. Informe uma URL primeiro."}
    try:
        _browser_ctx["page"].wait_for_timeout(max(0, seconds) * 1000)
        return {"ok": True, "message": f"Aguardado {seconds:.1f}s na janela interna."}
    except Exception as exc:
        return {"ok": False, "error": f"Erro no wait da janela interna: {exc}"}


def _worker_click_at(x: int, y: int) -> dict:
    if not _is_browser_session_alive():
        return {"ok": False, "error": "Nenhuma pagina ativa na janela interna. Informe uma URL primeiro."}
    try:
        _browser_ctx["page"].mouse.click(int(x), int(y))
        return {"ok": True, "message": f"Clique executado em ({int(x)}, {int(y)})."}
    except Exception as exc:
        return {"ok": False, "error": f"Erro ao clicar na janela interna: {exc}"}


def _worker_type_text(text: str, press_enter: bool = False) -> dict:
    if not _is_browser_session_alive():
        return {"ok": False, "error": "Nenhuma pagina ativa na janela interna. Informe uma URL primeiro."}
    try:
        if text:
            _browser_ctx["page"].keyboard.type(text)
        if press_enter:
            _browser_ctx["page"].keyboard.press("Enter")
        return {"ok": True, "message": "Texto digitado na janela interna."}
    except Exception as exc:
        return {"ok": False, "error": f"Erro ao digitar na janela interna: {exc}"}


def _worker_search_current_page(text: str, press_enter: bool = True) -> dict:
    if not _is_browser_session_alive():
        return {"ok": False, "error": "Nenhuma pagina ativa na janela interna. Informe uma URL primeiro."}

    page = _browser_ctx["page"]
    selectors = [
        "input[type='search']",
        "input[name*='search' i]",
        "input[id*='search' i]",
        "input[placeholder*='search' i]",
        "input[placeholder*='busca' i]",
        "input[placeholder*='pesquis' i]",
        "input[aria-label*='search' i]",
        "input[aria-label*='busca' i]",
        "input[aria-label*='pesquis' i]",
        "textarea[placeholder*='search' i]",
        "textarea[placeholder*='busca' i]",
    ]

    try:
        for selector in selectors:
            locator = page.locator(selector)
            count = min(locator.count(), 6)
            for index in range(count):
                field = locator.nth(index)
                try:
                    if not field.is_visible():
                        continue
                except Exception:
                    continue

                field.click(timeout=15000)
                field.fill(text)
                if press_enter:
                    field.press("Enter")
                return {"ok": True, "message": "Busca digitada no campo de pesquisa da pagina."}
    except Exception as exc:
        return {"ok": False, "error": f"Erro ao pesquisar na pagina atual: {exc}"}

    return {"ok": False, "error": "Nao encontrei um campo de busca utilizavel na pagina aberta."}


def _worker_press_key(key: str) -> dict:
    if not _is_browser_session_alive():
        return {"ok": False, "error": "Nenhuma pagina ativa na janela interna. Informe uma URL primeiro."}
    try:
        _browser_ctx["page"].keyboard.press(key)
        return {"ok": True, "message": f"Tecla enviada para janela interna: {key}"}
    except Exception as exc:
        return {"ok": False, "error": f"Erro ao enviar tecla na janela interna: {exc}"}


def _worker_copy_selection() -> dict:
    if not _is_browser_session_alive():
        return {"ok": False, "error": "Nenhuma pagina ativa na janela interna. Informe uma URL primeiro."}

    try:
        text = _browser_ctx["page"].evaluate(
            """() => {
                const active = document.activeElement;
                if (active && typeof active.value === 'string') {
                    const start = typeof active.selectionStart === 'number' ? active.selectionStart : null;
                    const end = typeof active.selectionEnd === 'number' ? active.selectionEnd : null;
                    if (start !== null && end !== null && end > start) {
                        return active.value.slice(start, end);
                    }
                }

                if (typeof window.getSelection === 'function') {
                    return String(window.getSelection() || '');
                }

                return '';
            }"""
        )
    except Exception as exc:
        return {"ok": False, "error": f"Erro ao copiar texto da janela interna: {exc}"}

    copied = text if isinstance(text, str) else str(text or "")
    if not copied:
        return {"ok": False, "error": "Nao encontrei texto selecionado para copiar na janela interna."}

    return {
        "ok": True,
        "text": copied,
        "message": f"Texto copiado da janela interna ({len(copied)} caracteres).",
    }


def _worker_paste_text(text: str) -> dict:
    if not _is_browser_session_alive():
        return {"ok": False, "error": "Nenhuma pagina ativa na janela interna. Informe uma URL primeiro."}
    if not text:
        return {"ok": False, "error": "A area de transferencia esta vazia."}

    try:
        accepts_text = _browser_ctx["page"].evaluate(
            """() => {
                const active = document.activeElement;
                if (!active) {
                    return false;
                }

                return Boolean(
                    active instanceof HTMLInputElement ||
                    active instanceof HTMLTextAreaElement ||
                    active.isContentEditable
                );
            }"""
        )
        if not accepts_text:
            return {"ok": False, "error": "Nenhum campo de texto esta focado na janela interna."}

        _browser_ctx["page"].keyboard.insert_text(text)
        return {"ok": True, "message": f"Texto colado na janela interna ({len(text)} caracteres)."}
    except Exception as exc:
        return {"ok": False, "error": f"Erro ao colar texto na janela interna: {exc}"}


def _worker_extract_page_text() -> dict:
    if not _is_browser_session_alive():
        return {"ok": False, "error": "Nenhuma pagina ativa na janela interna. Informe uma URL primeiro."}
    try:
        txt = _browser_ctx["page"].locator("body").inner_text(timeout=15000)
        compact = " ".join(txt.split())[:3000]
        return {"ok": True, "message": f"Texto principal da pagina: {compact}"}
    except Exception as exc:
        return {"ok": False, "error": f"Erro ao extrair texto da pagina: {exc}"}


def _worker_go_back() -> dict:
    if not _is_browser_session_alive():
        return {"ok": False, "error": "Nenhuma pagina ativa na janela interna. Informe uma URL primeiro."}
    try:
        _browser_ctx["page"].go_back(wait_until="domcontentloaded", timeout=20000)
        _apply_browser_zoom(_browser_ctx["page"])
        return {"ok": True, "message": "Voltei para a pagina anterior na janela interna."}
    except Exception as exc:
        return {"ok": False, "error": f"Erro ao voltar pagina na janela interna: {exc}"}


def _worker_go_forward() -> dict:
    if not _is_browser_session_alive():
        return {"ok": False, "error": "Nenhuma pagina ativa na janela interna. Informe uma URL primeiro."}
    try:
        _browser_ctx["page"].go_forward(wait_until="domcontentloaded", timeout=20000)
        _apply_browser_zoom(_browser_ctx["page"])
        return {"ok": True, "message": "Avancei para a proxima pagina na janela interna."}
    except Exception as exc:
        return {"ok": False, "error": f"Erro ao avancar pagina na janela interna: {exc}"}


def _worker_refresh() -> dict:
    if not _is_browser_session_alive():
        return {"ok": False, "error": "Nenhuma pagina ativa na janela interna. Informe uma URL primeiro."}
    try:
        _browser_ctx["page"].reload(wait_until="domcontentloaded", timeout=20000)
        _apply_browser_zoom(_browser_ctx["page"])
        return {"ok": True, "message": "Pagina recarregada na janela interna."}
    except Exception as exc:
        return {"ok": False, "error": f"Erro ao recarregar pagina na janela interna: {exc}"}


def _worker_set_zoom(zoom: float) -> dict:
    if not _is_browser_session_alive():
        return {"ok": False, "error": "Nenhuma pagina ativa na janela interna. Informe uma URL primeiro."}

    try:
        page = _browser_ctx["page"]
        _browser_ctx["zoom"] = _normalize_browser_zoom(zoom)
        _apply_browser_zoom(page)
        return {
            "ok": True,
            "message": f"Zoom do navegador interno ajustado para {round(_browser_ctx['zoom'] * 100):d}%.",
            "zoom": _browser_ctx["zoom"],
        }
    except Exception as exc:
        return {"ok": False, "error": f"Erro ao ajustar zoom da janela interna: {exc}"}


def _worker_snapshot() -> dict:
    if not _browser_ctx.get("authorized"):
        return {
            "ok": False,
            "error": "Acesso web nao concedido. Clique em 'Conceder acesso web'.",
        }

    if not _is_browser_session_alive():
        return {
            "ok": False,
            "error": "Aguardando URL para abrir o navegador interno.",
        }

    try:
        page = _browser_ctx["page"]
        _apply_browser_zoom(page)
        png_bytes = page.screenshot(type="png")
        b64 = base64.b64encode(png_bytes).decode("ascii")
        viewport = page.viewport_size or {"width": 1280, "height": 720}
        title = ""
        try:
            title = page.title()
        except Exception:
            title = ""
        return {
            "ok": True,
            "image_base64": b64,
            "url": page.url,
            "title": title,
            "width": int(viewport.get("width", 1280)),
            "height": int(viewport.get("height", 720)),
            "zoom": float(_browser_ctx.get("zoom") or 1.0),
        }
    except Exception as exc:
        return {"ok": False, "error": f"Erro ao capturar tela interna: {exc}"}


def browser_enable() -> str:
    _browser_ctx["authorized"] = True
    return "Acesso web concedido. Vou abrir o navegador interno quando voce informar uma URL."


def browser_disable() -> str:
    """Fecha a janela controlada do agente e encerra a sessao web."""
    result = _call_browser_worker(_worker_stop_runtime)
    if result.get("ok"):
        return result.get("message", "Sessao web do agente encerrada.")
    return result.get("error", "Erro ao fechar sessao web do agente.")


def browser_open_url(url: str) -> str:
    if not _browser_ctx.get("authorized"):
        _browser_ctx["authorized"] = True
    result = _call_browser_worker(_worker_open_url, url)
    if result.get("ok"):
        return result.get("message", "Janela interna navegou.")
    return result.get("error", "Erro ao navegar na janela interna.")


def browser_bootstrap() -> dict:
    result = _call_browser_worker(_worker_bootstrap_runtime)
    if isinstance(result, dict):
        return result
    return {"ok": False, "error": "Erro ao iniciar a area remota."}


def browser_click(selector: str) -> str:
    result = _call_browser_worker(_worker_click_selector, selector)
    if result.get("ok"):
        return result.get("message", f"Clique executado no seletor: {selector}")
    return result.get("error", "Erro ao clicar na janela interna.")


def browser_click_text(label: str) -> str:
    result = _call_browser_worker(_worker_click_text, label)
    if result.get("ok"):
        return result.get("message", f"Clique executado no texto visivel: {label}")
    return result.get("error", "Erro ao clicar na janela interna.")


def browser_click_first_result() -> str:
    result = _call_browser_worker(_worker_click_first_result)
    if result.get("ok"):
        return result.get("message", "Primeiro resultado aberto na janela interna.")
    return result.get("error", "Erro ao abrir o primeiro resultado na janela interna.")


def browser_click_best_result(target_text: str) -> str:
    result = _call_browser_worker(_worker_click_best_result, target_text)
    if result.get("ok"):
        return result.get("message", "Resultado relacionado aberto na janela interna.")
    return result.get("error", "Erro ao abrir resultado relacionado na janela interna.")


def browser_type(selector: str, text: str) -> str:
    result = _call_browser_worker(_worker_type_selector, selector, text)
    if result.get("ok"):
        return result.get("message", f"Texto preenchido no seletor {selector}.")
    return result.get("error", "Erro ao digitar na janela interna.")


def browser_extract_text(selector: str) -> str:
    result = _call_browser_worker(_worker_extract_selector, selector)
    if result.get("ok"):
        return result.get("message", "Texto extraido.")
    return result.get("error", "Erro ao extrair texto na janela interna.")


def browser_wait(seconds: float) -> str:
    result = _call_browser_worker(_worker_wait, seconds)
    if result.get("ok"):
        return result.get("message", f"Aguardado {seconds:.1f}s na janela interna.")
    return result.get("error", "Erro no wait da janela interna.")


def browser_click_at(x: int, y: int) -> str:
    result = _call_browser_worker(_worker_click_at, x, y)
    if result.get("ok"):
        return result.get("message", f"Clique executado em ({int(x)}, {int(y)}).")
    return result.get("error", "Erro ao clicar na janela interna.")


def browser_type_text(text: str, press_enter: bool = False) -> str:
    result = _call_browser_worker(_worker_type_text, text, press_enter)
    if result.get("ok"):
        return result.get("message", "Texto digitado na janela interna.")
    return result.get("error", "Erro ao digitar na janela interna.")


def browser_search_current_page(text: str, press_enter: bool = True) -> str:
    result = _call_browser_worker(_worker_search_current_page, text, press_enter)
    if result.get("ok"):
        return result.get("message", "Busca executada na pagina atual.")
    return result.get("error", "Erro ao pesquisar na pagina atual.")


def browser_press_key(key: str) -> str:
    result = _call_browser_worker(_worker_press_key, key)
    if result.get("ok"):
        return result.get("message", f"Tecla enviada para janela interna: {key}")
    return result.get("error", "Erro ao enviar tecla na janela interna.")


def browser_copy_selection() -> dict:
    result = _call_browser_worker(_worker_copy_selection)
    if isinstance(result, dict):
        return result
    return {"ok": False, "error": "Erro ao copiar texto da janela interna."}


def browser_paste_text(text: str) -> str:
    result = _call_browser_worker(_worker_paste_text, text)
    if result.get("ok"):
        return result.get("message", "Texto colado na janela interna.")
    return result.get("error", "Erro ao colar texto na janela interna.")


def browser_set_zoom(zoom: float) -> dict:
    result = _call_browser_worker(_worker_set_zoom, zoom)
    if isinstance(result, dict):
        return result
    return {"ok": False, "error": "Erro ao ajustar zoom da janela interna."}


def browser_extract_page_text() -> str:
    result = _call_browser_worker(_worker_extract_page_text)
    if result.get("ok"):
        return result.get("message", "Texto principal da pagina extraido.")
    return result.get("error", "Erro ao extrair texto da pagina.")


def browser_go_back() -> str:
    result = _call_browser_worker(_worker_go_back)
    if result.get("ok"):
        return result.get("message", "Voltei para a pagina anterior na janela interna.")
    return result.get("error", "Erro ao voltar pagina na janela interna.")


def browser_go_forward() -> str:
    result = _call_browser_worker(_worker_go_forward)
    if result.get("ok"):
        return result.get("message", "Avancei para a proxima pagina na janela interna.")
    return result.get("error", "Erro ao avancar pagina na janela interna.")


def browser_refresh() -> str:
    result = _call_browser_worker(_worker_refresh)
    if result.get("ok"):
        return result.get("message", "Pagina recarregada na janela interna.")
    return result.get("error", "Erro ao recarregar pagina na janela interna.")


def browser_snapshot() -> dict:
    """Retorna um snapshot PNG (base64) da janela interna para renderização na UI web."""

    result = _call_browser_worker(_worker_snapshot)
    if isinstance(result, dict):
        return result
    return {"ok": False, "error": "Falha ao capturar tela interna."}


def run_shell_command(command: str) -> str:
    """Executa um comando de shell localmente.

    Por segurança, a ideia é sempre mostrar o comando para o usuário
    antes de executar e pedir confirmação na CLI.
    """

    if not command.strip():
        return "Nenhum comando fornecido."

    try:
        completed = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
        )
        output = completed.stdout or completed.stderr or "(sem saída)"
        return output[:4000]
    except Exception as exc:  # pragma: no cover - defesa
        return f"Erro ao executar comando: {exc}"


def open_url(url: str) -> str:
    """Abre uma URL no navegador padrão."""

    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    try:
        webbrowser.open(url)
        return f"Abrindo URL no navegador: {url}"
    except Exception as exc:  # pragma: no cover
        return f"Erro ao abrir URL: {exc}"


def open_remote_desktop(target: str | None = None) -> str:
    """Tenta abrir o cliente de área de trabalho remota (Windows).

    Não preenche credenciais nem automatiza o acesso; apenas abre
    a ferramenta local (por exemplo, mstsc).
    """

    system = platform.system().lower()
    if system != "windows":
        return "Abertura de área de trabalho remota só está implementada para Windows."

    cmd = ["mstsc"]
    if target:
        # O usuário pode configurar um arquivo .rdp próprio.
        rdp_path = Path(target)
        cmd.append(str(rdp_path))

    try:
        subprocess.Popen(cmd)
        return "Cliente de área de trabalho remota aberto (mstsc)."
    except FileNotFoundError:
        return "mstsc não encontrado. Verifique se a Área de Trabalho Remota está instalada."
    except Exception as exc:  # pragma: no cover
        return f"Erro ao abrir área de trabalho remota: {exc}"


def speak_text(text: str) -> str:
    """Lê um texto em voz alta usando TTS local (pyttsx3).

    Dependências: pyttsx3 instalada no ambiente Python.
    """

    if not text.strip():
        return "Nenhum texto para ler."

    try:
        import pyttsx3  # type: ignore

        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        return "Texto enviado para síntese de voz."
    except Exception as exc:  # pragma: no cover
        return f"Erro ao usar TTS local: {exc}"


def describe_tools() -> str:
    return (
        "Ferramentas disponíveis:\n"
        "- run_shell_command: executa comandos de terminal locais.\n"
        "- open_url: abre uma URL no navegador padrão (modo legado).\n"
        "- open_remote_desktop: abre o cliente de RDP (Windows).\n"
        "- speak_text: lê um texto em voz alta via TTS local.\n"
        "- market analysis/paper trading: analisa acoes, forex e criptos com sizing modelado em BRL e carteira simulada.\n"
        "- browser_enable/browser_disable: abre/fecha janela interna do agente para automacao web.\n"
        "- browser_open_url/browser_click/browser_type/browser_extract_text/browser_wait: operacoes web na janela interna.\n"
        "- browser_snapshot/browser_click_at/browser_type_text/browser_press_key/browser_search_current_page: suporte a navegador embutido no painel web.\n"
        "- browser_click_text/browser_click_first_result/browser_click_best_result/browser_extract_page_text/browser_go_back/browser_go_forward/browser_refresh: automacoes naturais na pagina aberta.\n"
        "\nImportante: ações sensíveis (logins, candidaturas, etc.) devem ser revisadas\n"
        "e confirmadas por você antes de executar comandos sugeridos pelo agente.\n"
    )
