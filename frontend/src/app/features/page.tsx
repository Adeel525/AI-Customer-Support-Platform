import { BarChart3, Bot, Globe, MessageSquare, Search, Ticket, Zap } from "lucide-react";
import Link from "next/link";
import { MarketingNav } from "@/components/layout/marketing-nav";
import { Button } from "@/components/ui/button";

const features = [
  { icon: Bot, title: "Multi-tenant workspaces", desc: "Isolated environments for every company with RBAC and audit logs." },
  { icon: Search, title: "RAG knowledge base", desc: "Upload docs, crawl websites, and power answers with source citations." },
  { icon: MessageSquare, title: "Embeddable widget", desc: "Drop a chat widget on any site with one line of code." },
  { icon: Ticket, title: "Auto ticket generation", desc: "AI creates tickets when confidence drops or customers escalate." },
  { icon: Zap, title: "Live chat", desc: "WebSocket-powered agent handoff with full conversation history." },
  { icon: BarChart3, title: "Analytics dashboard", desc: "CSAT, top questions, confidence trends, and ticket volume." },
  { icon: Globe, title: "Website crawler", desc: "Automatically sync docs, blogs, and help center content." },
  { icon: Bot, title: "API platform", desc: "Public APIs with key management and rate limiting." },
];

export default function FeaturesPage() {
  return (
    <div className="min-h-screen bg-background">
      <MarketingNav />
      <div className="container mx-auto px-4 py-20">
        <div className="mb-16 text-center">
          <h1 className="text-4xl font-bold tracking-tight md:text-5xl">
            Built for modern <span className="text-gradient">support teams</span>
          </h1>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-muted-foreground">
            Everything you need to deploy AI support that actually understands your business.
          </p>
        </div>
        <div className="mx-auto grid max-w-5xl gap-6 md:grid-cols-2">
          {features.map((f) => (
            <div
              key={f.title}
              className="flex gap-4 rounded-xl border border-border/50 bg-card p-6 shadow-soft transition-all hover:border-primary/30 hover:shadow-glow"
            >
              <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
                <f.icon className="h-5 w-5" />
              </div>
              <div>
                <h3 className="font-semibold">{f.title}</h3>
                <p className="mt-1 text-sm text-muted-foreground">{f.desc}</p>
              </div>
            </div>
          ))}
        </div>
        <div className="mt-16 text-center">
          <Link href="/signup">
            <Button size="lg" variant="gradient">Get Started Free</Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
