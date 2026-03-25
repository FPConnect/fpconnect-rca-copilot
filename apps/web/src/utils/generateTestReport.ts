import jsPDF from "jspdf";

type ModuleResult = {
  name: string;
  status: string;
  details?: string;
};

export function generateTestReport(modulesResults: ModuleResult[]) {
  const doc = new jsPDF();
  let y = 10;
  doc.setFontSize(18);
  doc.text("Relatório de Testes Automatizados", 10, y);
  y += 10;
  doc.setFontSize(12);
  for (const mod of modulesResults) {
    doc.text(`Módulo: ${mod.name}`, 10, y);
    y += 7;
    doc.text(`Status: ${mod.status}`, 10, y);
    y += 7;
    if (mod.details) {
      doc.text(`Detalhes: ${mod.details}`, 10, y);
      y += 7;
    }
    y += 3;
    if (y > 270) {
      doc.addPage();
      y = 10;
    }
  }
  doc.save("relatorio-testes.pdf");
}
