import IntelPanel from "@/components/IntelPanel";

export default function IntelPage() {
  return (
    <div className="max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">Radar</h1>
      <p className="text-sm text-gray-500 mb-6">
        Intelligence feed (fontes públicas) para acompanhar tendências em
        HealthTech/MedTech, cibersegurança, interoperabilidade e confiabilidade.
      </p>
      <IntelPanel />
    </div>
  );
}
