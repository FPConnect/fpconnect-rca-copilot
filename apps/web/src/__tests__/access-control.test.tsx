import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import AccessControlPage from "@/app/access-control/page";
import { api } from "@/services/api";
import { useAuth } from "@/contexts/AuthContext";

jest.mock("@/contexts/AuthContext", () => ({
  useAuth: jest.fn(),
}));

jest.mock("@/components/AccessGuard", () => ({
  __esModule: true,
  default: ({ children }: { children: React.ReactNode }) => children,
}));

jest.mock("@/services/api", () => ({
  ApiError: class ApiError extends Error {
    constructor(public status: number, message: string) {
      super(message);
    }
  },
  api: {
    getUsers: jest.fn(),
    createManagedUser: jest.fn(),
    updateManagedUser: jest.fn(),
  },
}));

const mockedUseAuth = jest.mocked(useAuth);
const mockedApi = jest.mocked(api);

const master = {
  id: 1,
  email: "admin@fpconnect.com",
  full_name: "Admin OPSPECTA",
  role: "master" as const,
  access_level: 5,
  is_active: true,
};

beforeEach(() => {
  jest.clearAllMocks();
  mockedUseAuth.mockReturnValue({ user: master } as ReturnType<typeof useAuth>);
  mockedApi.getUsers.mockResolvedValue([master]);
});

test("loads real users and creates a subordinate account", async () => {
  mockedApi.createManagedUser.mockResolvedValue({
    id: 2,
    email: "manager@example.com",
    full_name: "Clinical Manager",
    role: "manager",
    access_level: 3,
    is_active: true,
  });
  render(<AccessControlPage />);

  expect(await screen.findByText("admin@fpconnect.com")).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "Novo Usuário" }));
  fireEvent.change(screen.getByLabelText("Nome completo"), { target: { value: "Clinical Manager" } });
  fireEvent.change(screen.getByLabelText("Email"), { target: { value: "manager@example.com" } });
  fireEvent.change(screen.getByLabelText("Perfil"), { target: { value: "manager" } });
  fireEvent.change(screen.getByLabelText(/^Senha temporária/), { target: { value: "ManagerSecure123!" } });
  fireEvent.click(screen.getByRole("button", { name: "Criar usuário" }));

  await waitFor(() => expect(mockedApi.createManagedUser).toHaveBeenCalledWith({
    email: "manager@example.com",
    password: "ManagerSecure123!",
    full_name: "Clinical Manager",
    phone_number: undefined,
    role: "manager",
  }));
  expect(await screen.findByText("manager@example.com")).toBeInTheDocument();
});

test("an admin cannot assign the admin role", async () => {
  const admin = { ...master, role: "admin" as const, access_level: 4 };
  mockedUseAuth.mockReturnValue({ user: admin } as ReturnType<typeof useAuth>);
  mockedApi.getUsers.mockResolvedValue([admin]);
  render(<AccessControlPage />);

  await screen.findByText("admin@fpconnect.com");
  fireEvent.click(screen.getByRole("button", { name: "Novo Usuário" }));
  const dialog = screen.getByRole("dialog", { name: "Criar novo usuário" });

  expect(within(dialog).queryByRole("option", { name: "Administrador" })).not.toBeInTheDocument();
  expect(within(dialog).getByRole("option", { name: "Gerente" })).toBeInTheDocument();
  expect(within(dialog).getByRole("option", { name: "Visitante" })).toBeInTheDocument();
});
