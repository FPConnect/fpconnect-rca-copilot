export const severityLabels: Record<string, string> = {
  critical: "Crítica",
  high: "Alta",
  medium: "Média",
  low: "Baixa",
};

const severityClasses: Record<string, string> = {
  critical: "bg-red-100 text-red-800 border-red-200",
  high: "bg-orange-100 text-orange-800 border-orange-200",
  medium: "bg-yellow-100 text-yellow-800 border-yellow-200",
  low: "bg-green-100 text-green-800 border-green-200",
};

export default function SeverityBadge({ value }: { value: string }) {
  return (
    <span className={`rounded-full border px-2 py-1 text-xs font-semibold ${severityClasses[value] ?? "border-slate-200 bg-slate-100 text-slate-700"}`}>
      {severityLabels[value] ?? value}
    </span>
  );
}
