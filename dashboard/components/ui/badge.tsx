import * as React from "react"
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "secondary" | "destructive" | "outline" | "success"
}

function Badge({ className, variant = "default", ...props }: BadgeProps) {
  const variants = {
    default: "border-transparent bg-zinc-50 text-zinc-950 hover:bg-zinc-50/80",
    secondary: "border-transparent bg-zinc-800 text-zinc-50 hover:bg-zinc-800/80",
    destructive: "border-transparent bg-red-900 text-red-50 hover:bg-red-900/80",
    outline: "text-zinc-50 border-zinc-800",
    success: "border-transparent bg-green-900 text-green-50 hover:bg-green-900/80"
  }

  return (
    <div
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-zinc-400 focus:ring-offset-2",
        variants[variant],
        className
      )}
      {...props}
    />
  )
}

export { Badge }
