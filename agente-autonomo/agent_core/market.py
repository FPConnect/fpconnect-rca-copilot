from __future__ import annotations

import json
import math
import csv
import io
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import pstdev
from urllib.error import HTTPError
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

from .config import settings
from .finance_knowledge import FINANCE_STUDY_TRACKS


DEFAULT_UNIVERSE = [
    "AAPL",
    "MSFT",
    "NVDA",
    "AMZN",
    "GOOGL",
    "META",
    "TSLA",
    "BRK-B",
    "JPM",
    "TSM",
    "ASML",
    "SAP",
    "PETR4.SA",
    "VALE3.SA",
    "BTC-USD",
    "ETH-USD",
    "EURUSD=X",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _http_get_json(url: str) -> dict:
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Accept": "application/json,text/plain,*/*",
        },
    )
    with urlopen(request, timeout=12) as response:
        payload = response.read().decode("utf-8", errors="ignore")
    data = json.loads(payload)
    if not isinstance(data, dict):
        raise ValueError("Resposta JSON invalida")
    return data


def _safe_float(value: object) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _round_down(value: float, decimals: int = 6) -> float:
    if value <= 0:
        return 0.0
    factor = 10**decimals
    return math.floor(value * factor) / factor


def _sma(values: list[float], period: int) -> float | None:
    if len(values) < period:
        return None
    window = values[-period:]
    return sum(window) / period


def _rsi(values: list[float], period: int = 14) -> float | None:
    if len(values) < period + 1:
        return None
    gains: list[float] = []
    losses: list[float] = []
    for previous, current in zip(values[-period - 1 : -1], values[-period:]):
        delta = current - previous
        gains.append(max(delta, 0.0))
        losses.append(abs(min(delta, 0.0)))
    average_gain = sum(gains) / period
    average_loss = sum(losses) / period
    if average_loss == 0:
        return 100.0
    relative_strength = average_gain / average_loss
    return 100.0 - (100.0 / (1.0 + relative_strength))


def _atr(highs: list[float], lows: list[float], closes: list[float], period: int = 14) -> float | None:
    if len(closes) < period + 1 or len(highs) != len(lows) or len(lows) != len(closes):
        return None
    ranges: list[float] = []
    for index in range(1, len(closes)):
        current_high = highs[index]
        current_low = lows[index]
        previous_close = closes[index - 1]
        true_range = max(
            current_high - current_low,
            abs(current_high - previous_close),
            abs(current_low - previous_close),
        )
        ranges.append(true_range)
    if len(ranges) < period:
        return None
    return sum(ranges[-period:]) / period


def _annualized_volatility(closes: list[float], period: int = 20) -> float | None:
    if len(closes) < period + 1:
        return None
    returns: list[float] = []
    for previous, current in zip(closes[-period - 1 : -1], closes[-period:]):
        if previous <= 0:
            continue
        returns.append((current / previous) - 1.0)
    if len(returns) < 2:
        return None
    return pstdev(returns) * math.sqrt(252.0) * 100.0


def _infer_quote_currency(symbol: str, payload: dict) -> str:
    raw_currency = str(payload.get("currency") or "").strip().upper()
    if raw_currency:
        return raw_currency
    if symbol.endswith(".SA"):
        return "BRL"
    if symbol.endswith("=X") and len(symbol) >= 7:
        return symbol[3:6].upper()
    if "-" in symbol:
        return symbol.rsplit("-", 1)[1].upper()
    return "USD"


def _infer_asset_type(symbol: str, payload: dict) -> str:
    quote_type = str(payload.get("quoteType") or "").upper()
    if quote_type == "CRYPTOCURRENCY":
        return "crypto"
    if symbol.endswith("=X"):
        return "forex"
    if "-" in symbol and symbol.rsplit("-", 1)[-1].upper() in {"USD", "BRL", "EUR", "USDT"}:
        return "crypto"
    return "equity"


def _to_stooq_symbol(symbol: str) -> str | None:
    normalized = symbol.strip().upper()
    if not normalized:
        return None
    if normalized.endswith(".SA"):
        return normalized[:-3].lower() + ".br"
    if normalized.endswith("=X"):
        # Stooq uses plain pair symbols for major FX pairs.
        return normalized.replace("=X", "").lower()
    if "-" in normalized:
        # Crypto and other dashed symbols are inconsistent on Stooq; skip fallback.
        return None
    if normalized.replace("-", "").isalnum():
        return normalized.lower() + ".us"
    return None


def _fetch_stooq_csv_rows(stooq_symbol: str, historical: bool = False) -> list[dict[str, str]]:
    suffix = "/q/d/l/" if historical else "/q/l/"
    url = f"https://stooq.com{suffix}?s={quote_plus(stooq_symbol)}&i=d"
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "text/csv,*/*",
        },
    )
    with urlopen(request, timeout=12) as response:
        payload = response.read().decode("utf-8", errors="ignore")
    cleaned = payload.strip()
    if not cleaned:
        return []
    if not historical and not cleaned.lower().startswith("symbol,"):
        cleaned = "Symbol,Date,Time,Open,High,Low,Close,Volume\n" + cleaned
    reader = csv.DictReader(io.StringIO(cleaned))
    rows = [row for row in reader if isinstance(row, dict)]
    return rows


