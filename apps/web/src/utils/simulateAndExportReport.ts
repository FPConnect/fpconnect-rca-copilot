import { generateTestReport } from "@/utils/generateTestReport";

export function simulateAndExportReport() {
  // Simulação dos resultados dos testes por módulo
  const modulesResults = [
    {
      name: "Backend API",
      status: "100% passed",
      details: "Todos os testes automatizados do backend passaram com sucesso."
    },
    {
      name: "Frontend Web",
      status: "100% passed (dummy test)",
      details: "Ambiente de testes do frontend validado com Vitest."
    },
    {
      name: "Mobile",
      status: "Não testado",
      details: "Testes automatizados ainda não implementados."
    }
  ];
  generateTestReport(modulesResults);
}
