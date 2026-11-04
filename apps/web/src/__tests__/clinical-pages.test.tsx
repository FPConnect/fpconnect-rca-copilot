import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import EquipmentPage from "@/app/machines/page";
import IncidentsPage from "@/app/tickets/page";
import AnalyzePage from "@/app/analyze/page";
import { api } from "@/services/api";

jest.mock("@/contexts/NotificationContext", () => ({
  useNotifications: () => ({ addNotification: jest.fn() }),
}));

jest.mock("@/contexts/AuthContext", () => ({
  useAuth: () => ({ user: { id: 1, role: "user", access_level: 2, is_active: true } }),
}));

jest.mock("@/services/api", () => ({
  api: {
    getMachines: jest.fn(),
    getTickets: jest.fn(),
    createTicket: jest.fn(),
    analyzeIncident: jest.fn(),
    confirmIncidentAnalysis: jest.fn(),
    getMe: jest.fn(),
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
        location: "UTI Adulto",
        status: "warning",
        type: "monitoring",
        last_check: "2026-05-15T08:26:00Z",
      },
    ]);
    mockedApi.getTickets.mockResolvedValue([
      {
        id: 101,
        title: "Perda intermitente de SpO2",
        status: "open",
        priority: "critical",
      },
    ]);
    mockedApi.createTicket.mockImplementation(async (payload) => ({
      id: 999,
      status: "open",
      ...payload,
    }));
    mockedApi.getMe.mockResolvedValue({
      id: 1,
      email: "reviewer@example.org",
      role: "user",
      access_level: 2,
    });
    mockedApi.confirmIncidentAnalysis.mockResolvedValue({
      ticket_id: 101,
      status: "human_confirmed",
      reviewer_id: 1,
      review_required: false,
    });
    mockedApi.analyzeIncident.mockResolvedValue({
      ticket_id: 101,
      root_cause: "Sensor SpO2 com cabo intermitente",
      recommendation: "Encaminhar à equipe técnica para revisão.",
      explanation: "Comparação com histórico de falhas recorrentes.",
    });
  });

  it("renders the equipment list with its current status", async () => {
    render(<EquipmentPage />);

    expect(await screen.findByText("Máquinas")).toBeInTheDocument();
    expect(await screen.findByText("Monitor Multiparamétrico")).toBeInTheDocument();
    expect(screen.getByText("Atenção")).toBeInTheDocument();
  });

  it("creates a ticket from the current ticket form", async () => {
    render(<IncidentsPage />);

    fireEvent.change(screen.getByPlaceholderText("Ticket title"), {
      target: { value: "Falha no monitor da UTI" },
    });
    fireEvent.change(screen.getAllByRole("combobox")[0], { target: { value: "critical" } });
    fireEvent.click(screen.getByRole("button", { name: "Create" }));

    await waitFor(() => expect(mockedApi.createTicket).toHaveBeenCalled());
    expect(await screen.findByText("Falha no monitor da UTI")).toBeInTheDocument();
  });

  it("labels technical suggestions as unconfirmed and requiring review", async () => {
    render(<AnalyzePage />);

    fireEvent.click(screen.getByRole("button", { name: "Gerar hipótese (não confirmada)" }));

    expect(await screen.findByText("Sensor SpO2 com cabo intermitente")).toBeInTheDocument();
    expect(screen.getByText("Encaminhar à equipe técnica para revisão.")).toBeInTheDocument();
    expect(screen.getByText("Hipótese não confirmada")).toBeInTheDocument();
  });
});
