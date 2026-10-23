"""Generate authenticated equipment reports from records stored by OPSPECTA."""

from __future__ import annotations

import io
import re
from html import escape
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

NAVY = colors.HexColor("#031B3B")
CYAN = colors.HexColor("#11C5D9")
TEAL = colors.HexColor("#009BA8")
INK = colors.HexColor("#172033")
MUTED = colors.HexColor("#56657A")
LINE = colors.HexColor("#D7E1EC")
SURFACE = colors.HexColor("#F4F8FC")
WARNING = colors.HexColor("#B45309")
CRITICAL = colors.HexColor("#B4233C")
SUCCESS = colors.HexColor("#087A55")

ASSET_DIR = Path(__file__).resolve().parents[1] / "assets"
LOGO_PATH = ASSET_DIR / "opspecta-logo.png"
FONT_REGULAR_PATH = ASSET_DIR / "fonts" / "Manrope-Regular.ttf"
FONT_BOLD_PATH = ASSET_DIR / "fonts" / "Manrope-Bold.ttf"
FONT_REGULAR = "OpspectaManrope"
FONT_BOLD = "OpspectaManropeBold"


def _register_fonts() -> None:
    registered = set(pdfmetrics.getRegisteredFontNames())
    if FONT_REGULAR not in registered:
        pdfmetrics.registerFont(TTFont(FONT_REGULAR, FONT_REGULAR_PATH))
    if FONT_BOLD not in registered:
        pdfmetrics.registerFont(TTFont(FONT_BOLD, FONT_BOLD_PATH))


@dataclass(frozen=True)
class EquipmentRecord:
    """Equipment fields persisted in the platform."""

    code: str
    name: str
    model: str | None
    location: str
    equipment_type: str
    status: str
    criticality: str
    last_failure: str | None
    recurrent_failures: int
    last_check: datetime | None


@dataclass(frozen=True)
class TicketRecord:
    """Ticket fields that may be included in an equipment report."""

    ticket_id: int
    title: str
    status: str
    priority: str
    created_at: datetime | None
    root_cause: str | None
    recommendation: str | None


def _safe_text(value: object, maximum: int = 500) -> str:
    text = " ".join(str(value or "-").split())
    if len(text) <= maximum:
        return escape(text, quote=False)
    return escape(f"{text[: maximum - 3].rstrip()}...", quote=False)


def _safe_code(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-._")
    return safe[:48] or "equipamento"


def _format_datetime(value: datetime | None) -> str:
    if value is None:
        return "Não informado"
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).strftime("%d/%m/%Y %H:%M UTC")


def _status_label(status: str) -> tuple[str, colors.Color]:
    labels = {
        "online": ("OPERACIONAL", SUCCESS),
        "warning": ("ATENÇÃO", WARNING),
        "offline": ("INDISPONÍVEL", CRITICAL),
    }
    return labels.get(status, (_safe_text(status, 30).upper(), MUTED))


def _ticket_status(status: str) -> str:
    return {
        "open": "Aberto",
        "in_progress": "Em andamento",
        "resolved": "Resolvido",
        "closed": "Encerrado",
    }.get(status, _safe_text(status, 30))


def _priority_label(priority: str) -> str:
    return {
        "low": "Baixa",
        "medium": "Média",
        "high": "Alta",
        "critical": "Crítica",
    }.get(priority, _safe_text(priority, 30))


def normalize_criticality(value: str) -> str:
    """Repair known legacy encodings before rendering a report."""
    normalized = value.strip().casefold()
    if normalized in {"m?dia", "média", "media", "mã©dia"}:
        return "Média"
    if normalized in {"cr?tica", "crítica", "critica", "crãtica"}:
        return "Crítica"
    return value


