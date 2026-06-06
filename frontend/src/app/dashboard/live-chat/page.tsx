"use client";

import { useQuery } from "@tanstack/react-query";
import { MessageSquare } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { chatApi } from "@/lib/api";

export default function LiveChatPage() {
  const { data } = useQuery({
    queryKey: ["conversations"],
    queryFn: () => chatApi.listConversations().then((r) => r.data),
  });

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Live Chat</h1>
      <Card>
        <CardHeader><CardTitle>Active Conversations</CardTitle></CardHeader>
        <CardContent>
          {data?.items?.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <MessageSquare className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No active conversations.</p>
            </div>
          ) : (
            <div className="space-y-2">
              {data?.items?.map((conv: { id: string; status: string; message_count: number; customer_id: string }) => (
                <div key={conv.id} className="flex items-center justify-between p-4 rounded-lg border">
                  <div>
                    <p className="font-medium">Customer {conv.customer_id?.slice(0, 8)}</p>
                    <p className="text-xs text-muted-foreground">{conv.message_count} messages</p>
                  </div>
                  <Badge variant={conv.status === "escalated" ? "warning" : "secondary"}>{conv.status}</Badge>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
