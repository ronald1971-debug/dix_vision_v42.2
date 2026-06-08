import * as React from "react"

import { cn } from "@/lib/utils"

interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "secondary" | "destructive" | "outline"
}

const Badge = React.forwardRef<HTMLDivElement, BadgeProps>(
  ({ className, variant = "default", ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center rounded-md border px-2 py-0.5 text-xs font-medium w-fit whitespace-nowrap shrink-0 [&>svg]:size-3 gap-1 [&>svg]:shrink-0",
          "transition-colors focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive",
          variant === "default" && "bg-primary border-primary text-primary-foreground [a&]:hover:bg-primary/90",
          variant === "secondary" && "bg-secondary border-secondary text-secondary-foreground [a&]:hover:bg-secondary/90",
          variant === "destructive" && "bg-destructive border-destructive text-white [a&]:hover:bg-destructive/90",
          variant === "outline" && "text-foreground [a&]:hover:bg-accent [a&]:hover:text-accent-foreground",
          className,
        )}
        {...props}
      />
    )
  },
)
Badge.displayName = "Badge"

export { Badge }