def _fetch_quote_from_stooq(symbol: str) -> QuoteSnapshot | None:
    stooq_symbol = _to_stooq_symbol(symbol)
    if not stooq_symbol:
        return None
    rows = _fetch_stooq_csv_rows(stooq_symbol, historical=False)
    if not rows:
        return None
    row = rows[0]
    close_price = _safe_float(row.get("Close"))
    open_price = _safe_float(row.get("Open"))
    if close_price is None or close_price <= 0:
        return None
    change_percent = None
    if open_price is not None and open_price > 0:
        change_percent = ((close_price / open_price) - 1.0) * 100.0

    return QuoteSnapshot(
        symbol=symbol.upper(),
        name=symbol.upper(),
        exchange="Stooq",
        currency="BRL" if symbol.upper().endswith(".SA") else "USD",
        asset_type="forex" if symbol.upper().endswith("=X") else "equity",
        price=close_price,
        previous_close=open_price,
        change_percent=change_percent,
        market_state="REGULAR",
        fetched_at=_now_iso(),
    )


def _fetch_history_from_stooq(symbol: str) -> tuple[list[float], list[float], list[float]] | None:
    stooq_symbol = _to_stooq_symbol(symbol)
    if not stooq_symbol:
        return None
    rows = _fetch_stooq_csv_rows(stooq_symbol, historical=True)
    if not rows:
        return None

    closes: list[float] = []
    highs: list[float] = []
    lows: list[float] = []
    for row in rows:
        close_value = _safe_float(row.get("Close"))
        high_value = _safe_float(row.get("High"))
        low_value = _safe_float(row.get("Low"))
        if close_value is None or high_value is None or low_value is None:
            continue
        if close_value <= 0 or high_value <= 0 or low_value <= 0:
            continue
        closes.append(close_value)
        highs.append(high_value)
        lows.append(low_value)

    # Stooq usually returns most-recent first; normalize to oldest->newest.
    if len(closes) >= 2 and closes[0] != closes[-1]:
        closes.reverse()
        highs.reverse()
        lows.reverse()

    if len(closes) < 60:
        return None
    return closes, highs, lows


@dataclass
class QuoteSnapshot:
    symbol: str
    name: str
    exchange: str
    currency: str
    asset_type: str
    price: float
    previous_close: float | None
    change_percent: float | None
    market_state: str
    fetched_at: str


@dataclass
class MarketAnalysis:
    quote: QuoteSnapshot
    sma20: float | None
    sma50: float | None
    rsi14: float | None
    atr14: float | None
    momentum_20d_pct: float | None
    volatility_20d_pct: float | None
    action: str
    confidence: str
    reasons: list[str]


@dataclass
class TradePlan:
    approved: bool
    symbol: str
    entry_price: float
    stop_price: float
    target_price: float
    quantity: float
    currency: str
    fx_rate_brl: float
    notional_brl: float
    modeled_profit_brl: float
    modeled_loss_brl: float
    action: str
    rationale: str


@dataclass
class PaperPosition:
    symbol: str
    quantity: float
    entry_price: float
    stop_price: float
    target_price: float
    currency: str
    fx_rate_brl: float
    opened_at: str
    rationale: str


