"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ticketApi } from "@/lib/api";

const priorityColors: Record<string, "destructive" | "warning" | "secondary" | "default"> = {
  critical: "destructive",
  high: "warning",
  medium: "secondary",
  low: "default",
};

export default function TicketsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["tickets"],
    queryFn: () => ticketApi.list().then((r) => r.data),
  });

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Support Tickets</h1>
        <p className="mt-1 text-muted-foreground">Manage and resolve customer support requests.</p>
      </div>
      <Card>
        <CardHeader><CardTitle>All Tickets ({data?.total || 0})</CardTitle></CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2">{[...Array(3)].map((_, i) => <div key={i} className="h-16 rounded border animate-pulse" />)}</div>
          ) : data?.items?.length === 0 ? (
            <p className="text-center py-8 text-muted-foreground">No tickets yet.</p>
          ) : (
            <div className="space-y-2">
              {data?.items?.map((ticket: { id: string; title: string; status: string; priority: string; category: string; auto_generated?: boolean }) => (
                <Link key={ticket.id} href={`/dashboard/tickets/${ticket.id}`} className="flex items-center justify-between p-4 rounded-lg border hover:bg-accent transition-colors">
                  <div>
                    <p className="font-medium">{ticket.title}</p>
                    <p className="text-xs text-muted-foreground">{ticket.category} {ticket.auto_generated && "• AI Generated"}</p>
                  </div>
                  <div className="flex gap-2">
                    <Badge variant={priorityColors[ticket.priority] || "secondary"}>{ticket.priority}</Badge>
                    <Badge variant="outline">{ticket.status}</Badge>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
