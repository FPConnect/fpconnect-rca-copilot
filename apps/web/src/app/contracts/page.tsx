"use client";

import { useEffect, useState } from "react";
import { api, SLAContract } from "@/services/api";

export default function ContractsPage() {
  const [contracts, setContracts] = useState<SLAContract[]>([]);

  useEffect(() => {
    api.getContracts().then(setContracts).catch(() => setContracts([]));
  }, []);

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-wide text-blue-700">Governança</p>
        <h1 className="mt-1 text-3xl font-bold text-slate-950">Contratos e SLA</h1>
        <p className="mt-2 text-sm text-slate-600">Acompanhe prazos de resposta, penalidades, vencimentos e cumprimento de SLA por equipamento contratado.</p>
      </section>

      <div className="overflow-x-auto rounded-2xl border border-slate-200 bg-white shadow-sm">
        <table className="min-w-[760px] w-full text-left text-sm">
          <thead className="border-b border-slate-200 bg-slate-50 text-slate-600"><tr>{["Equipamento", "Fornecedor", "Resposta", "SLA cumprido", "Vencimento", "Alerta"].map((h) => <th key={h} className="px-4 py-3 font-semibold">{h}</th>)}</tr></thead>
          <tbody className="divide-y divide-slate-100">
            {contracts.map((contract) => (
              <tr key={contract.id}>
                <td className="px-4 py-3 font-semibold text-slate-900">{contract.equipment}</td>
                <td className="px-4 py-3 text-slate-600">{contract.vendor}</td>
                <td className="px-4 py-3 text-slate-600">{contract.response_time_hours}h</td>
                <td className="px-4 py-3 font-semibold text-slate-900">{contract.sla_compliance}%</td>
                <td className="px-4 py-3 text-slate-600">{contract.days_to_expire ?? "—"} dias</td>
                <td className="px-4 py-3">{contract.alert ? <span className="rounded-full bg-amber-100 px-2 py-1 text-xs font-semibold text-amber-800">{contract.alert}</span> : <span className="text-slate-400">Sem alerta</span>}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
