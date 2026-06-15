import * as React from "react";
import { cn } from "@/lib/utils";

export function Card({ className, ...p }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("rounded-xl border border-border bg-panel", className)} {...p} />;
}
export function CardBody({ className, ...p }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("p-4", className)} {...p} />;
}

export function Button({
  className, variant = "default", ...p
}: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "default" | "ghost" | "accent" }) {
  const v = {
    default: "bg-panel border border-border hover:bg-border",
    ghost: "hover:bg-panel",
    accent: "bg-accent text-white hover:opacity-90",
  }[variant];
  return (
    <button
      className={cn("inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition disabled:opacity-50", v, className)}
      {...p}
    />
  );
}

export function Input({ className, ...p }: React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={cn("w-full rounded-lg border border-border bg-bg px-3 py-2 text-sm outline-none placeholder:text-muted focus:border-accent", className)}
      {...p}
    />
  );
}

const BADGE: Record<string, string> = {
  viral: "bg-viral/15 text-viral border-viral/30",
  evergreen: "bg-evergreen/15 text-evergreen border-evergreen/30",
  sleeper: "bg-sleeper/15 text-sleeper border-sleeper/30",
  none: "bg-border text-muted border-border",
};
export function Badge({ kind = "none", children }: { kind?: string; children: React.ReactNode }) {
  return <span className={cn("rounded-md border px-2 py-0.5 text-xs font-medium", BADGE[kind] || BADGE.none)}>{children}</span>;
}

export function Stat({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <Card>
      <CardBody>
        <div className="text-xs uppercase tracking-wide text-muted">{label}</div>
        <div className="mt-1 font-mono text-2xl">{value}</div>
      </CardBody>
    </Card>
  );
}

export function EmptyState({ title, hint }: { title: string; hint?: string }) {
  return (
    <div className="rounded-xl border border-dashed border-border p-10 text-center">
      <div className="text-sm font-medium">{title}</div>
      {hint && <div className="mt-1 text-sm text-muted">{hint}</div>}
    </div>
  );
}
