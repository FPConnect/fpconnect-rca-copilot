import Image from "next/image";

type FPConnectLogoProps = {
  variant?: "lockup" | "icon";
  theme?: "dark" | "light";
  size?: "sm" | "md" | "lg";
  subtitle?: string;
  className?: string;
  priority?: boolean;
};

const sizeMap = {
  sm: {
    icon: 34,
    lockupWidth: 128,
    lockupHeight: 38,
    title: "text-sm",
    subtitle: "text-[10px]",
    gap: "gap-2.5",
  },
  md: {
    icon: 44,
    lockupWidth: 168,
    lockupHeight: 50,
    title: "text-base",
    subtitle: "text-[11px]",
    gap: "gap-3",
  },
  lg: {
    icon: 56,
    lockupWidth: 214,
    lockupHeight: 64,
    title: "text-xl",
    subtitle: "text-xs",
    gap: "gap-4",
  },
} as const;

function joinClasses(...classes: Array<string | undefined | false>) {
  return classes.filter(Boolean).join(" ");
}

export default function FPConnectLogo({
  variant = "lockup",
  theme = "dark",
  size = "md",
  subtitle,
  className,
  priority = false,
}: FPConnectLogoProps) {
  const palette =
    theme === "dark"
      ? {
          title: "text-white",
          subtitle: "text-slate-400",
          ring: "ring-white/10",
          bg: "from-slate-950 via-slate-900 to-cyan-950",
        }
      : {
          title: "text-slate-900",
          subtitle: "text-slate-500",
          ring: "ring-slate-200",
          bg: "from-white via-slate-50 to-cyan-50",
        };

  const dimensions = sizeMap[size];

  if (variant === "icon") {
    return (
      <div
        className={joinClasses(
          "relative overflow-hidden rounded-2xl bg-gradient-to-br p-1 shadow-sm ring-1",
          palette.bg,
          palette.ring,
          className,
        )}
        style={{ width: dimensions.icon, height: dimensions.icon }}
      >
        <Image
          src="/branding/fpconnect-report-logo.svg"
          alt="FPConnect"
          width={dimensions.icon * 3}
          height={dimensions.icon}
          priority={priority}
          className="h-full w-full object-cover object-left"
        />
      </div>
    );
  }

  return (
    <div className={joinClasses("flex items-center", dimensions.gap, className)}>
      <div
        className={joinClasses(
          "relative overflow-hidden rounded-2xl bg-gradient-to-br p-1 shadow-sm ring-1",
          palette.bg,
          palette.ring,
        )}
        style={{ width: dimensions.icon, height: dimensions.icon }}
      >
        <Image
          src="/branding/fpconnect-report-logo.svg"
          alt="FPConnect"
          width={dimensions.icon * 3}
          height={dimensions.icon}
          priority={priority}
          className="h-full w-full object-cover object-left"
        />
      </div>
      <div className="min-w-0">
        <div className={joinClasses("font-semibold tracking-tight", dimensions.title, palette.title)}>
          FPConnect
        </div>
        <div className={joinClasses(dimensions.subtitle, palette.subtitle)}>
          {subtitle ?? "RCA Copilot"}
        </div>
      </div>
    </div>
  );
}