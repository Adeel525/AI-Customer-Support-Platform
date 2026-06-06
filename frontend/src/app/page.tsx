import { ArrowRight, Bot, MessageSquare, Shield, Sparkles, Zap } from "lucide-react";
import Link from "next/link";
import { MarketingNav } from "@/components/layout/marketing-nav";
import { Button } from "@/components/ui/button";

const features = [
  {
    icon: Bot,
    title: "Smart Chatbots",
    desc: "RAG-powered bots trained on your docs with source citations and confidence scoring.",
  },
  {
    icon: MessageSquare,
    title: "Live Chat",
    desc: "Seamless escalation to human agents with full conversation context preserved.",
  },
  {
    icon: Zap,
    title: "Auto Tickets",
    desc: "AI generates support tickets automatically when confidence drops below threshold.",
  },
  {
    icon: Shield,
    title: "Enterprise Ready",
    desc: "Multi-tenant isolation, RBAC, audit logs, and API access built in from day one.",
  },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -top-40 right-0 h-[500px] w-[500px] rounded-full bg-primary/10 blur-3xl" />
        <div className="absolute top-1/2 -left-40 h-[400px] w-[400px] rounded-full bg-accent/10 blur-3xl" />
      </div>

      <MarketingNav />

      <section className="relative container mx-auto px-4 pb-24 pt-20 text-center">
        <div className="mx-auto mb-6 inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-4 py-1.5 text-sm font-medium text-primary animate-slide-up">
          <Sparkles className="h-3.5 w-3.5" />
          AI-powered customer support platform
        </div>

        <h1 className="mx-auto max-w-4xl text-5xl font-bold tracking-tight md:text-6xl lg:text-7xl animate-slide-up">
          Support that learns from{" "}
          <span className="text-gradient">your knowledge</span>
        </h1>

        <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground md:text-xl animate-slide-up">
          Create custom AI chatbots from your documents, website, and FAQs.
          Reduce support tickets by 70% with intelligent, context-aware responses.
        </p>

        <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row animate-slide-up">
          <Link href="/signup">
            <Button size="lg" variant="gradient">
              Start Free Trial
              <ArrowRight className="ml-1 h-4 w-4" />
            </Button>
          </Link>
          <Link href="/features">
            <Button size="lg" variant="outline" className="border-primary/20">
              Explore Features
            </Button>
          </Link>
        </div>

        <div className="mx-auto mt-16 max-w-3xl rounded-2xl border border-border/50 bg-card/50 p-2 shadow-soft backdrop-blur-sm glow-primary">
          <div className="rounded-xl bg-muted/30 p-8 md:p-12">
            <div className="flex items-center justify-center gap-3 text-muted-foreground">
              <div className="h-3 w-3 rounded-full bg-red-400/60" />
              <div className="h-3 w-3 rounded-full bg-amber-400/60" />
              <div className="h-3 w-3 rounded-full bg-emerald-400/60" />
            </div>
            <p className="mt-6 text-left text-sm leading-relaxed text-muted-foreground md:text-base">
              <span className="font-semibold text-primary">Customer:</span> What&apos;s your refund policy?
              <br /><br />
              <span className="font-semibold text-foreground">SupportAI:</span> Based on our policy document, refunds are available within 30 days of purchase for unused subscriptions. Would you like me to help you start a refund request?
              <br /><br />
              <span className="text-xs text-primary/70">Sources: refund-policy.pdf, page 2</span>
            </p>
          </div>
        </div>
      </section>

      <section className="relative border-t border-border/50 bg-muted/30 py-24">
        <div className="container mx-auto px-4">
          <div className="mb-12 text-center">
            <h2 className="text-3xl font-bold tracking-tight md:text-4xl">
              Everything you need to automate support
            </h2>
            <p className="mt-3 text-muted-foreground">Built for teams who want AI that actually knows their business.</p>
          </div>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            {features.map((f) => (
              <div
                key={f.title}
                className="group rounded-xl border border-border/50 bg-card p-6 shadow-soft transition-all duration-300 hover:border-primary/30 hover:shadow-glow"
              >
                <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-xl bg-primary/10 text-primary transition-colors group-hover:bg-gradient-brand group-hover:text-white">
                  <f.icon className="h-5 w-5" />
                </div>
                <h3 className="mb-2 font-semibold text-lg">{f.title}</h3>
                <p className="text-sm leading-relaxed text-muted-foreground">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
