"use client";

import { useMemo, useState } from "react";

const ROUTES = [
  "/dashboard",
  "/machines",
  "/health-checks",
  "/alerts",
  "/metrics",
  "/maintenance",
  "/access-control",
  "/history",
];

export default function TestCenterPage() {
  const [activeRoute, setActiveRoute] = useState<string>(ROUTES[0]);
  const iframeSrc = useMemo(() => activeRoute, [activeRoute]);

  return (
    <div className="max-w-7xl mx-auto space-y-4">
      <div className="bg-white rounded-xl shadow p-4 md:p-5">
        <h1 className="text-2xl font-bold text-gray-900">Central de Testes</h1>
        <p className="text-sm text-gray-600 mt-1">
          Use só este link para validar todas as telas do app: <span className="font-semibold">/test-center</span>
        </p>
        <div className="mt-4 flex flex-wrap gap-2">
          {ROUTES.map((route) => (
            <button
              key={route}
              onClick={() => setActiveRoute(route)}
              className={`px-3 py-1.5 text-sm rounded-lg border transition ${
                activeRoute === route
                  ? "bg-blue-600 text-white border-blue-600"
                  : "bg-white text-gray-700 border-gray-300 hover:bg-gray-50"
              }`}
            >
              {route}
            </button>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-xl shadow overflow-hidden border border-gray-200">
        <div className="px-4 py-2 bg-gray-50 border-b text-sm text-gray-700">
          Prévia atual: <span className="font-semibold">{activeRoute}</span>
        </div>
        <iframe title="Prévia da tela" src={iframeSrc} className="w-full h-[75vh]" />
      </div>
    </div>
  );
}
