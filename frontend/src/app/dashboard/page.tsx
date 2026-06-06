"use client";

import { useQuery } from "@tanstack/react-query";
import { BarChart3, MessageSquare, Ticket, ThumbsUp } from "lucide-react";
import { MetricCard } from "@/components/dashboard/metric-card";
import { analyticsApi } from "@/lib/api";

export default function DashboardPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["analytics-overview"],
    queryFn: () => analyticsApi.overview().then((r) => r.data),
  });

  if (isLoading) {
    return (
      <div>
        <div className="mb-8 h-8 w-48 animate-pulse rounded-lg bg-muted" />
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-32 animate-pulse rounded-xl border bg-muted/50" />
          ))}
        </div>
      </div>
    );
  }

  const metrics = data || {};

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Overview</h1>
        <p className="mt-1 text-muted-foreground">Your support performance at a glance.</p>
      </div>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <MetricCard title="Total Conversations" value={metrics.total_conversations || 0} icon={MessageSquare} accent="teal" />
        <MetricCard title="Resolved" value={metrics.resolved_conversations || 0} icon={ThumbsUp} accent="cyan" />
        <MetricCard title="Tickets" value={metrics.ticket_volume || 0} icon={Ticket} accent="amber" />
        <MetricCard title="CSAT Score" value={`${metrics.csat_score || 0}%`} icon={BarChart3} accent="rose" />
      </div>
    </div>
  );
}
