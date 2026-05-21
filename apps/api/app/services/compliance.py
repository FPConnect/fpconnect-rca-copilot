"""Compliance report generation services."""

from __future__ import annotations

import io
from typing import Any

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def generate_anvisa_pdf(report_data: dict[str, Any]) -> bytes:
    """Generate an ANVISA compliance PDF report."""
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, 800, "RELATÓRIO DE CONFORMIDADE ANVISA")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, 770, f"Período: {report_data['start']} - {report_data['end']}")
    pdf.drawString(
        50,
        750,
        f"Tickets: {report_data['tickets']} | Calibrações: {report_data['calibrations']}",
    )
    pdf.drawString(50, 730, f"Conformidade: {report_data['compliance']}%")
    pdf.showPage()
    pdf.save()
    return buffer.getvalue()
