"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { workspaceApi } from "@/lib/api";

export default function SettingsPage() {
  const queryClient = useQueryClient();
  const { data: workspace } = useQuery({
    queryKey: ["workspace"],
    queryFn: () => workspaceApi.getCurrent().then((r) => r.data),
  });

  const [form, setForm] = useState({ name: "", support_email: "" });

  useEffect(() => {
    if (workspace) {
      setForm({
        name: workspace.name || "",
        support_email: workspace.settings?.support_email || "",
      });
    }
  }, [workspace]);

  const handleSave = async () => {
    await workspaceApi.update({ name: form.name, support_email: form.support_email });
    toast.success("Settings saved");
    queryClient.invalidateQueries({ queryKey: ["workspace"] });
  };

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Settings</h1>
      <Card>
        <CardHeader><CardTitle>Workspace Settings</CardTitle></CardHeader>
        <CardContent className="space-y-4 max-w-md">
          <div><Label>Workspace Name</Label><Input value={form.name || workspace?.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></div>
          <div><Label>Support Email</Label><Input value={form.support_email} onChange={(e) => setForm({ ...form, support_email: e.target.value })} /></div>
          <Button onClick={handleSave}>Save Changes</Button>
        </CardContent>
      </Card>
    </div>
  );
}
