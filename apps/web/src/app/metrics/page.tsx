const METRICS = [
  { label: "Uptime Médio", value: "99.2%", change: "+0.1%", positive: true },
  { label: "MTBF (horas)", value: "1,240", change: "+5%", positive: true },
  { label: "MTTR (minutos)", value: "18", change: "-12%", positive: true },
  { label: "Alertas (7d)", value: "34", change: "+8%", positive: false },
];

const PERFORMANCE = [
  { machine: "Ressonância magnética", uptime: 99.8, incidents: 0 },
  { machine: "Monitor de ECG", uptime: 94.5, incidents: 3 },
  { machine: "Ventilador", uptime: 99.9, incidents: 0 },
  { machine: "Desfibrilador", uptime: 78.2, incidents: 5 },
  { machine: "Monitor multiparamétrico", uptime: 98.7, incidents: 1 },
];

export default function MetricsPage() {
  return (
    <div className="max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Métricas de Performance</h1>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {METRICS.map((m) => (
          <div key={m.label} className="bg-white rounded-xl shadow p-5">
            <p className="text-sm text-gray-500">{m.label}</p>
            <p className="text-3xl font-bold text-gray-900 mt-1">{m.value}</p>
            <p className={`text-sm font-medium mt-1 ${m.positive ? "text-green-600" : "text-red-600"}`}>
              {m.change} vs semana anterior
            </p>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-xl shadow p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Uptime por Equipamento</h2>
        <div className="space-y-4">
          {PERFORMANCE.map((p) => (
            <div key={p.machine}>
              <div className="flex justify-between text-sm mb-1">
                <span className="font-medium text-gray-700">{p.machine}</span>
                <span className="text-gray-500">
                  {p.uptime}% &middot; {p.incidents} incidente(s)
                </span>
              </div>
              <div className="w-full bg-gray-100 rounded-full h-2.5">
                <div
                  className={`h-2.5 rounded-full ${p.uptime >= 99 ? "bg-green-500" : p.uptime >= 90 ? "bg-yellow-500" : "bg-red-500"}`}
                  style={{ width: `${p.uptime}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
