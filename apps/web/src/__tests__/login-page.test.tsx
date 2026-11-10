import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import LoginPage from "@/app/login/page";
import { ApiError } from "@/services/api";

const mockLogin = jest.fn();
const mockRegister = jest.fn();

jest.mock("@/contexts/AuthContext", () => ({
  useAuth: () => ({ login: mockLogin, register: mockRegister }),
}));

beforeEach(() => {
  mockLogin.mockReset();
  mockRegister.mockReset();
});

it("submits the entered credentials through the existing authentication flow", async () => {
  mockLogin.mockResolvedValue(undefined);
  render(<LoginPage />);
  fireEvent.change(screen.getByLabelText("Email"), { target: { value: "user@example.test" } });
  fireEvent.change(screen.getByLabelText("Senha"), { target: { value: "synthetic-password" } });
  fireEvent.click(screen.getByRole("button", { name: "Entrar" }));
  await waitFor(() => expect(mockLogin).toHaveBeenCalledWith("user@example.test", "synthetic-password"));
});

it("announces rejected credentials without exposing backend details", async () => {
  mockLogin.mockRejectedValue(new ApiError(401, "backend details"));
  render(<LoginPage />);
  fireEvent.change(screen.getByLabelText("Email"), { target: { value: "user@example.test" } });
  fireEvent.change(screen.getByLabelText("Senha"), { target: { value: "synthetic-password" } });
  fireEvent.click(screen.getByRole("button", { name: "Entrar" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("Credenciais inválidas.");
  expect(screen.queryByText("backend details")).not.toBeInTheDocument();
});
