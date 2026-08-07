from datetime import datetime
from pathlib import Path

from fpdf import FPDF


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "SECURITY_AUDIT_2026-04-05.md"
TARGET = ROOT / "SECURITY_AUDIT_2026-04-05.pdf"


class AuditPdf(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 8, "FPConnect - Auditoria de Seguranca", ln=True)
        self.set_font("Arial", "", 9)
        self.cell(0, 6, f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", ln=True)
        self.ln(2)

    def footer(self):
        self.set_y(-12)
        self.set_font("Arial", "", 8)
        self.cell(0, 8, f"Pagina {self.page_no()}", align="C")


def render_markdown_line(pdf: AuditPdf, line: str) -> None:
    stripped = line.rstrip()
    if not stripped:
        pdf.ln(2)
        return

    if stripped.startswith("# "):
        pdf.set_font("Arial", "B", 15)
        pdf.multi_cell(0, 8, stripped[2:])
        pdf.ln(1)
        return

    if stripped.startswith("## "):
        pdf.set_font("Arial", "B", 12)
        pdf.multi_cell(0, 7, stripped[3:])
        pdf.ln(1)
        return

    if stripped.startswith("### "):
        pdf.set_font("Arial", "B", 11)
        pdf.multi_cell(0, 6, stripped[4:])
        return

    if stripped.startswith("- "):
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 5, f"- {stripped[2:]}")
        return

    if stripped[:2].isdigit() and stripped[1:3] == ". ":
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 5, stripped)
        return

    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 5, stripped)


def main() -> None:
    content = SOURCE.read_text(encoding="utf-8").splitlines()
    pdf = AuditPdf()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    for line in content:
        render_markdown_line(pdf, line.encode("latin-1", "replace").decode("latin-1"))

    pdf.output(str(TARGET))
    print(f"PDF gerado: {TARGET}")


if __name__ == "__main__":
    main()
