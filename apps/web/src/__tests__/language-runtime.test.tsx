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
    fireEvent.click(screen.getByRole("button", { name: "Criar novo usuário" }));

    await waitFor(() => {
      expect(screen.getAllByRole("textbox", { name: "Name" })).toHaveLength(2);
    });
  });
});
