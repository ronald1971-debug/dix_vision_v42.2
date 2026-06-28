import * as React from "react"

import { cn } from "@/lib/utils"

const VARIANTS = {
  default: "border-border bg-bg",
  destructive: "border-red-500/40 text-red-100 bg-red-500/10",
} as const

function Alert({ className, variant, ...props }: React.ComponentProps<"div"> & { variant?: keyof typeof VARIANTS }) {
  return (
    <div
      role="alert"
      data-slot="alert"
      className={cn(
        "flex items-start gap-3 rounded-lg border px-4 py-3 text-sm",
        variant ? VARIANTS[variant] : "",
        className,
      )}
      {...props}
    />
  )
}

function AlertDescription({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="alert-description"
      className={cn("text-muted-foreground text-xs", className)}
      {...props}
    />
  )
}

export { Alert, AlertDescription }
