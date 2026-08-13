"use client";

import { useMemo, useState } from "react";
import {
  Activity,
  ArrowRight,
  Banknote,
  BrainCircuit,
  CheckCircle2,
  ClipboardCheck,
  FileText,
  GitBranch,
  Network,
  Radar,
  ShieldAlert,
  SlidersHorizontal,
  Target,
  Users,
} from "lucide-react";
import {
  calculateMoatImpact,
  evidenceSignals,
  experiments,
  strategicMoats,
  stakeholderPerspectives,
  type MoatId,
} from "@/lib/strategic-moats";

const moatIcon = {
  "capacity-twin": Activity,
  "trust-graph": Network,
  "revenue-command": Banknote,
} satisfies Record<MoatId, typeof Activity>;

const currency = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
  maximumFractionDigits: 0,
});

const number = new Intl.NumberFormat("pt-BR");

export default function StrategicMoatsPage() {
  const [selectedId, setSelectedId] = useState<MoatId>("capacity-twin");
  const [downtimeHours, setDowntimeHours] = useState(18);
  const [assetsAtRisk, setAssetsAtRisk] = useState(7);
  const [hourlyClinicalValue, setHourlyClinicalValue] = useState(8500);
  const [clinicalMultiplier, setClinicalMultiplier] = useState(2.2);
  const [avoidableRate, setAvoidableRate] = useState(0.44);

  const selectedMoat = useMemo(
    () => strategicMoats.find((moat) => moat.id === selectedId) ?? strategicMoats[0],
    [selectedId],
  );
  const selectedExperiments = experiments.filter(
    (experiment) => experiment.moatId === selectedId,
  );
  const projection = calculateMoatImpact({
    downtimeHours,
    assetsAtRisk,
    hourlyClinicalValue,
    clinicalMultiplier,
    avoidableRate,
  });

  const SelectedIcon = moatIcon[selectedMoat.id];

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-bold uppercase tracking-[0.14em] text-emerald-700">
              <Target size={14} />
              Diferenciais estratégicos
            </div>
            <h1 className="mt-4 text-3xl font-black tracking-tight text-slate-950">
              FPConnect como sistema operacional de risco, capacidade e receita.
            </h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600">
              Três diferenciais adicionados como módulos independentes: simulação de
              capacidade clínica, grafo de confiança por dispositivo e comando
              executivo de receita.
            </p>
          </div>
          <div className="grid min-w-[260px] grid-cols-3 gap-2 rounded-xl border border-slate-200 bg-slate-50 p-3 text-center">
            <div>
              <div className="text-2xl font-black text-slate-950">3</div>
              <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">
                Módulos
              </div>
            </div>
            <div>
              <div className="text-2xl font-black text-emerald-700">
                {projection.executiveScore}
              </div>
              <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">
                Score
              </div>
            </div>
            <div>
              <div className="text-2xl font-black text-cyan-700">
                {number.format(projection.avoidedHours)}h
              </div>
              <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">
                Evitadas
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-4 lg:grid-cols-3">
        {strategicMoats.map((moat) => {
          const Icon = moatIcon[moat.id];
          const active = moat.id === selectedId;
          return (
            <button
              key={moat.id}
              type="button"
              data-moat-trigger={moat.id}
              onClick={() => setSelectedId(moat.id)}
              className={`rounded-xl border p-5 text-left shadow-sm transition ${
                active
                  ? "border-cyan-300 bg-cyan-50 ring-2 ring-cyan-100"
                  : "border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50"
              }`}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-slate-900 text-cyan-200">
                  <Icon size={20} />
                </div>
                <span
                  className={`rounded-full px-2 py-1 text-xs font-bold ${
                    active
                      ? "bg-cyan-200 text-cyan-950"
                      : "bg-slate-100 text-slate-600"
                  }`}
                >
                  Diferencial {strategicMoats.findIndex((item) => item.id === moat.id) + 1}
                </span>
              </div>
              <h2 className="mt-4 text-lg font-black text-slate-950">{moat.title}</h2>
              <p className="mt-2 text-sm leading-6 text-slate-600">{moat.commercialEdge}</p>
              <div className="mt-4 flex items-center gap-2 text-sm font-bold text-cyan-700">
                Abrir análise <ArrowRight size={15} />
              </div>
            </button>
          );
        })}
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.08fr_0.92fr]">
        <div
          className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
          data-selected-moat={selectedMoat.id}
        >
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <div className="flex items-center gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-slate-950 text-cyan-200">
                  <SelectedIcon size={22} />
                </div>
                <div>
                  <p className="text-xs font-bold uppercase tracking-[0.16em] text-slate-500">
                    Diferencial selecionado
                  </p>
                  <h2 className="text-2xl font-black text-slate-950">
                    {selectedMoat.title}
                  </h2>
                </div>
              </div>
              <p className="mt-4 max-w-3xl text-sm leading-6 text-slate-600">
                {selectedMoat.thesis}
              </p>
            </div>
            <div className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm font-bold text-emerald-800">
              {selectedMoat.proofMetric}
            </div>
          </div>

          <div className="mt-6 grid gap-4 lg:grid-cols-2">
            <div className="rounded-xl border border-slate-200 p-4">
              <div className="mb-3 flex items-center gap-2 text-sm font-black text-slate-950">
                <BrainCircuit size={18} className="text-cyan-700" />
                Loop operacional
              </div>
              <div className="space-y-3">
                {selectedMoat.operatingLoop.map((item, index) => (
                  <div key={item} className="flex gap-3">
                    <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-slate-900 text-xs font-black text-white">
                      {index + 1}
                    </span>
                    <p className="text-sm leading-6 text-slate-600">{item}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-xl border border-slate-200 p-4">
              <div className="mb-3 flex items-center gap-2 text-sm font-black text-slate-950">
                <Radar size={18} className="text-amber-600" />
                Sinais de mercado
              </div>
              <div className="space-y-3">
                {selectedMoat.sourceSignals.map((signal) => (
                  <div key={signal} className="flex gap-3">
                    <CheckCircle2
                      size={18}
                      className="mt-0.5 shrink-0 text-emerald-600"
                    />
                    <p className="text-sm leading-6 text-slate-600">{signal}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="mt-6 rounded-xl border border-slate-200">
            <div className="border-b border-slate-200 px-4 py-3">
              <h3 className="text-sm font-black uppercase tracking-[0.14em] text-slate-500">
                Simulação por stakeholder
              </h3>
            </div>
            <div className="grid divide-y divide-slate-200 lg:grid-cols-3 lg:divide-x lg:divide-y-0">
              {stakeholderPerspectives[selectedMoat.id].map((item) => (
                <div key={item.stakeholder} className="p-4">
                  <div className="flex items-center gap-2 text-sm font-black text-slate-950">
                    <Users size={16} className="text-cyan-700" />
                    {item.stakeholder}
                  </div>
                  <p className="mt-3 text-xs font-bold uppercase tracking-wide text-rose-700">
                    Dor
                  </p>
                  <p className="mt-1 text-sm leading-6 text-slate-600">{item.pain}</p>
                  <p className="mt-3 text-xs font-bold uppercase tracking-wide text-emerald-700">
                    Promessa
                  </p>
                  <p className="mt-1 text-sm leading-6 text-slate-600">{item.promise}</p>
                  <p className="mt-3 text-xs font-bold uppercase tracking-wide text-cyan-700">
                    Prova
                  </p>
                  <p className="mt-1 text-sm leading-6 text-slate-600">{item.proof}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-5 flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-cyan-50 text-cyan-700">
                <SlidersHorizontal size={20} />
              </div>
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.16em] text-slate-500">
                  Impacto simulado
                </p>
                <h2 className="text-xl font-black text-slate-950">
                  Valor protegido
                </h2>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <Metric label="Valor protegido" value={currency.format(projection.protectedValue)} />
              <Metric label="Horas evitadas" value={`${number.format(projection.avoidedHours)}h`} />
              <Metric label="Score executivo" value={`${projection.executiveScore}/99`} />
              <Metric label="Ativos no cenário" value={number.format(assetsAtRisk)} />
            </div>

            <div className="mt-5 rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm font-semibold leading-6 text-amber-900">
              {projection.boardMessage}
            </div>

            <div className="mt-5 space-y-5">
              <Slider
                label="Horas de downtime evitável"
                value={downtimeHours}
                min={2}
                max={72}
                suffix="h"
                onChange={setDowntimeHours}
              />
              <Slider
                label="Ativos críticos no cenário"
                value={assetsAtRisk}
                min={1}
                max={20}
                onChange={setAssetsAtRisk}
              />
              <Slider
                label="Valor clínico-financeiro por hora"
                value={hourlyClinicalValue}
                min={1500}
                max={30000}
                step={500}
                formatter={(value) => currency.format(value)}
                onChange={setHourlyClinicalValue}
              />
              <Slider
                label="Multiplicador de criticidade clínica"
                value={clinicalMultiplier}
                min={1}
                max={4}
                step={0.1}
                suffix="x"
                onChange={setClinicalMultiplier}
              />
              <Slider
                label="Parcela evitável com FPConnect"
                value={avoidableRate}
                min={0.1}
                max={0.75}
                step={0.01}
                formatter={(value) => `${Math.round(value * 100)}%`}
                onChange={setAvoidableRate}
              />
            </div>
          </div>

          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-4 flex items-center gap-2 text-sm font-black text-slate-950">
              <ShieldAlert size={18} className="text-rose-600" />
              Fontes que viram vantagem
            </div>
            <div className="space-y-3">
              {evidenceSignals.map((signal) => (
                <div key={signal.label} className="rounded-lg border border-slate-200 p-3">
                  <div className="flex items-center justify-between gap-3">
                    <p className="text-sm font-black text-slate-950">{signal.label}</p>
                    <span className="rounded-full bg-slate-100 px-2 py-1 text-[11px] font-bold text-slate-600">
                      {signal.posture}
                    </span>
                  </div>
                  <p className="mt-2 text-sm leading-6 text-slate-600">{signal.value}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="rounded-xl border border-slate-200 bg-white shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 px-6 py-4">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.16em] text-slate-500">
              Experimentos de validação
            </p>
            <h2 className="text-xl font-black text-slate-950">
              Próximos testes para {selectedMoat.shortTitle}
            </h2>
          </div>
          <div className="inline-flex items-center gap-2 rounded-full bg-slate-100 px-3 py-2 text-xs font-bold text-slate-700">
            <ClipboardCheck size={14} />
            90 dias
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[820px] text-left text-sm">
            <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th className="px-6 py-3 font-black">Experimento</th>
                <th className="px-6 py-3 font-black">Dono</th>
                <th className="px-6 py-3 font-black">Métrica</th>
                <th className="px-6 py-3 font-black">Sinal de aprovação</th>
                <th className="px-6 py-3 font-black">Ativo inicial</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {selectedExperiments.map((experiment) => (
                <tr key={experiment.name} className="align-top">
                  <td className="px-6 py-4 font-bold text-slate-950">
                    {experiment.name}
                  </td>
                  <td className="px-6 py-4 text-slate-600">{experiment.owner}</td>
                  <td className="px-6 py-4 text-slate-600">{experiment.metric}</td>
                  <td className="px-6 py-4 text-slate-600">{experiment.passSignal}</td>
                  <td className="px-6 py-4 text-slate-600">{experiment.firstAsset}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="grid gap-4 lg:grid-cols-3">
        <ActionCard
          icon={GitBranch}
          title="Produto"
          text={selectedMoat.ninetyDayWedge}
        />
        <ActionCard
          icon={FileText}
          title="Comercial"
          text={selectedMoat.buyerHook}
        />
        <ActionCard
          icon={Target}
          title="Posicionamento"
          text={selectedMoat.commercialEdge}
        />
      </section>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
      <p className="text-[11px] font-bold uppercase tracking-wide text-slate-500">
        {label}
      </p>
      <p className="mt-1 text-lg font-black text-slate-950">{value}</p>
    </div>
  );
}

function Slider({
  label,
  value,
  min,
  max,
  step = 1,
  suffix = "",
  formatter,
  onChange,
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  step?: number;
  suffix?: string;
  formatter?: (value: number) => string;
  onChange: (value: number) => void;
}) {
  const display = formatter ? formatter(value) : `${value}${suffix}`;

  return (
    <label className="block">
      <div className="mb-2 flex items-center justify-between gap-3 text-sm">
        <span className="font-semibold text-slate-700">{label}</span>
        <span className="rounded-md bg-slate-100 px-2 py-1 font-black text-slate-950">
          {display}
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(event) => onChange(Number(event.target.value))}
        className="h-2 w-full cursor-pointer accent-cyan-600"
      />
    </label>
  );
}

function ActionCard({
  icon: Icon,
  title,
  text,
}: {
  icon: typeof GitBranch;
  title: string;
  text: string;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-900 text-cyan-200">
          <Icon size={18} />
        </div>
        <h3 className="text-base font-black text-slate-950">{title}</h3>
      </div>
      <p className="mt-3 text-sm leading-6 text-slate-600">{text}</p>
    </div>
  );
}