def _styles() -> dict[str, ParagraphStyle]:
    _register_fonts()
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "EquipmentTitle",
            parent=base["Heading1"],
            fontName=FONT_BOLD,
            fontSize=22,
            leading=27,
            textColor=NAVY,
            spaceAfter=5 * mm,
        ),
        "subtitle": ParagraphStyle(
            "EquipmentSubtitle",
            parent=base["BodyText"],
            fontName=FONT_REGULAR,
            fontSize=9,
            leading=13,
            textColor=MUTED,
        ),
        "section": ParagraphStyle(
            "EquipmentSection",
            parent=base["Heading2"],
            fontName=FONT_BOLD,
            fontSize=12,
            leading=15,
            textColor=NAVY,
            spaceBefore=4 * mm,
            spaceAfter=2.5 * mm,
        ),
        "body": ParagraphStyle(
            "EquipmentBody",
            parent=base["BodyText"],
            fontName=FONT_REGULAR,
            fontSize=8.5,
            leading=12,
            textColor=INK,
        ),
        "small": ParagraphStyle(
            "EquipmentSmall",
            parent=base["BodyText"],
            fontName=FONT_REGULAR,
            fontSize=7.3,
            leading=10,
            textColor=MUTED,
        ),
        "label": ParagraphStyle(
            "EquipmentLabel",
            parent=base["BodyText"],
            fontName=FONT_BOLD,
            fontSize=7.2,
            leading=9,
            textColor=TEAL,
        ),
        "value": ParagraphStyle(
            "EquipmentValue",
            parent=base["BodyText"],
            fontName=FONT_BOLD,
            fontSize=9,
            leading=12,
            textColor=NAVY,
        ),
        "center": ParagraphStyle(
            "EquipmentCenter",
            parent=base["BodyText"],
            fontName=FONT_BOLD,
            fontSize=8.5,
            leading=11,
            alignment=TA_CENTER,
            textColor=NAVY,
        ),
    }


def _header_footer(canvas, doc, *, report_id: str, demonstration: bool) -> None:
    _register_fonts()
    canvas.saveState()
    width, height = A4
    canvas.setFillColor(NAVY)
    canvas.rect(0, height - 24 * mm, width, 24 * mm, fill=1, stroke=0)
    logo_size = 12.5 * mm
    logo_x = 18 * mm
    logo_y = height - 18.5 * mm
    canvas.setFillColor(colors.white)
    canvas.roundRect(logo_x, logo_y, logo_size, logo_size, 2 * mm, fill=1, stroke=0)
    canvas.drawImage(
        str(LOGO_PATH),
        logo_x + 0.6 * mm,
        logo_y + 0.6 * mm,
        width=logo_size - 1.2 * mm,
        height=logo_size - 1.2 * mm,
        preserveAspectRatio=True,
        mask="auto",
    )
    canvas.setFont(FONT_BOLD, 15)
    canvas.setFillColor(colors.white)
    canvas.drawString(34 * mm, height - 12.8 * mm, "OPSPECTA")
    canvas.setFont(FONT_REGULAR, 6.7)
    canvas.setFillColor(CYAN)
    canvas.drawString(
        34 * mm, height - 17.2 * mm, "INTELIGÊNCIA OPERACIONAL PARA A SAÚDE"
    )
    canvas.setFont(FONT_BOLD, 7.5)
    canvas.setFillColor(colors.white)
    canvas.drawRightString(width - 18 * mm, height - 14 * mm, report_id)
    if demonstration:
        canvas.setFillColor(colors.HexColor("#FFF3D6"))
        canvas.roundRect(18 * mm, 13 * mm, 74 * mm, 7 * mm, 2 * mm, fill=1, stroke=0)
        canvas.setFont(FONT_BOLD, 6.8)
        canvas.setFillColor(WARNING)
        canvas.drawCentredString(55 * mm, 15.4 * mm, "DEMONSTRAÇÃO - DADOS FICTÍCIOS")
    canvas.setStrokeColor(LINE)
    canvas.line(18 * mm, 11 * mm, width - 18 * mm, 11 * mm)
    canvas.setFont(FONT_REGULAR, 6.8)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 7 * mm, "Documento gerado pela plataforma OPSPECTA")
    canvas.drawRightString(width - 18 * mm, 7 * mm, f"Página {doc.page}")
    canvas.restoreState()


def _field(
    label: str, value: object, styles: dict[str, ParagraphStyle]
) -> list[Paragraph]:
    return [
        Paragraph(label.upper(), styles["label"]),
        Paragraph(_safe_text(value, 180), styles["value"]),
    ]


def _metadata_table(
    equipment: EquipmentRecord, styles: dict[str, ParagraphStyle]
) -> Table:
    data = [
        [
            _field("Código", equipment.code, styles),
            _field("Equipamento", equipment.name, styles),
            _field("Modelo", equipment.model or "Não informado", styles),
        ],
        [
            _field("Local", equipment.location, styles),
            _field("Categoria", equipment.equipment_type, styles),
            _field("Criticidade", normalize_criticality(equipment.criticality), styles),
        ],
    ]
    table = Table(data, colWidths=[55 * mm, 67 * mm, 49 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), SURFACE),
                ("BOX", (0, 0), (-1, -1), 0.7, LINE),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    return table


