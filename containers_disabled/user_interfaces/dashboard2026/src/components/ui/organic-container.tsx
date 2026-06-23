import type { ReactNode } from "react";

interface OrganicContainerProps {
  children: ReactNode;
  variant?: "rock" | "water" | "wind" | "earth";
  className?: string;
}

const VARIANT_CLASSES: Record<string, string> = {
  rock: "clip-path-polygon-rock hover:scale-[1.01]",
  water: "clip-path-wave hover:scale-[1.01]",
  wind: "clip-path-drift hover:translate-y-[-2px]",
  earth: "clip-path-earth hover:scale-[1.01]",
};

export function OrganicContainer({
  children,
  variant = "rock",
  className = "",
}: OrganicContainerProps) {
  return (
    <div
      className={`
        relative overflow-hidden
        bg-[#111111] text-[#E7E5E4]
        border border-[#27272a]
        shadow-[0_8px_24px_rgba(0,0,0,0.55)]
        transition-transform duration-700 ease-out
        ${VARIANT_CLASSES[variant]}
        ${className}
      `}
    >
      <div className="pointer-events-none absolute inset-0 opacity-[0.03] mix-blend-overlay" aria-hidden="true" />
      <div className="relative z-10">{children}</div>
    </div>
  );
}