@dataclass
class ClosedPaperTrade:
    symbol: str
    quantity: float
    entry_price: float
    exit_price: float
    currency: str
    realized_pnl_brl: float
    exit_reason: str
    opened_at: str
    closed_at: str


@dataclass
class PaperState:
    cash_brl: float
    positions: list[PaperPosition]
    closed_trades: list[ClosedPaperTrade]
    updated_at: str


def _empty_paper_state() -> PaperState:
    return PaperState(
        cash_brl=float(settings.paper_initial_cash_brl),
        positions=[],
        closed_trades=[],
        updated_at=_now_iso(),
    )


def load_paper_state(path: Path | None = None) -> PaperState:
    state_path = path or settings.market_state_path
    state_path.parent.mkdir(parents=True, exist_ok=True)
    if not state_path.exists():
        return _empty_paper_state()
    try:
        payload = json.loads(state_path.read_text(encoding="utf-8"))
        positions = [PaperPosition(**item) for item in payload.get("positions", []) if isinstance(item, dict)]
        closed_trades = [ClosedPaperTrade(**item) for item in payload.get("closed_trades", []) if isinstance(item, dict)]
        return PaperState(
            cash_brl=float(payload.get("cash_brl", settings.paper_initial_cash_brl)),
            positions=positions,
            closed_trades=closed_trades,
            updated_at=str(payload.get("updated_at") or _now_iso()),
        )
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return _empty_paper_state()


def save_paper_state(state: PaperState, path: Path | None = None) -> None:
    state_path = path or settings.market_state_path
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state.updated_at = _now_iso()
    payload = json.dumps(asdict(state), ensure_ascii=False, indent=2)
    state_path.write_text(payload, encoding="utf-8")


def fetch_quote(symbol: str) -> QuoteSnapshot:
    encoded = quote_plus(symbol)
    try:
        data = _http_get_json(f"https://query2.finance.yahoo.com/v7/finance/quote?symbols={encoded}")
    except HTTPError as exc:
        if int(getattr(exc, "code", 0)) == 401:
            fallback = _fetch_quote_from_stooq(symbol)
            if fallback is not None:
                return fallback
        raise
    results = data.get("quoteResponse", {}).get("result", [])
    if not results:
        raise ValueError(f"Nao encontrei cotacao para {symbol}")
    payload = results[0]
    price = _safe_float(
        payload.get("regularMarketPrice")
        or payload.get("postMarketPrice")
        or payload.get("preMarketPrice")
    )
    if price is None or price <= 0:
        raise ValueError(f"Cotacao invalida para {symbol}")
    return QuoteSnapshot(
        symbol=symbol.upper(),
        name=str(payload.get("longName") or payload.get("shortName") or payload.get("displayName") or symbol.upper()),
        exchange=str(payload.get("fullExchangeName") or payload.get("exchange") or "mercado externo"),
        currency=_infer_quote_currency(symbol.upper(), payload),
        asset_type=_infer_asset_type(symbol.upper(), payload),
        price=price,
        previous_close=_safe_float(payload.get("regularMarketPreviousClose") or payload.get("previousClose")),
        change_percent=_safe_float(payload.get("regularMarketChangePercent")),
        market_state=str(payload.get("marketState") or "UNKNOWN"),
        fetched_at=_now_iso(),
    )


def fetch_history(symbol: str, period: str = "6mo", interval: str = "1d") -> tuple[list[float], list[float], list[float]]:
    encoded = quote_plus(symbol)
    try:
        data = _http_get_json(
            "https://query2.finance.yahoo.com/v8/finance/chart/"
            f"{encoded}?interval={quote_plus(interval)}&range={quote_plus(period)}&includePrePost=false"
        )
    except HTTPError as exc:
        if int(getattr(exc, "code", 0)) == 401:
            fallback = _fetch_history_from_stooq(symbol)
            if fallback is not None:
                return fallback
        raise
    results = data.get("chart", {}).get("result", [])
    if not results:
        raise ValueError(f"Nao encontrei historico para {symbol}")
    indicators = results[0].get("indicators", {}).get("quote", [])
    if not indicators:
        raise ValueError(f"Historico invalido para {symbol}")
    payload = indicators[0]
    raw_closes = payload.get("close", [])
    raw_highs = payload.get("high", [])
    raw_lows = payload.get("low", [])

    closes: list[float] = []
    highs: list[float] = []
    lows: list[float] = []
    for close_value, high_value, low_value in zip(raw_closes, raw_highs, raw_lows):
        close_float = _safe_float(close_value)
        high_float = _safe_float(high_value)
        low_float = _safe_float(low_value)
        if close_float is None or high_float is None or low_float is None:
            continue
        closes.append(close_float)
        highs.append(high_float)
        lows.append(low_float)
    if len(closes) < 60:
        raise ValueError(f"Historico insuficiente para {symbol}")
    return closes, highs, lows