def _indicator_table(
    equipment: EquipmentRecord,
    tickets: Sequence[TicketRecord],
    styles: dict[str, ParagraphStyle],
) -> Table:
    open_count = sum(ticket.status in {"open", "in_progress"} for ticket in tickets)
    values = [
        ("Status registrado", _status_label(equipment.status)[0]),
        ("Chamados no período", str(len(tickets))),
        ("Chamados em aberto", str(open_count)),
        ("Falhas recorrentes", str(equipment.recurrent_failures)),
        ("Disponibilidade", "Não mensurada"),
        ("MTBF / MTTR", "Não calculados"),
    ]
    cells = []
    for label, value in values:
        cells.append(
            [
                Paragraph(label.upper(), styles["label"]),
                Paragraph(value, styles["center"]),
            ]
        )
    table = Table([cells[:3], cells[3:]], colWidths=[57 * mm] * 3)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.7, LINE),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return table


def _tickets_table(
    tickets: Sequence[TicketRecord], styles: dict[str, ParagraphStyle]
) -> Table:
    header = [
        Paragraph("ID / DATA", styles["label"]),
        Paragraph("CHAMADO", styles["label"]),
        Paragraph("PRIORIDADE", styles["label"]),
        Paragraph("STATUS", styles["label"]),
    ]
    rows: list[list[Paragraph]] = [header]
    if not tickets:
        rows.append(
            [
                Paragraph("-", styles["small"]),
                Paragraph(
                    "Nenhum chamado registrado para este equipamento no período.",
                    styles["body"],
                ),
                Paragraph("-", styles["small"]),
                Paragraph("-", styles["small"]),
            ]
        )
    else:
        for ticket in tickets[:10]:
            rows.append(
                [
                    Paragraph(
                        f"#{ticket.ticket_id}<br/>{_format_datetime(ticket.created_at)[:10]}",
                        styles["small"],
                    ),
                    Paragraph(_safe_text(ticket.title, 180), styles["body"]),
                    Paragraph(_priority_label(ticket.priority), styles["small"]),
                    Paragraph(_ticket_status(ticket.status), styles["small"]),
                ]
            )
    table = Table(rows, colWidths=[25 * mm, 91 * mm, 27 * mm, 28 * mm], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), SURFACE),
                ("BOX", (0, 0), (-1, -1), 0.7, LINE),
                ("INNERGRID", (0, 0), (-1, -1), 0.45, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table


def _analysis_blocks(
    tickets: Sequence[TicketRecord], styles: dict[str, ParagraphStyle]
):
    blocks = []
    analyzed = [
        ticket for ticket in tickets if ticket.root_cause or ticket.recommendation
    ]
    if not analyzed:
        empty = Table(
            [
                [
                    Paragraph(
                        "Não há análise de causa raiz concluída nos chamados deste equipamento para o período selecionado.",
                        styles["body"],
                    )
                ]
            ],
            colWidths=[171 * mm],
        )
        empty.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), SURFACE),
                    ("BOX", (0, 0), (-1, -1), 0.7, LINE),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ]
            )
        )
        return [empty]

    for ticket in analyzed[:6]:
        content = [
            Paragraph(
                f"Chamado #{ticket.ticket_id} - {_safe_text(ticket.title, 140)}",
                styles["value"],
            ),
            Spacer(1, 2 * mm),
            Paragraph(
                f"<b>Hipótese registrada:</b> {_safe_text(ticket.root_cause or 'Não registrada', 420)}",
                styles["body"],
            ),
            Spacer(1, 1.5 * mm),
            Paragraph(
                f"<b>Recomendação registrada:</b> {_safe_text(ticket.recommendation or 'Não registrada', 420)}",
                styles["body"],
            ),
        ]
        box = Table([[content]], colWidths=[171 * mm])
        box.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), SURFACE),
                    ("BOX", (0, 0), (-1, -1), 0.7, LINE),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        blocks.extend([KeepTogether(box), Spacer(1, 3 * mm)])
    return blocks


