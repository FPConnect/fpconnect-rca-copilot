"use client";

import Image from "next/image";
import { APP_NAME } from "@/lib/brand";
import { useLanguagePreference } from "@/components/LanguageRuntime";

type BrandLogoProps = {
  inverse?: boolean;
  compact?: boolean;
  className?: string;
};

export default function BrandLogo({ inverse = false, compact = false, className = "" }: BrandLogoProps) {
  const language = useLanguagePreference();
  const tagline = language === "en-US"
    ? "Operational intelligence for healthcare"
    : "Inteligência operacional para a saúde";

  return (
    <span
      className={`inline-flex items-center gap-2.5 ${className}`}
      aria-label={`${APP_NAME} - ${tagline}`}
      data-no-translate
    >
      <Image
        aria-hidden="true"
        src="/brand/opspecta-logo.png"
        alt=""
        width={44}
        height={44}
        className="block h-11 w-11 shrink-0 object-contain"
      />
      {!compact && (
        <span className="min-w-0 pb-px">
          <span
            className={`brand-wordmark block text-[23px] leading-[0.9] ${inverse ? "text-white" : "text-[#071a3d]"}`}
            data-brand-wordmark
          >
            {APP_NAME}
          </span>
          <span
            className={`brand-tagline mt-1.5 block text-[10px] leading-none ${inverse ? "text-slate-300" : "text-slate-600"}`}
          >
            {tagline}
          </span>
        </span>
      )}
    </span>
  );
}
