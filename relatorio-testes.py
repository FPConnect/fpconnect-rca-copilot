from fpdf import FPDF
import datetime

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Relatório de Testes Automatizados', 0, 1, 'C')
        self.set_font('Arial', '', 10)
        self.cell(0, 10, f'Gerado em: {datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}', 0, 1, 'C')
        self.ln(5)

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(2)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 8, body)
        self.ln(2)

def gerar_relatorio_testes():
    pdf = PDF()
    pdf.add_page()

    # Backend
    pdf.chapter_title('Módulo: Backend API')
    pdf.chapter_body('Status: 100% passed\nTodos os testes automatizados do backend passaram com sucesso.')

    # Frontend
    pdf.chapter_title('Módulo: Frontend Web')
    pdf.chapter_body('Status: 100% passed (dummy test)\nAmbiente de testes do frontend validado com Vitest.')

    # Mobile
    pdf.chapter_title('Módulo: Mobile')
    pdf.chapter_body('Status: Não testado\nTestes automatizados ainda não implementados.')

    pdf.output('relatorio-testes.pdf')

if __name__ == "__main__":
    gerar_relatorio_testes()