def generate_equipment_pdf(
    equipment: EquipmentRecord,
    tickets: Sequence[TicketRecord],
    *,
    period_days: int,
    demonstration: bool,
) -> tuple[bytes, str]:
    """Build a two-page PDF and return its bytes and download filename."""
    generated_at = datetime.now(timezone.utc)
    report_id = f"OPS-{_safe_code(equipment.code).upper()}-{generated_at:%Y%m%d%H%M}"
    filename = f"opspecta-relatorio-{_safe_code(equipment.code).lower()}.pdf"
    styles = _styles()
    buffer = io.BytesIO()
    document = BaseDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=31 * mm,
        bottomMargin=24 * mm,
        title=f"OPSPECTA - Relatório operacional {equipment.code}",
        author="OPSPECTA",
        subject="Relatório operacional de equipamento",
        creator="OPSPECTA API",
    )
    frame = Frame(
        document.leftMargin,
        document.bottomMargin,
        document.width,
        document.height,
        id="report",
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
    )
    document.addPageTemplates(
        [
            PageTemplate(
                id="equipment-report",
                frames=[frame],
                onPage=lambda canvas, doc: _header_footer(
                    canvas,
                    doc,
                    report_id=report_id,
                    demonstration=demonstration,
                ),
            )
        ]
    )

    status_text, status_color = _status_label(equipment.status)
    status_style = ParagraphStyle(
        "EquipmentStatus",
        parent=styles["value"],
        fontSize=11,
        alignment=TA_RIGHT,
        textColor=status_color,
    )
    title = Table(
        [
            [
                [
                    Paragraph("RELATÓRIO OPERACIONAL DE EQUIPAMENTO", styles["label"]),
                    Paragraph(_safe_text(equipment.name, 120), styles["title"]),
                ],
                Paragraph(status_text, status_style),
            ]
        ],
        colWidths=[132 * mm, 39 * mm],
    )
    title.setStyle(
        TableStyle(
            [("VALIGN", (0, 0), (-1, -1), "TOP"), ("ALIGN", (1, 0), (1, 0), "RIGHT")]
        )
    )

    disclosure = (
        "Este relatório foi gerado com dados fictícios de demonstração e não representa resultados de clientes."
        if demonstration
        else "Este relatório reflete somente os registros disponíveis na plataforma no momento da emissão."
    )
    story = [
        title,
        Paragraph(disclosure, styles["subtitle"]),
        Spacer(1, 4 * mm),
        _metadata_table(equipment, styles),
        Paragraph("Resumo operacional", styles["section"]),
        Paragraph(
            f"O equipamento está registrado como <b>{status_text.lower()}</b>, com "
            f"<b>{equipment.recurrent_failures}</b> ocorrência(s) recorrente(s) informada(s). "
            f"A consulta considera os últimos <b>{period_days} dias</b> e encontrou "
            f"<b>{len(tickets)}</b> chamado(s) associado(s) ao código {_safe_text(equipment.code, 48)}.",
            styles["body"],
        ),
        Spacer(1, 3 * mm),
        _indicator_table(equipment, tickets, styles),
        Paragraph("Registro técnico disponível", styles["section"]),
        Table(
            [
                [
                    Paragraph(
                        f"<b>Última falha registrada:</b> {_safe_text(equipment.last_failure or 'Não informada', 420)}<br/>"
                        f"<b>Última verificação:</b> {_format_datetime(equipment.last_check)}",
                        styles["body"],
                    )
                ]
            ],
            colWidths=[171 * mm],
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                    ("BOX", (0, 0), (-1, -1), 0.7, LINE),
                    ("LEFTPADDING", (0, 0), (-1, -1), 9),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            ),
        ),
        PageBreak(),
        Paragraph("Chamados do período", styles["title"]),
        Paragraph(
            "A relação abaixo é limitada aos chamados criados pelo usuário autenticado e vinculados ao código do equipamento.",
            styles["subtitle"],
        ),
        Spacer(1, 4 * mm),
        _tickets_table(tickets, styles),
        Paragraph("Análises e recomendações registradas", styles["section"]),
    ]
    story.extend(_analysis_blocks(tickets, styles))
    story.extend(
        [
            Paragraph("Limites de interpretação", styles["section"]),
            Paragraph(
                "A OPSPECTA organiza evidências e registros para apoiar a revisão técnica. O documento não substitui "
                "inspeção, manutenção, calibração, validação clínica ou decisão do profissional responsável. "
                "Disponibilidade, MTBF e MTTR não são estimados sem telemetria e critérios de cálculo documentados.",
                styles["body"],
            ),
            Spacer(1, 4 * mm),
            Table(
                [
                    [
                        _field("Identificador", report_id, styles),
                        _field("Emitido em", _format_datetime(generated_at), styles),
                        _field("Período", f"Últimos {period_days} dias", styles),
                    ]
                ],
                colWidths=[70 * mm, 58 * mm, 43 * mm],
                style=TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), SURFACE),
                        ("BOX", (0, 0), (-1, -1), 0.7, LINE),
                        ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 8),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                        ("TOPPADDING", (0, 0), (-1, -1), 7),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                    ]
                ),
            ),
        ]
    )
    document.build(story)
    return buffer.getvalue(), filename
