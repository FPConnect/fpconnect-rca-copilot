"use client";

import { Search, X } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";

interface SearchBarProps {
  placeholder?: string;
  value?: string;
  onChange: (value: string) => void;
  debounceMs?: number;
  className?: string;
}

export default function SearchBar({
  placeholder = "Pesquisar...",
  value = "",
  onChange,
  debounceMs = 300,
  className = "",
}: SearchBarProps) {
  const [localValue, setLocalValue] = useState(value);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    setLocalValue(value);
  }, [value]);

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const val = e.target.value;
      setLocalValue(val);
      if (timerRef.current) clearTimeout(timerRef.current);
      timerRef.current = setTimeout(() => onChange(val), debounceMs);
    },
    [onChange, debounceMs],
  );

  const handleClear = useCallback(() => {
    setLocalValue("");
    if (timerRef.current) clearTimeout(timerRef.current);
    onChange("");
  }, [onChange]);

  useEffect(() => {
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, []);

  return (
    <div className={`relative flex items-center ${className}`}>
      <Search
        size={16}
        className="absolute left-3 text-gray-400 pointer-events-none"
      />
      <input
        type="text"
        value={localValue}
        onChange={handleChange}
        placeholder={placeholder}
        className="w-full pl-9 pr-8 py-2 text-sm border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        aria-label={placeholder}
      />
      {localValue && (
        <button
          onClick={handleClear}
          className="absolute right-2 text-gray-400 hover:text-gray-600"
          aria-label="Limpar pesquisa"
        >
          <X size={14} />
        </button>
      )}
    </div>
  );
}
