import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const plans = [
  { name: "Free", price: "$0", docs: "10", messages: "1,000" },
  { name: "Starter", price: "$29", docs: "100", messages: "10,000" },
  { name: "Professional", price: "$99", docs: "1,000", messages: "100,000" },
  { name: "Enterprise", price: "Custom", docs: "Unlimited", messages: "Unlimited" },
];

export default function BillingPage() {
  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Billing</h1>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {plans.map((plan) => (
          <Card key={plan.name} className={plan.name === "Free" ? "border-primary" : ""}>
            <CardHeader>
              <CardTitle>{plan.name}</CardTitle>
              <p className="text-3xl font-bold">{plan.price}<span className="text-sm font-normal text-muted-foreground">/mo</span></p>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">{plan.docs} documents</p>
              <p className="text-sm text-muted-foreground">{plan.messages} messages/mo</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
