"use client";

import { useQuery } from "@tanstack/react-query";
import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { analyticsApi } from "@/lib/api";

export default function AnalyticsPage() {
  const { data } = useQuery({
    queryKey: ["analytics-overview"],
    queryFn: () => analyticsApi.overview().then((r) => r.data),
  });

  const confidenceData = data?.confidence_trend || [];
  const questionsData = (data?.top_questions || []).map((q: { question: string; count: number }) => ({
    question: q.question.slice(0, 30),
    count: q.count,
  }));

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
        <p className="mt-1 text-muted-foreground">Track chatbot performance and customer satisfaction.</p>
      </div>
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Chatbot Accuracy Trend</CardTitle></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={confidenceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="accuracy" stroke="hsl(160, 84%, 39%)" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Top Questions</CardTitle></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={questionsData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="question" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="hsl(160, 84%, 39%)" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
