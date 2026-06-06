import { Mail, MessageCircle, Slack } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const integrations = [
  { name: "WhatsApp", icon: MessageCircle, status: "Coming Soon" },
  { name: "Slack", icon: Slack, status: "Coming Soon" },
  { name: "Email", icon: Mail, status: "Coming Soon" },
];

export default function IntegrationsPage() {
  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Integrations</h1>
      <div className="grid gap-4 md:grid-cols-3">
        {integrations.map((int) => (
          <Card key={int.name}>
            <CardHeader className="flex flex-row items-center gap-3">
              <int.icon className="h-8 w-8" />
              <div>
                <CardTitle>{int.name}</CardTitle>
                <Badge variant="secondary">{int.status}</Badge>
              </div>
            </CardHeader>
            <CardContent>
              <Button variant="outline" disabled>Connect</Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
