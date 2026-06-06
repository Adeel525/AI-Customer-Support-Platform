"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { FileText, Trash2, Upload } from "lucide-react";
import { useRef, useState } from "react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { knowledgeApi } from "@/lib/api";

export default function KnowledgeBasePage() {
  const fileRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const queryClient = useQueryClient();

  const { data: docs } = useQuery({
    queryKey: ["documents"],
    queryFn: () => knowledgeApi.list().then((r) => r.data),
  });

  const { data: stats } = useQuery({
    queryKey: ["knowledge-stats"],
    queryFn: () => knowledgeApi.stats().then((r) => r.data),
  });

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      await knowledgeApi.upload(file);
      toast.success("Document uploaded and processing started");
      queryClient.invalidateQueries({ queryKey: ["documents"] });
      queryClient.invalidateQueries({ queryKey: ["knowledge-stats"] });
    } catch {
      toast.error("Upload failed");
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  const handleDelete = async (id: string) => {
    await knowledgeApi.delete(id);
    toast.success("Document deleted");
    queryClient.invalidateQueries({ queryKey: ["documents"] });
  };

  const statusVariant = (status: string) => {
    if (status === "indexed") return "success";
    if (status === "failed") return "destructive";
    if (status === "processing") return "warning";
    return "secondary";
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Knowledge Base</h1>
          <p className="mt-1 text-muted-foreground">Upload and manage documents for your AI chatbot.</p>
        </div>
        <div>
          <input ref={fileRef} type="file" className="hidden" accept=".pdf,.docx,.txt,.md,.csv" onChange={handleUpload} />
          <Button onClick={() => fileRef.current?.click()} disabled={uploading}>
            <Upload className="h-4 w-4 mr-2" />
            {uploading ? "Uploading..." : "Upload Document"}
          </Button>
        </div>
      </div>

      {stats && (
        <div className="grid gap-4 md:grid-cols-4 mb-6">
          {[
            { label: "Documents", value: stats.total_documents },
            { label: "Pages Indexed", value: stats.pages_indexed },
            { label: "Tokens", value: stats.tokens_indexed?.toLocaleString() },
            { label: "Coverage", value: `${stats.coverage_score}%` },
          ].map((s) => (
            <Card key={s.label}>
              <CardContent className="pt-6">
                <p className="text-sm text-muted-foreground">{s.label}</p>
                <p className="text-2xl font-bold">{s.value}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Card>
        <CardHeader><CardTitle>Documents</CardTitle></CardHeader>
        <CardContent>
          {docs?.items?.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No documents yet. Upload your first document to get started.</p>
            </div>
          ) : (
            <div className="space-y-2">
              {docs?.items?.map((doc: { id: string; filename: string; status: string; token_count: number }) => (
                <div key={doc.id} className="flex items-center justify-between p-3 rounded-lg border">
                  <div className="flex items-center gap-3">
                    <FileText className="h-5 w-5 text-muted-foreground" />
                    <div>
                      <p className="font-medium">{doc.filename}</p>
                      <p className="text-xs text-muted-foreground">{doc.token_count} tokens</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant={statusVariant(doc.status) as "success"}>{doc.status}</Badge>
                    <Button variant="ghost" size="icon" onClick={() => handleDelete(doc.id)}>
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
