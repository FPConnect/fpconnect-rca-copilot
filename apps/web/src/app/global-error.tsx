"use client";

import { useEffect } from "react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <html lang="pt-BR">
      <body className="flex flex-col items-center justify-center min-h-screen text-center px-4 bg-gray-50">
        <h2 className="text-2xl font-semibold text-gray-700 mb-2">Algo deu errado</h2>
        <p className="text-gray-500 mb-8">
          Ocorreu um erro crítico. Tente recarregar a página.
        </p>
        <button
          onClick={reset}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
        >
          Tentar novamente
        </button>
      </body>
    </html>
  );
}
