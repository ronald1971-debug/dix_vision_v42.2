import type { ReactNode, CSSProperties } from "react";

interface NaturalShapeProps {
  children: ReactNode;
  shape?: "blob-soft" | "blob-sharp" | "wave" | "stone";
  className?: string;
  style?: CSSProperties;
}

const SHAPE_STYLES: Record<string, CSSProperties> = {
  "blob-soft": {
    borderRadius: "63% 37% 54% 46% / 55% 48% 52% 45%",
  },
  "blob-sharp": {
    borderRadius: "30% 70% 70% 30% / 30% 52% 48% 70%",
  },
  wave: {
    borderRadius: "46% 54% 44% 56% / 48% 42% 58% 52%",
  },
  stone: {
    borderRadius: "59% 41% 38% 62% / 45% 54% 46% 55%",
  },
};

export function NaturalShape({
  children,
  shape = "blob-soft",
  className = "",
  style = {},
}: NaturalShapeProps) {
  return (
    <div
      className={`
        inline-flex items-center justify-center
        bg-[#171717] text-[#E7E5E4]
        border border-[#27272a]
        shadow-[0_10px_30px_rgba(0,0,0,0.55)]
        transition-all duration-700 ease-out
        hover:shadow-[0_14px_38px_rgba(0,0,0,0.70)]
        hover:brightness-110
        ${className}
      `}
      style={{ ...SHAPE_STYLES[shape], ...style }}
    >
      {children}
    </div>
  );
}