def fetch_brl_fx_rate(currency: str) -> float:
    normalized = currency.strip().upper()
    if not normalized or normalized == "BRL":
        return 1.0
    try:
        data = _http_get_json(f"https://api.frankfurter.app/latest?from={normalized}&to=BRL")
        rate = _safe_float((data.get("rates") or {}).get("BRL"))
    except Exception:
        data = _http_get_json(f"https://open.er-api.com/v6/latest/{normalized}")
        rate = _safe_float((data.get("rates") or {}).get("BRL"))
    if rate is None or rate <= 0:
        raise ValueError(f"Nao consegui converter {normalized} para BRL")
    return rate


def analyze_symbol(symbol: str) -> MarketAnalysis:
    quote = fetch_quote(symbol)
    closes, highs, lows = fetch_history(symbol)

    sma20 = _sma(closes, 20)
    sma50 = _sma(closes, 50)
    rsi14 = _rsi(closes, 14)
    atr14 = _atr(highs, lows, closes, 14)
    volatility_20d_pct = _annualized_volatility(closes, 20)
    momentum_20d_pct = None
    if len(closes) >= 21 and closes[-21] > 0:
        momentum_20d_pct = ((closes[-1] / closes[-21]) - 1.0) * 100.0

    reasons: list[str] = []
    action = "wait"
    confidence = "baixa"

    if sma20 is not None and sma50 is not None and quote.price > sma20 > sma50:
        reasons.append("preco acima das medias de 20 e 50 dias")
    if momentum_20d_pct is not None:
        if momentum_20d_pct > 3:
            reasons.append("momentum de 20 dias positivo")
        elif momentum_20d_pct < -3:
            reasons.append("momentum de 20 dias negativo")
    if rsi14 is not None:
        if rsi14 > 72:
            reasons.append("RSI alto, ativo esticado")
        elif rsi14 < 35:
            reasons.append("RSI baixo, ativo pressionado")

    if sma20 is not None and sma50 is not None and momentum_20d_pct is not None:
        if quote.price > sma20 > sma50 and momentum_20d_pct > 1.5 and (rsi14 or 0) < 72:
            action = "buy"
            confidence = "alta"
        elif quote.price > sma20 and momentum_20d_pct > 0:
            action = "watch"
            confidence = "media"
        elif quote.price < sma20 < sma50 and momentum_20d_pct < -2:
            action = "avoid"
            confidence = "media"

    if volatility_20d_pct is not None and volatility_20d_pct > 65:
        reasons.append("volatilidade anualizada elevada")
        if action == "buy":
            action = "watch"
            confidence = "media"

    if not reasons:
        reasons.append("sem alinhamento tecnico suficiente")

    return MarketAnalysis(
        quote=quote,
        sma20=sma20,
        sma50=sma50,
        rsi14=rsi14,
        atr14=atr14,
        momentum_20d_pct=momentum_20d_pct,
        volatility_20d_pct=volatility_20d_pct,
        action=action,
        confidence=confidence,
        reasons=reasons,
    )


