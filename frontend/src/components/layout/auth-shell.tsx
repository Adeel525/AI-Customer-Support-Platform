import { Sparkles } from "lucide-react";
import Link from "next/link";

interface AuthShellProps {
  children: React.ReactNode;
  title: string;
  subtitle: string;
}

export function AuthShell({ children, title, subtitle }: AuthShellProps) {
  return (
    <div className="flex min-h-screen">
      <div className="relative hidden w-1/2 flex-col justify-between overflow-hidden bg-sidebar p-12 lg:flex">
        <div className="absolute inset-0 bg-gradient-brand opacity-90" />
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PHBhdGggZD0iTTM2IDM0djItaDJ2LTJoLTJ6bTAtNHYyaDJ2LTJoLTJ6bTAtNHYyaDJ2LTJoLTJ6bTAtNHYyaDJ2LTJoLTJ6bTAtNHYyaDJ2LTJoLTJ6bTAtNHYyaDJ2LTJoLTJ6bTAtNHYyaDJ2LTJoLTJ6Ii8+PC9nPjwvZz48L3N2Zz4=')] opacity-30" />
        <div className="relative">
          <Link href="/" className="flex items-center gap-2.5 font-bold text-xl text-white">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-white/20 backdrop-blur-sm">
              <Sparkles className="h-4 w-4" />
            </div>
            SupportAI
          </Link>
        </div>
        <div className="relative space-y-4">
          <h2 className="text-3xl font-bold leading-tight text-white">
            AI support that knows your business inside out
          </h2>
          <p className="max-w-md text-white/70">
            Train chatbots on your docs, website, and FAQs. Escalate to humans when it matters.
          </p>
        </div>
        <p className="relative text-sm text-white/50">Trusted by support teams worldwide</p>
      </div>

      <div className="flex flex-1 flex-col items-center justify-center bg-background p-6">
        <div className="mb-8 flex items-center gap-2 lg:hidden">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-brand">
            <Sparkles className="h-4 w-4 text-white" />
          </div>
          <span className="font-bold text-lg">SupportAI</span>
        </div>
        <div className="w-full max-w-md animate-slide-up">
          <div className="mb-8 text-center lg:text-left">
            <h1 className="text-2xl font-bold tracking-tight">{title}</h1>
            <p className="mt-2 text-muted-foreground">{subtitle}</p>
          </div>
          {children}
        </div>
      </div>
    </div>
  );
}
