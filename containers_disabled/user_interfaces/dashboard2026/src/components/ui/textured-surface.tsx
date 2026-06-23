import type { ReactNode, CSSProperties } from "react";

interface TexturedSurfaceProps {
  children: ReactNode;
  density?: "light" | "medium" | "heavy";
  blend?: "normal" | "overlay" | "soft-light";
  className?: string;
  style?: CSSProperties;
}

const DENSITY_CLASSES: Record<string, string> = {
  light: "opacity-[0.018]",
  medium: "opacity-[0.032]",
  heavy: "opacity-[0.048]",
};

export function TexturedSurface({
  children,
  density,
  blend,
  className = "",
  style = {},
}: TexturedSurfaceProps) {
  const densityClass = density ? DENSITY_CLASSES[density] ?? DENSITY_CLASSES.medium : DENSITY_CLASSES.medium;
  const blendClass = blend ? `mix-blend-${blend}` : "mix-blend-overlay";

  return (
    <div
      className={`relative overflow-hidden ${className}`}
      style={style}
    >
      <div
        className={`
          pointer-events-none absolute inset-0
          bg-[url('data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 256 256%22%3E%3Cfilter id=%22noise%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.85%22 numOctaves=%224%22 stitchTiles=%22stitch%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23noise)%22 opacity=%220.5%22/%3E%3C/svg%3E')]
          bg-repeat
          bg-[length:220px_220px]
          ${blendClass}
          invert
          ${densityClass}
        `}
        aria-hidden="true"
      />
      <div className="relative z-10">{children}</div>
    </div>
  );
}