def build_trade_plan(symbol: str, profit_floor_brl: float = 100.0, max_loss_brl: float = 50.0) -> TradePlan:
    analysis = analyze_symbol(symbol)
    quote = analysis.quote

    if analysis.action != "buy":
        return TradePlan(
            approved=False,
            symbol=quote.symbol,
            entry_price=quote.price,
            stop_price=0.0,
            target_price=0.0,
            quantity=0.0,
            currency=quote.currency,
            fx_rate_brl=1.0,
            notional_brl=0.0,
            modeled_profit_brl=0.0,
            modeled_loss_brl=0.0,
            action=analysis.action,
            rationale="Estrutura tecnica ainda nao sinaliza compra com qualidade suficiente.",
        )

    if analysis.atr14 is None or analysis.atr14 <= 0:
        return TradePlan(
            approved=False,
            symbol=quote.symbol,
            entry_price=quote.price,
            stop_price=0.0,
            target_price=0.0,
            quantity=0.0,
            currency=quote.currency,
            fx_rate_brl=1.0,
            notional_brl=0.0,
            modeled_profit_brl=0.0,
            modeled_loss_brl=0.0,
            action="wait",
            rationale="ATR insuficiente para modelar stop tecnico.",
        )

    fx_rate_brl = fetch_brl_fx_rate(quote.currency)
    stop_distance = max(analysis.atr14 * 1.2, quote.price * 0.006)
    raw_quantity = max_loss_brl / (stop_distance * fx_rate_brl)
    quantity = _round_down(raw_quantity, decimals=6)
    if quantity <= 0:
        return TradePlan(
            approved=False,
            symbol=quote.symbol,
            entry_price=quote.price,
            stop_price=0.0,
            target_price=0.0,
            quantity=0.0,
            currency=quote.currency,
            fx_rate_brl=fx_rate_brl,
            notional_brl=0.0,
            modeled_profit_brl=0.0,
            modeled_loss_brl=0.0,
            action="wait",
            rationale="Quantidade calculada ficou abaixo do minimo pratico.",
        )

    required_target_distance = profit_floor_brl / max(quantity * fx_rate_brl, 1e-9)
    target_distance = max(required_target_distance, stop_distance * 2.05)
    stop_price = max(quote.price - stop_distance, 0.0)
    target_price = quote.price + target_distance
    modeled_loss_brl = quantity * stop_distance * fx_rate_brl
    modeled_profit_brl = quantity * target_distance * fx_rate_brl
    notional_brl = quantity * quote.price * fx_rate_brl

    approved = modeled_profit_brl >= profit_floor_brl and modeled_loss_brl <= max_loss_brl + 0.01
    rationale = (
        "Plano aprovado para paper trading. O alvo modelado atende piso de lucro em BRL e o stop modelado respeita o teto de perda em BRL. "
        "Isso nao elimina gap, slippage, latencia nem risco de execucao real."
    )
    if not approved:
        rationale = "Nao consegui montar um plano que respeite simultaneamente piso de lucro modelado e teto de perda modelada em BRL."

    return TradePlan(
        approved=approved,
        symbol=quote.symbol,
        entry_price=quote.price,
        stop_price=stop_price,
        target_price=target_price,
        quantity=quantity,
        currency=quote.currency,
        fx_rate_brl=fx_rate_brl,
        notional_brl=notional_brl,
        modeled_profit_brl=modeled_profit_brl,
        modeled_loss_brl=modeled_loss_brl,
        action=analysis.action,
        rationale=rationale,
    )


def _render_indicator(name: str, value: float | None, suffix: str = "") -> str:
    if value is None:
        return f"- {name}: n/d"
    return f"- {name}: {value:.2f}{suffix}"


def render_analysis(symbol: str) -> str:
    analysis = analyze_symbol(symbol)
    quote = analysis.quote
    lines = [
        f"Analise de {quote.symbol} | {quote.name}",
        f"- Mercado: {quote.exchange}",
        f"- Classe: {quote.asset_type}",
        f"- Preco atual: {quote.price:.4f} {quote.currency}",
        _render_indicator("SMA20", analysis.sma20),
        _render_indicator("SMA50", analysis.sma50),
        _render_indicator("RSI14", analysis.rsi14),
        _render_indicator("ATR14", analysis.atr14),
        _render_indicator("Momentum 20d", analysis.momentum_20d_pct, "%"),
        _render_indicator("Volatilidade 20d anualizada", analysis.volatility_20d_pct, "%"),
        f"- Acao sugerida: {analysis.action} ({analysis.confidence})",
        f"- Sinais: {'; '.join(analysis.reasons[:4])}",
        "- Aviso: esta leitura e tecnica e educacional. Nao existe garantia de lucro minimo nem limite absoluto de perda em mercado real.",
    ]
    return "\n".join(lines)


