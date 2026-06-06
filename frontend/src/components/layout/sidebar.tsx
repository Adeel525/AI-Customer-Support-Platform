"use client";

import {
  BarChart3,
  Bot,
  CreditCard,
  Globe,
  LayoutDashboard,
  MessageSquare,
  Plug,
  Settings,
  Sparkles,
  Ticket,
  BookOpen,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/dashboard", label: "Overview", icon: LayoutDashboard },
  { href: "/dashboard/knowledge-base", label: "Knowledge Base", icon: BookOpen },
  { href: "/dashboard/sources", label: "Website Sources", icon: Globe },
  { href: "/dashboard/chatbots", label: "Chatbots", icon: Bot },
  { href: "/dashboard/live-chat", label: "Live Chat", icon: MessageSquare },
  { href: "/dashboard/tickets", label: "Tickets", icon: Ticket },
  { href: "/dashboard/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/dashboard/integrations", label: "Integrations", icon: Plug },
  { href: "/dashboard/billing", label: "Billing", icon: CreditCard },
  { href: "/dashboard/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 z-40 flex h-screen w-[260px] flex-col bg-sidebar text-sidebar-foreground">
      <div className="flex h-16 items-center gap-2.5 border-b border-white/10 px-5">
        <Link href="/dashboard" className="flex items-center gap-2.5 font-bold text-lg tracking-tight">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-brand">
            <Sparkles className="h-4 w-4 text-white" />
          </div>
          SupportAI
        </Link>
      </div>

      <nav className="flex-1 space-y-1 overflow-y-auto p-3">
        {navItems.map((item) => {
          const Icon = item.icon;
          const active =
            pathname === item.href ||
            (item.href !== "/dashboard" && pathname.startsWith(item.href));
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "group flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200",
                active
                  ? "bg-sidebar-accent/15 text-white shadow-sm"
                  : "text-sidebar-muted hover:bg-white/5 hover:text-sidebar-foreground"
              )}
            >
              <Icon
                className={cn(
                  "h-4 w-4 transition-colors",
                  active ? "text-sidebar-accent" : "text-sidebar-muted group-hover:text-sidebar-foreground"
                )}
              />
              {item.label}
              {active && (
                <div className="ml-auto h-1.5 w-1.5 rounded-full bg-sidebar-accent" />
              )}
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-white/10 p-4">
        <div className="rounded-lg bg-white/5 p-3">
          <p className="text-xs font-medium text-sidebar-foreground">Need help?</p>
          <p className="mt-0.5 text-xs text-sidebar-muted">Check our docs or contact support.</p>
        </div>
      </div>
    </aside>
  );
}
