import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import EquipmentPage from "@/app/machines/page";
import IncidentsPage from "@/app/tickets/page";
import AnalyzePage from "@/app/analyze/page";
import { api } from "@/services/api";

jest.mock("@/contexts/NotificationContext", () => ({
  useNotifications: () => ({ addNotification: jest.fn() }),
}));

jest.mock("@/services/api", () => ({
  api: {
    getMachines: jest.fn(),
    getTickets: jest.fn(),
    createTicket: jest.fn(),
    analyzeIncident: jest.fn(),
  },
}));

const mockedApi = api as jest.Mocked<typeof api>;

describe("clinical engineering web pages", () => {
  beforeEach(() => {
    jest.resetAllMocks();
    mockedApi.getMachines.mockResolvedValue([
      {
        id: 1,
        code: "ECG-02",
        name: "Monitor Multiparamétrico",
        model: "IntelliVue MX450",
        location: "UTI Adulto",
        status: "warning",
        type: "monitoring",
        criticality: "Alta",
        last_failure: "Perda intermitente de SpO2",
        recurrent_failures: 4,
        last_check: "2026-05-15T08:26:00Z",
      },
    ]);
    mockedApi.getTickets.mockResolvedValue([
      {
        id: 101,
        title: "Perda intermitente de SpO2",
        status: "open",
        priority: "critical",
        device_id: "ECG-02",
        location: "UTI Adulto",
        root_cause: "Sensor com mau contato",
      },
    ]);
    mockedApi.createTicket.mockImplementation(async (payload) => ({
      id: 999,
      status: "open",
      ...payload,
    }));
    mockedApi.analyzeIncident.mockResolvedValue({
      ticket_id: 101,
      root_cause: "Sensor SpO2 com cabo intermitente",
      recommendation: "Trocar cabo e validar curva.",
      explanation: "Comparação com histórico de falhas recorrentes.",
    });
  });

  it("renders the equipment list with recurrent failure indicator", async () => {
    render(<EquipmentPage />);

    expect(await screen.findByText("Equipamentos")).toBeInTheDocument();
    expect(await screen.findByText("Monitor Multiparamétrico")).toBeInTheDocument();
    expect(screen.getByText(/falhas recorrentes: 4/i)).toBeInTheDocument();
  });

  it("creates an incident from the clinical incident form", async () => {
    render(<IncidentsPage />);

    fireEvent.change(screen.getByLabelText("Descrição do chamado"), {
      target: { value: "Falha no monitor da UTI" },
    });
    fireEvent.change(screen.getByLabelText("Equipamento"), { target: { value: "ECG-02" } });
    fireEvent.change(screen.getByLabelText("Unidade clínica"), { target: { value: "UTI Adulto" } });
    fireEvent.click(screen.getByRole("button", { name: "Criar chamado" }));

    await waitFor(() => expect(mockedApi.createTicket).toHaveBeenCalled());
    expect(await screen.findByText("Falha no monitor da UTI")).toBeInTheDocument();
  });

  it("shows root cause and next steps on the diagnosis page", async () => {
    render(<AnalyzePage />);

    fireEvent.click(screen.getByRole("button", { name: "Analisar falha" }));

    expect(await screen.findByText("Sensor SpO2 com cabo intermitente")).toBeInTheDocument();
    expect(screen.getByText("Trocar cabo e validar curva.")).toBeInTheDocument();
  });
});