def render_trade_plan(symbol: str) -> str:
    plan = build_trade_plan(symbol)
    if not plan.approved:
        return (
            f"Plano de trade para {plan.symbol}\n"
            f"- Status: bloqueado\n"
            f"- Motivo: {plan.rationale}\n"
            "- Observacao: o agente so aprova trades simulados quando o modelo consegue manter alvo >= R$ 100 e perda modelada <= R$ 50 em BRL. Isso nao e garantia no mercado real."
        )

    return (
        f"Plano de trade para {plan.symbol}\n"
        f"- Status: aprovado para paper trading\n"
        f"- Entrada: {plan.entry_price:.4f} {plan.currency}\n"
        f"- Stop tecnico: {plan.stop_price:.4f} {plan.currency}\n"
        f"- Alvo tecnico: {plan.target_price:.4f} {plan.currency}\n"
        f"- Quantidade: {plan.quantity:.6f}\n"
        f"- Notional estimado: R$ {plan.notional_brl:.2f}\n"
        f"- Lucro modelado no alvo: R$ {plan.modeled_profit_brl:.2f}\n"
        f"- Perda modelada no stop: R$ {plan.modeled_loss_brl:.2f}\n"
        f"- FX para BRL: {plan.fx_rate_brl:.4f}\n"
        f"- Nota: {plan.rationale}"
    )


def _position_unrealized_pnl_brl(position: PaperPosition, current_price: float) -> float:
    return (current_price - position.entry_price) * position.quantity * position.fx_rate_brl


def open_paper_trade(symbol: str) -> str:
    if settings.allow_live_trading:
        return "Execucao real segue desabilitada neste modulo. A implementacao atual opera apenas paper trading com supervisao explicita."

    state = load_paper_state()
    if any(position.symbol.upper() == symbol.upper() for position in state.positions):
        return f"Ja existe posicao aberta em {symbol.upper()} na carteira simulada."

    plan = build_trade_plan(symbol)
    if not plan.approved:
        return render_trade_plan(symbol)

    if plan.notional_brl > state.cash_brl:
        return (
            f"Trade bloqueado para {plan.symbol}. Caixa atual da carteira simulada: R$ {state.cash_brl:.2f}. "
            f"Notional necessario: R$ {plan.notional_brl:.2f}."
        )

    position = PaperPosition(
        symbol=plan.symbol,
        quantity=plan.quantity,
        entry_price=plan.entry_price,
        stop_price=plan.stop_price,
        target_price=plan.target_price,
        currency=plan.currency,
        fx_rate_brl=plan.fx_rate_brl,
        opened_at=_now_iso(),
        rationale=plan.rationale,
    )
    state.cash_brl -= plan.notional_brl
    state.positions.append(position)
    save_paper_state(state)

    return (
        f"Paper trade aberto em {plan.symbol}.\n"
        f"- Quantidade: {plan.quantity:.6f}\n"
        f"- Entrada simulada: {plan.entry_price:.4f} {plan.currency}\n"
        f"- Stop: {plan.stop_price:.4f} {plan.currency}\n"
        f"- Alvo: {plan.target_price:.4f} {plan.currency}\n"
        f"- Caixa restante: R$ {state.cash_brl:.2f}"
    )


def close_paper_trade(symbol: str, reason: str = "saida manual") -> str:
    state = load_paper_state()
    for index, position in enumerate(state.positions):
        if position.symbol.upper() != symbol.upper():
            continue
        quote = fetch_quote(position.symbol)
        exit_price = quote.price
        realized_pnl_brl = _position_unrealized_pnl_brl(position, exit_price)
        exit_value_brl = position.quantity * exit_price * position.fx_rate_brl
        state.cash_brl += exit_value_brl
        state.closed_trades.append(
            ClosedPaperTrade(
                symbol=position.symbol,
                quantity=position.quantity,
                entry_price=position.entry_price,
                exit_price=exit_price,
                currency=position.currency,
                realized_pnl_brl=realized_pnl_brl,
                exit_reason=reason,
                opened_at=position.opened_at,
                closed_at=_now_iso(),
            )
        )
        state.positions.pop(index)
        save_paper_state(state)
        return (
            f"Posicao simulada encerrada em {position.symbol}.\n"
            f"- Saida: {exit_price:.4f} {position.currency}\n"
            f"- PnL realizado: R$ {realized_pnl_brl:.2f}\n"
            f"- Caixa atual: R$ {state.cash_brl:.2f}"
        )
    return f"Nao encontrei posicao aberta em {symbol.upper()} na carteira simulada."


