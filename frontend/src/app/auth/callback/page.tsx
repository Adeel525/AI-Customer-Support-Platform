"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect } from "react";
import { authApi } from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";

function CallbackHandler() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const { setAuth } = useAuthStore();

  useEffect(() => {
    const accessToken = searchParams.get("access_token");
    const refreshToken = searchParams.get("refresh_token");
    if (accessToken && refreshToken) {
      localStorage.setItem("access_token", accessToken);
      localStorage.setItem("refresh_token", refreshToken);
      authApi.me().then(({ data }) => {
        setAuth(data.user, data.workspaces, { access_token: accessToken, refresh_token: refreshToken });
        router.push("/dashboard");
      });
    } else {
      router.push("/login");
    }
  }, [searchParams, router, setAuth]);

  return <div className="min-h-screen flex items-center justify-center">Authenticating...</div>;
}

export default function AuthCallbackPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center">Loading...</div>}>
      <CallbackHandler />
    </Suspense>
  );
}
