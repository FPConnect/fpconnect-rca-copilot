import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { useState } from "react";
import LanguageRuntime from "@/components/LanguageRuntime";

function LoginModeToggle() {
  const [isRegister, setIsRegister] = useState(false);

  return (
    <>
      <LanguageRuntime />
      <h1>{isRegister ? "Criar conta" : "Entrar"}</h1>
      {isRegister && <input aria-label="Nome" />}
      <input aria-label={isRegister ? "Nome" : "Senha"} />
      <button onClick={() => setIsRegister(!isRegister)}>
        {isRegister ? "Já tenho conta" : "Criar novo usuário"}
      </button>
    </>
  );
}

function DashboardDisclosure() {
  return (
    <>
      <LanguageRuntime />
      <p role="note">
        Demonstração — dados fictícios. Estes indicadores não representam resultados de clientes nem uma operação em produção.
      </p>
    </>
  );
}

function CustomerEnglishSurface() {
  return (
    <>
      <LanguageRuntime />
      <p>Configure os dados e preferências necessários para acompanhar os equipamentos da sua operação.</p>
      <button aria-label="Remover notificação">Remover notificação</button>
      <p>{"  Página 1 de 2  "}</p>
    </>
  );
}

describe("LanguageRuntime", () => {
  beforeEach(() => {
    localStorage.setItem(
      "fpconnect_system_preferences",
      JSON.stringify({ language: "pt-BR" }),
    );
  });

  it("preserves React-updated text when switching between login and registration", async () => {
    render(<LoginModeToggle />);

    fireEvent.click(screen.getByRole("button", { name: "Criar novo usuário" }));

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Criar conta" })).toBeInTheDocument();
      expect(screen.getByRole("button", { name: "Já tenho conta" })).toBeInTheDocument();
      expect(screen.getAllByRole("textbox", { name: "Nome" })).toHaveLength(2);
    });

    fireEvent.click(screen.getByRole("button", { name: "Já tenho conta" }));

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Entrar" })).toBeInTheDocument();
      expect(screen.getByRole("button", { name: "Criar novo usuário" })).toBeInTheDocument();
      expect(screen.getByRole("textbox", { name: "Senha" })).toBeInTheDocument();
    });
  });

  it("retranslates React-updated accessibility attributes from their new source text", async () => {
    localStorage.setItem(
      "fpconnect_system_preferences",
      JSON.stringify({ language: "en-US" }),
    );
    render(<LoginModeToggle />);

    expect(screen.getByRole("textbox", { name: "Password" })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Create new user" }));

    await waitFor(() => {
      expect(screen.getAllByRole("textbox", { name: "Name" })).toHaveLength(2);
    });
  });

  it("translates the dashboard disclosure when English is selected", async () => {
    localStorage.setItem(
      "fpconnect_system_preferences",
      JSON.stringify({ language: "en-US" }),
    );

    render(<DashboardDisclosure />);

    await waitFor(() => {
      expect(screen.getByRole("note")).toHaveTextContent(
        "Demo — fictional data. These indicators do not represent customer results or a production operation.",
      );
    });
  });

  it("translates customer controls and dynamic pagination with surrounding whitespace", async () => {
    localStorage.setItem(
      "fpconnect_system_preferences",
      JSON.stringify({ language: "en-US" }),
    );

    render(<CustomerEnglishSurface />);

    await waitFor(() => {
      expect(screen.getByText(
        "Configure the data and preferences required to monitor your operation's equipment.",
      )).toBeInTheDocument();
      expect(screen.getByRole("button", { name: "Remove notification" })).toBeInTheDocument();
      expect(screen.getByText("Page 1 of 2")).toBeInTheDocument();
    });
  });
});
