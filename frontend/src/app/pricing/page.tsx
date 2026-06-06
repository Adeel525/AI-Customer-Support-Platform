import { Check } from "lucide-react";
import Link from "next/link";
import { MarketingNav } from "@/components/layout/marketing-nav";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

const plans = [
  { name: "Free", price: "$0", features: ["10 documents", "1,000 messages/mo", "1 chatbot", "2 team members"], popular: false },
  { name: "Starter", price: "$29", features: ["100 documents", "10,000 messages/mo", "3 chatbots", "5 team members"], popular: false },
  { name: "Professional", price: "$99", features: ["1,000 documents", "100,000 messages/mo", "10 chatbots", "20 team members"], popular: true },
  { name: "Enterprise", price: "Custom", features: ["Unlimited", "Custom integrations", "SSO", "Dedicated support"], popular: false },
];

export default function PricingPage() {
  return (
    <div className="min-h-screen bg-background">
      <MarketingNav />
      <div className="container mx-auto px-4 py-20">
        <div className="mb-16 text-center">
          <h1 className="text-4xl font-bold tracking-tight md:text-5xl">
            Simple, transparent <span className="text-gradient">pricing</span>
          </h1>
          <p className="mt-4 text-lg text-muted-foreground">Start free, scale as your support volume grows.</p>
        </div>
        <div className="mx-auto grid max-w-6xl gap-6 md:grid-cols-2 lg:grid-cols-4">
          {plans.map((plan) => (
            <Card
              key={plan.name}
              className={cn(
                "relative transition-all hover:shadow-glow",
                plan.popular && "border-primary shadow-glow scale-[1.02]"
              )}
            >
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-gradient-brand px-3 py-0.5 text-xs font-semibold text-white">
                  Most Popular
                </div>
              )}
              <CardHeader>
                <CardTitle className="text-lg">{plan.name}</CardTitle>
                <p className="text-4xl font-bold tracking-tight">
                  {plan.price}
                  {plan.price !== "Custom" && <span className="text-sm font-normal text-muted-foreground">/mo</span>}
                </p>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3 text-sm">
                  {plan.features.map((f) => (
                    <li key={f} className="flex items-center gap-2">
                      <Check className="h-4 w-4 shrink-0 text-primary" />
                      {f}
                    </li>
                  ))}
                </ul>
                <Link href="/signup" className="mt-6 block">
                  <Button className="w-full" variant={plan.popular ? "gradient" : "outline"}>
                    Get Started
                  </Button>
                </Link>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
