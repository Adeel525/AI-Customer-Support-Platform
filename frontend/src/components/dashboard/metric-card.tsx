import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface MetricCardProps {
  title: string;
  value: string | number;
  description?: string;
  icon: LucideIcon;
  trend?: string;
  accent?: "teal" | "cyan" | "amber" | "rose";
}

const accentStyles = {
  teal: "bg-primary/10 text-primary",
  cyan: "bg-accent/10 text-accent",
  amber: "bg-amber-500/10 text-amber-600 dark:text-amber-400",
  rose: "bg-rose-500/10 text-rose-600 dark:text-rose-400",
};

export function MetricCard({ title, value, description, icon: Icon, trend, accent = "teal" }: MetricCardProps) {
  return (
    <Card className="overflow-hidden">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
        <div className={cn("flex h-9 w-9 items-center justify-center rounded-lg", accentStyles[accent])}>
          <Icon className="h-4 w-4" />
        </div>
      </CardHeader>
      <CardContent>
        <div className="text-3xl font-bold tracking-tight">{value}</div>
        {description && <p className="mt-1 text-xs text-muted-foreground">{description}</p>}
        {trend && <p className="mt-2 text-xs font-medium text-primary">{trend}</p>}
      </CardContent>
    </Card>
  );
}
