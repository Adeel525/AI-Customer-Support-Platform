"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Globe, RefreshCw } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { crawlerApi } from "@/lib/api";

export default function SourcesPage() {
  const [url, setUrl] = useState("");
  const queryClient = useQueryClient();

  const { data } = useQuery({
    queryKey: ["crawler-jobs"],
    queryFn: () => crawlerApi.list().then((r) => r.data),
  });

  const handleAdd = async () => {
    if (!url) return;
    await crawlerApi.create(url);
    toast.success("Crawler job created");
    setUrl("");
    queryClient.invalidateQueries({ queryKey: ["crawler-jobs"] });
  };

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Website Sources</h1>
      <Card className="mb-6">
        <CardHeader><CardTitle>Add Website</CardTitle></CardHeader>
        <CardContent className="flex gap-2">
          <Input placeholder="https://docs.example.com" value={url} onChange={(e) => setUrl(e.target.value)} />
          <Button onClick={handleAdd}>Crawl</Button>
        </CardContent>
      </Card>
      <div className="space-y-2">
        {data?.items?.map((job: { id: string; url: string; status: string; pages_crawled: number; last_sync: string }) => (
          <div key={job.id} className="flex items-center justify-between p-4 rounded-lg border">
            <div className="flex items-center gap-3">
              <Globe className="h-5 w-5" />
              <div>
                <p className="font-medium">{job.url}</p>
                <p className="text-xs text-muted-foreground">{job.pages_crawled} pages crawled</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Badge>{job.status}</Badge>
              <Button variant="ghost" size="icon" onClick={() => crawlerApi.sync(job.id)}>
                <RefreshCw className="h-4 w-4" />
              </Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
