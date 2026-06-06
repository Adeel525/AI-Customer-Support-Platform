"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Bot, Copy, Plus, Trash2 } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { chatbotApi } from "@/lib/api";

export default function ChatbotsPage() {
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ name: "", welcome_message: "Hi! How can I help you today?", primary_color: "#10b981" });
  const queryClient = useQueryClient();

  const { data } = useQuery({
    queryKey: ["chatbots"],
    queryFn: () => chatbotApi.list().then((r) => r.data),
  });

  const handleCreate = async () => {
    await chatbotApi.create(form);
    toast.success("Chatbot created!");
    setShowCreate(false);
    queryClient.invalidateQueries({ queryKey: ["chatbots"] });
  };

  const handleDelete = async (id: string) => {
    await chatbotApi.delete(id);
    toast.success("Chatbot deleted");
    queryClient.invalidateQueries({ queryKey: ["chatbots"] });
  };

  const copyEmbed = (id: string) => {
    const snippet = `<script src="${window.location.origin}/widget.js" data-chatbot-id="${id}"></script>`;
    navigator.clipboard.writeText(snippet);
    toast.success("Embed code copied!");
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Chatbots</h1>
          <p className="mt-1 text-muted-foreground">Create and customize AI support agents.</p>
        </div>
        <Button onClick={() => setShowCreate(true)}><Plus className="h-4 w-4 mr-2" />Create Chatbot</Button>
      </div>

      {showCreate && (
        <Card className="mb-6">
          <CardHeader><CardTitle>New Chatbot</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div><Label>Name</Label><Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></div>
            <div><Label>Welcome Message</Label><Input value={form.welcome_message} onChange={(e) => setForm({ ...form, welcome_message: e.target.value })} /></div>
            <div><Label>Primary Color</Label><Input type="color" value={form.primary_color} onChange={(e) => setForm({ ...form, primary_color: e.target.value })} /></div>
            <div className="flex gap-2">
              <Button onClick={handleCreate}>Create</Button>
              <Button variant="outline" onClick={() => setShowCreate(false)}>Cancel</Button>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {data?.items?.map((bot: { id: string; name: string; welcome_message: string; is_active: boolean; primary_color: string }) => (
          <Card key={bot.id}>
            <CardHeader className="flex flex-row items-center gap-3">
              <div className="h-10 w-10 rounded-full flex items-center justify-center" style={{ backgroundColor: bot.primary_color }}>
                <Bot className="h-5 w-5 text-white" />
              </div>
              <div>
                <CardTitle className="text-lg">{bot.name}</CardTitle>
                <Badge variant={bot.is_active ? "success" : "secondary"}>{bot.is_active ? "Active" : "Inactive"}</Badge>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">{bot.welcome_message}</p>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={() => copyEmbed(bot.id)}>
                  <Copy className="h-3 w-3 mr-1" />Embed
                </Button>
                <Button variant="ghost" size="sm" onClick={() => handleDelete(bot.id)}>
                  <Trash2 className="h-3 w-3" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
