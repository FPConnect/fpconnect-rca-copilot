"use client";

import { ChevronLeft, ChevronRight } from "lucide-react";
import { useLanguagePreference } from "@/components/LanguageRuntime";

interface PaginationProps {
  page: number;
  totalPages: number;
  onPrev: () => void;
  onNext: () => void;
}

export default function Pagination({
  page,
  totalPages,
  onPrev,
  onNext,
}: PaginationProps) {
  const language = useLanguagePreference();
  const english = language === "en-US";

  return (
    <div className="flex items-center justify-between mt-4">
      <button
        onClick={onPrev}
        disabled={page <= 1}
        className="flex items-center gap-1 px-4 py-2 rounded-lg border border-gray-300 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
      >
        <ChevronLeft size={16} />
        {english ? "Previous" : "Voltar"}
      </button>
      <span className="text-sm text-gray-500">
        {english ? `Page ${page} of ${totalPages}` : `Página ${page} de ${totalPages}`}
      </span>
      <button
        onClick={onNext}
        disabled={page >= totalPages}
        className="flex items-center gap-1 px-4 py-2 rounded-lg border border-gray-300 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
      >
        {english ? "Next" : "Avançar"}
        <ChevronRight size={16} />
      </button>
    </div>
  );
}
