"use client";

import Link from "next/link";
import { useState } from "react";
import { toast } from "sonner";
import { AuthShell } from "@/components/layout/auth-shell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { authApi } from "@/lib/api";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await authApi.forgotPassword(email);
    setSent(true);
    toast.success("If the email exists, a reset link has been sent.");
  };

  return (
    <AuthShell title="Reset password" subtitle="We'll send you a link to reset your password">
      {sent ? (
        <div className="rounded-xl border border-primary/20 bg-primary/5 p-6 text-center">
          <p className="font-medium text-foreground">Check your inbox</p>
          <p className="mt-1 text-sm text-muted-foreground">A reset link has been sent if the email exists.</p>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input id="email" type="email" placeholder="you@company.com" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>
          <Button type="submit" variant="gradient" className="w-full">Send Reset Link</Button>
        </form>
      )}
      <div className="mt-6 text-center text-sm">
        <Link href="/login" className="font-medium text-primary hover:underline">Back to login</Link>
      </div>
    </AuthShell>
  );
}