def sync_paper_trades() -> str:
    state = load_paper_state()
    if not state.positions:
        return "Nao ha posicoes abertas para sincronizar na carteira simulada."

    events: list[str] = []
    remaining_positions: list[PaperPosition] = []
    for position in state.positions:
        quote = fetch_quote(position.symbol)
        current_price = quote.price
        close_reason = ""
        if current_price <= position.stop_price:
            close_reason = "stop atingido"
        elif current_price >= position.target_price:
            close_reason = "alvo atingido"

        if not close_reason:
            unrealized = _position_unrealized_pnl_brl(position, current_price)
            events.append(
                f"- {position.symbol}: aberto | preco={current_price:.4f} {position.currency} | PnL nao realizado=R$ {unrealized:.2f}"
            )
            remaining_positions.append(position)
            continue

        realized_pnl_brl = _position_unrealized_pnl_brl(position, current_price)
        exit_value_brl = position.quantity * current_price * position.fx_rate_brl
        state.cash_brl += exit_value_brl
        state.closed_trades.append(
            ClosedPaperTrade(
                symbol=position.symbol,
                quantity=position.quantity,
                entry_price=position.entry_price,
                exit_price=current_price,
                currency=position.currency,
                realized_pnl_brl=realized_pnl_brl,
                exit_reason=close_reason,
                opened_at=position.opened_at,
                closed_at=_now_iso(),
            )
        )
        events.append(
            f"- {position.symbol}: encerrado automaticamente ({close_reason}) | saida={current_price:.4f} {position.currency} | PnL=R$ {realized_pnl_brl:.2f}"
        )

    state.positions = remaining_positions
    save_paper_state(state)
    header = f"Sincronizacao concluida. Caixa atual: R$ {state.cash_brl:.2f}"
    return "\n".join([header, *events])


def render_portfolio() -> str:
    state = load_paper_state()
    lines = [
        "Carteira simulada",
        f"- Caixa BRL: R$ {state.cash_brl:.2f}",
        f"- Posicoes abertas: {len(state.positions)}",
        f"- Trades encerrados: {len(state.closed_trades)}",
    ]
    if not state.positions:
        lines.append("- Nenhuma posicao aberta no momento.")
        return "\n".join(lines)

    gross_exposure = 0.0
    for position in state.positions:
        quote = fetch_quote(position.symbol)
        exposure_brl = position.quantity * quote.price * position.fx_rate_brl
        unrealized = _position_unrealized_pnl_brl(position, quote.price)
        gross_exposure += exposure_brl
        lines.append(
            f"- {position.symbol}: qty={position.quantity:.6f} | entrada={position.entry_price:.4f} | atual={quote.price:.4f} {position.currency} | stop={position.stop_price:.4f} | alvo={position.target_price:.4f} | PnL=R$ {unrealized:.2f}"
        )
    lines.append(f"- Exposicao bruta estimada: R$ {gross_exposure:.2f}")
    lines.append("- Aviso: carteira simulada. Nao ha roteamento para corretora real nesta versao.")
    return "\n".join(lines)


def render_universe(symbols: list[str] | None = None) -> str:
    selected = symbols or DEFAULT_UNIVERSE
    scored: list[tuple[int, str]] = []
    for symbol in selected:
        try:
            analysis = analyze_symbol(symbol)
            score = {"buy": 3, "watch": 2, "wait": 1, "avoid": 0}.get(analysis.action, 0)
            line = (
                f"- {analysis.quote.symbol}: {analysis.action} ({analysis.confidence}) | "
                f"preco={analysis.quote.price:.4f} {analysis.quote.currency} | "
                f"mom20={analysis.momentum_20d_pct:.2f}% | RSI={analysis.rsi14:.2f}"
                if analysis.momentum_20d_pct is not None and analysis.rsi14 is not None
                else f"- {analysis.quote.symbol}: {analysis.action} ({analysis.confidence}) | preco={analysis.quote.price:.4f} {analysis.quote.currency}"
            )
            scored.append((score, line))
        except Exception as exc:
            scored.append((0, f"- {symbol.upper()}: falha na analise ({exc})"))
    scored.sort(key=lambda item: item[0], reverse=True)
    return "\n".join(["Radar global de mercado", *[line for _, line in scored]])


