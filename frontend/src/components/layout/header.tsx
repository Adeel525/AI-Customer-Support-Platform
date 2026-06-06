"use client";

import { LogOut, Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/stores/auth-store";

export function Header() {
  const { theme, setTheme } = useTheme();
  const { user, currentWorkspace, logout } = useAuthStore();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  const initials = user?.full_name
    ?.split(" ")
    .map((n) => n[0])
    .join("")
    .slice(0, 2)
    .toUpperCase() || "?";

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-border/50 bg-background/80 px-6 backdrop-blur-xl">
      <div>
        <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Workspace</p>
        <p className="font-semibold text-foreground">{currentWorkspace?.name || "Loading..."}</p>
      </div>
      <div className="flex items-center gap-2">
        <Button
          variant="ghost"
          size="icon"
          className="rounded-lg"
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
        >
          <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
        </Button>
        <div className="flex items-center gap-3 rounded-full border border-border/60 bg-muted/50 py-1 pl-1 pr-4">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-brand text-xs font-bold text-white">
            {initials}
          </div>
          <span className="text-sm font-medium">{user?.full_name}</span>
        </div>
        <Button variant="ghost" size="icon" className="rounded-lg text-muted-foreground hover:text-foreground" onClick={handleLogout}>
          <LogOut className="h-4 w-4" />
        </Button>
      </div>
    </header>
  );
}
