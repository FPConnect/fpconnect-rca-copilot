import { APP_NAME } from "@/lib/brand";

type BrandLogoProps = {
  inverse?: boolean;
  compact?: boolean;
  className?: string;
};

export default function BrandLogo({ inverse = false, compact = false, className = "" }: BrandLogoProps) {
  return (
    <span
      className={`inline-flex items-center gap-3 ${className}`}
      aria-label={`${APP_NAME} - Inteligência operacional para a saúde`}
      data-no-translate
    >
      <span
        aria-hidden="true"
        className="relative block h-10 w-10 shrink-0 rounded-full"
        style={{
          background:
            "conic-gradient(#082149 0deg 76deg, transparent 76deg 104deg, #17c9c2 104deg 183deg, transparent 183deg 211deg, #082149 211deg 290deg, transparent 290deg 318deg, #17c9c2 318deg 360deg)",
        }}
      >
        <span
          className={`absolute inset-[9px] rounded-full ${inverse ? "bg-[#071a33]" : "bg-white"}`}
        />
        <span className="absolute right-0 top-0 h-2.5 w-2.5 bg-[#22d7cf] ring-2 ring-white" />
      </span>
      {!compact && (
        <span className="min-w-0">
          <span className={`block text-xl font-black leading-none ${inverse ? "text-white" : "text-[#071a3d]"}`}>
            {APP_NAME}
          </span>
          <span className={`mt-1 block text-[10px] leading-none ${inverse ? "text-slate-300" : "text-slate-500"}`}>
            Inteligência operacional para a saúde
          </span>
        </span>
      )}
    </span>
  );
}
