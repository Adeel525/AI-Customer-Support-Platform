"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";
import { AuthShell } from "@/components/layout/auth-shell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { authApi } from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";

export default function SignupPage() {
  const [form, setForm] = useState({ email: "", password: "", full_name: "", workspace_name: "" });
  const [loading, setLoading] = useState(false);
  const { setAuth } = useAuthStore();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const { data } = await authApi.signup(form);
      setAuth(data.user, [{ ...data.workspace, role: "owner" }], {
        access_token: data.access_token,
        refresh_token: data.refresh_token,
      });
      toast.success("Account created successfully!");
      router.push("/dashboard");
    } catch {
      toast.error("Failed to create account. Email may already be in use.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthShell title="Create your account" subtitle="Start building your AI support chatbot in minutes">
      <form onSubmit={handleSubmit} className="space-y-4">
        {[
          { id: "full_name", label: "Full Name", type: "text", placeholder: "Jane Smith" },
          { id: "workspace_name", label: "Company Name", type: "text", placeholder: "Acme Inc." },
          { id: "email", label: "Email", type: "email", placeholder: "you@company.com" },
          { id: "password", label: "Password", type: "password", placeholder: "Min. 8 characters" },
        ].map((field) => (
          <div key={field.id} className="space-y-2">
            <Label htmlFor={field.id}>{field.label}</Label>
            <Input
              id={field.id}
              type={field.type}
              placeholder={field.placeholder}
              value={form[field.id as keyof typeof form]}
              onChange={(e) => setForm({ ...form, [field.id]: e.target.value })}
              required
            />
          </div>
        ))}
        <Button type="submit" variant="gradient" className="w-full mt-2" disabled={loading}>
          {loading ? "Creating account..." : "Create account"}
        </Button>
      </form>
      <div className="mt-6 text-center text-sm text-muted-foreground">
        Already have an account?{" "}
        <Link href="/login" className="font-medium text-primary hover:underline">
          Sign in
        </Link>
      </div>
    </AuthShell>
  );
}
