"use client";

import { X } from "lucide-react";
import { ReactNode } from "react";

interface ModalProps {
  open: boolean;
  title: string;
  onClose: () => void;
  children: ReactNode;
}

export default function Modal({ open, title, onClose, children }: ModalProps) {
  if (!open) return null;

  return (
    <div className="modal-layer fixed inset-0 z-50 flex items-start justify-center px-4 sm:items-center">
      <div
        className="absolute inset-0 bg-black/50"
        onClick={onClose}
        aria-hidden="true"
      />
      <div className="modal-panel relative my-auto w-full max-w-md rounded-xl bg-white shadow-xl">
        <div className="flex items-center justify-between border-b border-gray-200 px-4 py-4 sm:px-6">
          <h2 className="text-lg font-semibold text-gray-800">{title}</h2>
          <button
            onClick={onClose}
            className="p-1 rounded text-gray-400 hover:bg-gray-100 transition-colors"
            aria-label="Fechar"
          >
            <X size={20} />
          </button>
        </div>
        <div className="px-4 py-4 sm:px-6">{children}</div>
      </div>
    </div>
  );
}
