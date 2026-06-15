"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard, Users, FileVideo, Flame, Bookmark, Hammer, KanbanSquare, Settings,
} from "lucide-react";
import { cn } from "@/lib/utils";

const NAV = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/competitors", label: "Competitors", icon: Users },
  { href: "/posts", label: "Posts", icon: FileVideo },
  { href: "/outliers", label: "Outliers", icon: Flame },
  { href: "/vault", label: "Vault", icon: Bookmark },
  { href: "/forge", label: "Forge", icon: Hammer },
  { href: "/flow", label: "Flow", icon: KanbanSquare },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const path = usePathname();
  return (
    <aside className="sticky top-0 flex h-screen w-56 flex-col border-r border-border bg-panel/40 px-3 py-4">
      <div className="px-2 pb-6">
        <span className="text-lg font-bold tracking-tight">VYSE</span>
        <p className="text-[11px] text-muted">Find what works. Know why.</p>
      </div>
      <nav className="flex flex-col gap-1">
        {NAV.map(({ href, label, icon: Icon }) => {
          const active = path.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition",
                active ? "bg-accent/15 text-fg" : "text-muted hover:bg-panel hover:text-fg"
              )}
            >
              <Icon size={16} /> {label}
            </Link>
          );
        })}
      </nav>
      <div className="mt-auto px-3 text-[11px] text-muted">Dev workspace · agency plan</div>
    </aside>
  );
}
