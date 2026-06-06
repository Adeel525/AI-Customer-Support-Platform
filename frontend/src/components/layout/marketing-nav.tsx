import { Sparkles } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";

export function MarketingNav() {
  return (
    <header className="sticky top-0 z-50 glass border-b-0">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <Link href="/" className="flex items-center gap-2.5 font-bold text-lg tracking-tight">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-brand shadow-glow">
            <Sparkles className="h-4 w-4 text-white" />
          </div>
          <span>SupportAI</span>
        </Link>
        <nav className="hidden md:flex items-center gap-8">
          <Link href="/features" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
            Features
          </Link>
          <Link href="/pricing" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
            Pricing
          </Link>
        </nav>
        <div className="flex items-center gap-3">
          <Link href="/login">
            <Button variant="ghost" className="font-medium">Login</Button>
          </Link>
          <Link href="/signup">
            <Button className="bg-gradient-brand hover:opacity-90 shadow-glow border-0 font-medium">
              Get Started
            </Button>
          </Link>
        </div>
      </div>
    </header>
  );
}
