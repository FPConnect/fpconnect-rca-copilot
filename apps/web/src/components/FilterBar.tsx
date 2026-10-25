"use client";

import { X } from "lucide-react";

export interface FilterOption {
  label: string;
  value: string;
}

export interface FilterConfig {
  key: string;
  label: string;
  options: FilterOption[];
}

interface FilterBarProps {
  filters: FilterConfig[];
  values: Record<string, string>;
  onChange: (key: string, value: string) => void;
  onClear: () => void;
}

export default function FilterBar({
  filters,
  values,
  onChange,
  onClear,
}: FilterBarProps) {
  const activeCount = Object.values(values).filter(Boolean).length;

  return (
    <div className="grid w-full min-w-0 grid-cols-1 gap-3 min-[360px]:grid-cols-2 sm:flex sm:w-auto sm:flex-wrap sm:items-center">
      {filters.map((f) => (
        <div key={f.key} className="flex min-w-0 items-center gap-1.5">
          <label
            htmlFor={`filter-${f.key}`}
            className="text-xs font-medium text-gray-500"
          >
            {f.label}:
          </label>
          <select
            id={`filter-${f.key}`}
            value={values[f.key] ?? ""}
            onChange={(e) => onChange(f.key, e.target.value)}
            className="min-w-0 flex-1 rounded-lg border border-gray-300 bg-white px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 sm:flex-none"
          >
            <option value="">Todos</option>
            {f.options.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      ))}
      {activeCount > 0 && (
        <button
          onClick={onClear}
          className="col-span-full flex items-center justify-center gap-1 rounded-lg border border-gray-200 px-2 py-1.5 text-xs text-gray-500 transition-colors hover:border-red-200 hover:text-red-600 sm:col-auto"
          aria-label="Limpar filtros"
        >
          <X size={12} />
          Limpar filtros
          <span className="ml-1 px-1.5 py-0.5 bg-blue-100 text-blue-700 rounded-full font-semibold">
            {activeCount}
          </span>
        </button>
      )}
    </div>
  );
}
