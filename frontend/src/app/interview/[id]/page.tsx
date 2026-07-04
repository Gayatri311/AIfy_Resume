"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft, MessageSquare } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { getResumeAnalysis } from "@/lib/api";
import type { InterviewQuestion } from "@/types/resume";

const CATEGORY_COLORS: Record<string, string> = {
  Behavioral: "bg-blue-100 text-blue-700",
  Technical: "bg-purple-100 text-purple-700",
  AI: "bg-emerald-100 text-emerald-700",
  "Scenario-based": "bg-amber-100 text-amber-700",
};

export default function InterviewPage() {
  const { id } = useParams<{ id: string }>();
  const [questions, setQuestions] = useState<InterviewQuestion[]>([]);

  useEffect(() => {
    if (id) {
      getResumeAnalysis(id).then((a) => setQuestions(a.interview_questions));
    }
  }, [id]);

  const grouped = questions.reduce(
    (acc, q) => {
      if (!acc[q.category]) acc[q.category] = [];
      acc[q.category].push(q);
      return acc;
    },
    {} as Record<string, InterviewQuestion[]>
  );

  return (
    <div className="min-h-screen bg-muted/30">
      <header className="border-b border-border bg-background">
        <div className="mx-auto flex h-14 max-w-4xl items-center gap-4 px-4">
          <Button variant="ghost" size="sm" asChild>
            <Link href={`/dashboard/${id}`}>
              <ArrowLeft className="h-4 w-4" /> Back to Dashboard
            </Link>
          </Button>
          <h1 className="font-semibold">Interview Preparation</h1>
        </div>
      </header>

      <main className="mx-auto max-w-4xl px-4 py-8">
        <div className="mb-8 text-center">
          <MessageSquare className="mx-auto mb-4 h-10 w-10 text-primary" />
          <h2 className="text-2xl font-bold">Tailored Interview Questions</h2>
          <p className="mt-2 text-muted-foreground">
            Generated from your enhanced resume — prepare honest, specific answers.
          </p>
        </div>

        {Object.entries(grouped).map(([category, qs]) => (
          <div key={category} className="mb-8">
            <Badge className={`mb-4 ${CATEGORY_COLORS[category] || ""}`}>{category}</Badge>
            <div className="space-y-3">
              {qs.map((q, i) => (
                <Card key={q.id}>
                  <CardContent className="flex gap-4 p-4">
                    <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10 text-sm font-bold text-primary">
                      {i + 1}
                    </span>
                    <p className="text-sm leading-relaxed">{q.question}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        ))}

        <div className="mt-8 text-center">
          <Button asChild size="lg">
            <Link href={`/preview/${id}`}>View Final Resume →</Link>
          </Button>
        </div>
      </main>
    </div>
  );
}