def market_help_text() -> str:
    return (
        "Comandos de mercado:\n"
        "- mercado: analisar <ticker>   -> analise tecnica rapida de uma acao, forex ou cripto.\n"
        "- mercado: plano <ticker>      -> monta um plano de paper trade com piso modelado >= R$ 100 e risco modelado <= R$ 50.\n"
        "- mercado: comprar <ticker>    -> abre uma posicao simulada se o plano passar nas regras.\n"
        "- mercado: vender <ticker>     -> encerra manualmente uma posicao simulada.\n"
        "- mercado: carteira            -> mostra caixa e posicoes do paper trading.\n"
        "- mercado: atualizar           -> sincroniza stops/alvos das posicoes simuladas.\n"
        "- mercado: universo            -> faz um radar das principais empresas/ativos globais do universo padrao.\n"
        "- mercado: ranking AAPL,MSFT   -> analisa uma lista customizada de tickers.\n"
        "- mercado: trilha iniciante    -> guia de estudo para quem esta comecando.\n"
        "- mercado: trilha fundamentalista -> guia de estudo focado em fundamentos.\n"
        "- mercado: trilha trader       -> guia de estudo focado em operacao e risco.\n"
        "\nImportante: mercado real nao permite garantir lucro minimo nem perda maxima absoluta. Esta versao implementa analise e paper trading com travas modeladas em BRL; execucao real permanece fora do escopo por seguranca."
    )


def market_study_help_text() -> str:
    return (
        "Trilhas de estudo disponiveis:\n"
        "- mercado: trilha iniciante\n"
        "- mercado: trilha fundamentalista\n"
        "- mercado: trilha trader"
    )


def render_study_track(track: str) -> str:
    normalized = track.strip().lower()
    if not normalized:
        return market_study_help_text()

    if normalized in {"fundamento", "fundamentos", "fundamental"}:
        normalized = "fundamentalista"
    if normalized in {"operacional", "operacao", "operação", "trade"}:
        normalized = "trader"
    if normalized in {"inicio", "comecar", "começar", "basico", "básico"}:
        normalized = "iniciante"

    payload = FINANCE_STUDY_TRACKS.get(normalized)
    if not payload:
        return market_study_help_text()

    title, steps = payload
    return "\n".join([title, *steps])


def handle_market_command(command: str) -> str | None:
    lowered = command.strip().lower()
    if not lowered:
        return None

    aliases = (
        "mercado:",
        "trading:",
        "trade:",
        "acoes:",
        "ações:",
    )
    if lowered in {"mercado", "trading", "trade"}:
        return market_help_text()
    if lowered in {"mercado: help", "mercado: ajuda", "trading: help", "trading: ajuda"}:
        return market_help_text()
    if not lowered.startswith(aliases):
        return None

    _, _, payload = command.partition(":")
    action = payload.strip()
    lowered_action = action.lower()

    if lowered_action in {"help", "ajuda"}:
        return market_help_text()
    if lowered_action.startswith("analisar "):
        return render_analysis(action[9:].strip())
    if lowered_action.startswith("plano "):
        return render_trade_plan(action[6:].strip())
    if lowered_action.startswith("comprar "):
        return open_paper_trade(action[8:].strip())
    if lowered_action.startswith("vender "):
        return close_paper_trade(action[7:].strip())
    if lowered_action in {"carteira", "portfolio", "portifolio"}:
        return render_portfolio()
    if lowered_action in {"atualizar", "sincronizar", "sync"}:
        return sync_paper_trades()
    if lowered_action in {"universo", "radar"}:
        return render_universe()
    if lowered_action.startswith("ranking "):
        raw_symbols = action[8:].strip()
        symbols = [item.strip().upper() for item in raw_symbols.split(",") if item.strip()]
        if not symbols:
            return "Lista vazia. Use: mercado: ranking AAPL,MSFT,NVDA"
        return render_universe(symbols)
    if lowered_action in {"trilha", "estudar", "estudo", "trilhas"}:
        return market_study_help_text()
    if lowered_action.startswith("trilha "):
        return render_study_track(action[7:].strip())
    if lowered_action.startswith("estudar "):
        return render_study_track(action[8:].strip())
    return market_help_text()