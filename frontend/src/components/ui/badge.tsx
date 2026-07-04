import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

/** Flat, matte badges — distinct hues without glossy / neon fills. */
const badgeVariants = cva(
  "inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium",
  {
    variants: {
      variant: {
        default: "border-slate-200 bg-slate-100 text-slate-700",
        outline: "border-border bg-background text-muted-foreground",
        info: "border-sky-200 bg-sky-50 text-sky-800",
        accent: "border-violet-200 bg-violet-50 text-violet-800",
        success: "border-emerald-200 bg-emerald-50 text-emerald-800",
        warning: "border-amber-200 bg-amber-50 text-amber-900",
        danger: "border-rose-200 bg-rose-50 text-rose-800",
      },
    },
    defaultVariants: { variant: "default" },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export { Badge, badgeVariants };
