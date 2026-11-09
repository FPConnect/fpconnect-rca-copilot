import { fireEvent, render, screen } from "@testing-library/react";
import LandingPage from "@/app/page";
import DemonstracaoPage from "@/app/demonstracao/page";
import { StrategicMoatsContent } from "@/app/strategic-moats/page";
import { DashboardContent } from "@/app/dashboard/page";
import MetricsPage from "@/app/metrics/page";
import { calculateMoatImpact } from "@/lib/strategic-moats";
import { getAppName } from "@/lib/brand";

describe("display name and commercial claims", () => {
  const originalAppName = process.env.NEXT_PUBLIC_APP_NAME;

  afterEach(() => {
    if (originalAppName === undefined) {
      delete process.env.NEXT_PUBLIC_APP_NAME;
    } else {
      process.env.NEXT_PUBLIC_APP_NAME = originalAppName;
    }
  });

  it("keeps OPSPECTA fixed even when deployment configuration is stale", () => {
    delete process.env.NEXT_PUBLIC_APP_NAME;
    expect(getAppName()).toBe("OPSPECTA");

    process.env.NEXT_PUBLIC_APP_NAME = "Wrong deployment label";
    expect(getAppName()).toBe("OPSPECTA");
  });

  it("uses the institutional wordmark treatment for the brand name", () => {
    render(<LandingPage />);

    expect(document.querySelector("main")).toHaveClass("brand-surface");
    const wordmarks = document.querySelectorAll("[data-brand-wordmark]");
    expect(wordmarks.length).toBeGreaterThanOrEqual(2);
    wordmarks.forEach((wordmark) => {
      expect(wordmark).toHaveClass("brand-wordmark");
      expect(wordmark).toHaveTextContent("OPSPECTA");
    });
    expect(screen.getByRole("heading", { level: 1, name: "Transforme ordens de serviço em prioridades de ação" })).toBeInTheDocument();
    expect(document.querySelector("[data-brand-banner]")).toBeInTheDocument();
    expect(document.querySelector("[data-brand-banner] img"))
      .toHaveAttribute("src", expect.stringContaining("opspecta-brand-banner.jpg"));
  });

  it("shows the source-aligned offers in Portuguese and English", () => {
    render(<LandingPage />);

    expect(document.documentElement).toHaveAttribute("lang", "pt-BR");
    expect(screen.queryByText("Amostra inicial de tickets")).not.toBeInTheDocument();
    expect(screen.queryByText("20")).not.toBeInTheDocument();
    expect(screen.getByText("Até 300")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /^Diagnóstico de suporte Escopo inicial$/ })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /^Piloto de indicadores Oferta recomendada$/ })).toBeInTheDocument();
    expect(screen.queryByText("Basic")).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /^Piloto de indicadores Oferta recomendada$/ }));
    expect(screen.getByText(/Até 300 OS/)).toBeInTheDocument();
    expect(screen.queryByText(/R\$/)).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "English" }));
    expect(document.documentElement).toHaveAttribute("lang", "en-US");
    expect(JSON.parse(localStorage.getItem("fpconnect_system_preferences") ?? "{}"))
      .toEqual(expect.objectContaining({ language: "en-US" }));
    expect(screen.getByText("Metrics pilot reference")).toBeInTheDocument();
    expect(screen.getByText("Up to 300")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /^Metrics pilot Recommended offer$/ })).toBeInTheDocument();
    expect(document.querySelector("[data-brand-banner] img"))
      .toHaveAttribute("src", expect.stringContaining("opspecta-brand-banner-en.png"));
    expect(screen.getByAltText("OPSPECTA - Operational intelligence for healthcare"))
      .toBeInTheDocument();
    expect(screen.queryByText(/per month/i)).not.toBeInTheDocument();
  });

  it("explains pilot value in both locales and directs visitors to the diagnostic flow", () => {
    render(<LandingPage />);
    fireEvent.click(screen.getByRole("button", { name: "Português" }));

    expect(screen.getByRole("heading", {
      level: 2,
      name: "O que sua equipe pode aprender com uma amostra de OS",
    })).toBeInTheDocument();
    expect(screen.getByText(/dashboard e uma triagem estruturada/)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Conhecer o diagnóstico de entrada" })).toHaveAttribute("href", "/diagnostic");
    expect(screen.queryByText("Demonstração não é resultado medido.")).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "English" }));

    expect(screen.getByRole("heading", {
      level: 2,
      name: "What your team can learn from a service-order sample",
    })).toBeInTheDocument();
    expect(screen.getByText(/dashboard and structured triage/)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Explore the entry diagnostic" })).toHaveAttribute("href", "/diagnostic");
    expect(screen.queryByText("A demonstration is not a measured result.")).not.toBeInTheDocument();
  });

  it("keeps the illustrative-data and privacy caveats on the detailed demonstration page", () => {
    render(<DemonstracaoPage />);

    expect(screen.getByText(/Não representa dados reais, funcionalidade automatizada em produção nem resultado entregue a clientes/)).toBeInTheDocument();
    expect(screen.getByText(/Não envie registros sensíveis por canais públicos/)).toBeInTheDocument();
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

  it("labels dashboard figures and trends as illustrative", () => {
    render(<DashboardContent />);

    expect(screen.getAllByRole("note")).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ textContent: expect.stringMatching(/Dados demonstrativos/) }),
      ]),
    );
    expect(screen.getAllByText("Variação demonstrativa")).toHaveLength(3);
  });

  it("labels metrics values and trends as illustrative", () => {
    render(<MetricsPage />);

    expect(screen.getByRole("note")).toHaveTextContent(/dados demonstrativos estáticos/);
    expect(screen.getAllByText("Variação demonstrativa")).toHaveLength(4);
  });

  it("keeps the strategic scenario at zero until assumptions are entered", () => {
    render(<StrategicMoatsContent />);

    expect(screen.getByText("Valor hipotético do cenário")).toBeInTheDocument();
    expect(screen.getByText(/Cenário aritmético baseado somente nas premissas informadas/)).toBeInTheDocument();
    expect(screen.getAllByText("0h").length).toBeGreaterThanOrEqual(2);
  });
});
