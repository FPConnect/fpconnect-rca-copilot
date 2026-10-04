import { fireEvent, render, screen } from "@testing-library/react";
import LandingPage from "@/app/page";
import StrategicMoatsPage from "@/app/strategic-moats/page";
import DashboardPage from "@/app/dashboard/page";
import MetricsPage from "@/app/metrics/page";
import { calculateMoatImpact } from "@/lib/strategic-moats";
import { getAppName, getBrandTransitionNotice } from "@/lib/brand";

describe("display name and commercial claims", () => {
  const originalAppName = process.env.NEXT_PUBLIC_APP_NAME;

  afterEach(() => {
    if (originalAppName === undefined) {
      delete process.env.NEXT_PUBLIC_APP_NAME;
    } else {
      process.env.NEXT_PUBLIC_APP_NAME = originalAppName;
    }
  });

  it("uses OPSPECTA as the default and keeps the legacy name in the transition notice", () => {
    delete process.env.NEXT_PUBLIC_APP_NAME;
    expect(getAppName()).toBe("OPSPECTA");
    expect(getBrandTransitionNotice()).toMatch(/FPConnect/);

    process.env.NEXT_PUBLIC_APP_NAME = "  OPSPECTA  ";
    expect(getAppName()).toBe("OPSPECTA");
  });

  it("shows the source-aligned offers in Portuguese and English", () => {
    render(<LandingPage />);

    expect(screen.queryByText("Amostra inicial de tickets")).not.toBeInTheDocument();
    expect(screen.queryByText("20")).not.toBeInTheDocument();
    expect(screen.getByText("Até 300")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /^Diagnóstico de suporte Escopo inicial$/ })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /^Piloto de indicadores Oferta recomendada$/ })).toBeInTheDocument();
    expect(screen.queryByText("Basic")).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /^Piloto de indicadores Oferta recomendada$/ }));
    expect(screen.getByText("R$ 4.900")).toBeInTheDocument();
    expect(screen.getByText(/Até 300 OS/)).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "English" }));
    expect(screen.getByText("Metrics pilot reference")).toBeInTheDocument();
    expect(screen.getByText("Up to 300")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /^Metrics pilot Recommended offer$/ })).toBeInTheDocument();
  });

  it("calculates an illustrative scenario from explicit premises", () => {
    const projection = calculateMoatImpact({
      downtimeHours: 4,
      assetsAtRisk: 3,
      hourlyClinicalValue: 1000,
      clinicalMultiplier: 2,
      avoidableRate: 0.25,
    });

    expect(projection.scenarioHours).toBe(3);
    expect(projection.scenarioValue).toBe(6000);
    expect(projection.boardMessage).toMatch(/Não mede efeito do produto/);
    expect(projection.boardMessage).toMatch(/retorno garantido/);
  });

  it("keeps the strategic scenario at zero until assumptions are entered", () => {
    render(<StrategicMoatsPage />);

    expect(screen.getByText("Valor hipotético do cenário")).toBeInTheDocument();
    expect(screen.getByText(/Cenário aritmético baseado somente nas premissas informadas/)).toBeInTheDocument();
    expect(screen.getAllByText("0h").length).toBeGreaterThanOrEqual(2);
  });

  it("labels dashboard figures as demonstration data", () => {
    render(<DashboardPage />);

    expect(screen.getByText(/Dados de demonstração:/)).toBeInTheDocument();
    expect(screen.getByText("Variação demonstrativa: -12%")).toBeInTheDocument();
  });

  it("labels metrics figures as demonstration data", () => {
    render(<MetricsPage />);

    expect(screen.getByText(/Dados de demonstração:/)).toBeInTheDocument();
    expect(screen.getByText("Disponibilidade demonstrativa por equipamento")).toBeInTheDocument();
  });
});
