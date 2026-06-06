"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Header } from "@/components/layout/header";
import { Sidebar } from "@/components/layout/sidebar";
import { authApi } from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, setAuth } = useAuthStore();
  const router = useRouter();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/login");
      return;
    }
    if (!user) {
      authApi
        .me()
        .then(({ data }) => {
          setAuth(data.user, data.workspaces, {
            access_token: token,
            refresh_token: localStorage.getItem("refresh_token") || "",
          });
        })
        .catch(() => router.push("/login"))
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [user, router, setAuth]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-4">
          <div className="h-10 w-10 animate-spin rounded-full border-2 border-primary border-t-transparent" />
          <p className="text-sm text-muted-foreground">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Sidebar />
      <div className="pl-[260px]">
        <Header />
        <main className="relative min-h-[calc(100vh-4rem)] bg-grid p-6">
          <div className="relative animate-fade-in">{children}</div>
        </main>
      </div>
    </div>
  );
}
