export default function DashboardPage() {
  const metrics = [
    { label: "Open Tickets", value: 12, color: "bg-yellow-100 text-yellow-800" },
    { label: "In Progress", value: 5, color: "bg-blue-100 text-blue-800" },
    { label: "Resolved Today", value: 8, color: "bg-green-100 text-green-800" },
    { label: "Critical", value: 2, color: "bg-red-100 text-red-800" },
  ];

  return (
    <div className="max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {metrics.map((m) => (
          <div key={m.label} className={`rounded-xl p-6 ${m.color} shadow`}>
            <div className="text-4xl font-bold">{m.value}</div>
            <div className="text-sm font-medium mt-1">{m.label}</div>
          </div>
        ))}
      </div>
      <div className="bg-white rounded-xl shadow p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">
          Recent Activity
        </h2>
        <p className="text-gray-500">No recent activity to display.</p>
      </div>
    </div>
  );
}
