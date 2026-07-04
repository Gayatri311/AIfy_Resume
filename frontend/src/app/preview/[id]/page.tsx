"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft, Download, Check, LayoutDashboard } from "lucide-react";
import { Button } from "@/components/ui/button";
import { getResumeAnalysis } from "@/lib/api";
import { ResumePaper } from "@/components/review/resume-paper";
import { downloadResumePdf } from "@/lib/pdf-export";
import { buildHighlightKeywordsFromResume } from "@/lib/keyword-highlight";
import type { ResumeAnalysis } from "@/types/resume";

export default function PreviewPage() {
  const { id } = useParams<{ id: string }>();
  const resumeRef = useRef<HTMLDivElement>(null);
  const [analysis, setAnalysis] = useState<ResumeAnalysis | null>(null);
  const [exporting, setExporting] = useState(false);
  const [exported, setExported] = useState(false);

  useEffect(() => {
    if (id) getResumeAnalysis(id).then(setAnalysis);
  }, [id]);

  const highlightKeywords = useMemo(() => {
    if (!analysis) return [];
    if (analysis.highlight_keywords?.length) return analysis.highlight_keywords;
    return buildHighlightKeywordsFromResume(
      analysis.enhanced.skills,
      analysis.missing_keywords ?? []
    );
  }, [analysis]);

  const handleDownload = async () => {
    if (!resumeRef.current || !analysis?.enhanced) return;
    setExporting(true);
    setExported(false);
    try {
      const page = resumeRef.current.querySelector(".resume-export-page") as HTMLElement | null;
      if (!page) throw new Error("Resume not found");
      const name = analysis.enhanced.personal.name.replace(/\s+/g, "-").toLowerCase() || "resume";
      await downloadResumePdf(page, `${name}-resume.pdf`, { watermark: false });
      setExported(true);
      setTimeout(() => setExported(false), 3000);
    } catch (e) {
      console.error("PDF export error:", e);
      const msg = e instanceof Error ? e.message : "Unknown error";
      alert(`PDF export failed: ${msg}`);
    } finally {
      setExporting(false);
    }
  };

  if (!analysis) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  const resume = analysis.enhanced;

  return (
    <div className="min-h-screen bg-muted/50">
      <header className="sticky top-0 z-10 border-b border-border bg-background/80 backdrop-blur-lg">
        <div className="mx-auto flex h-14 max-w-5xl items-center justify-between gap-2 px-4">
          <Button variant="ghost" size="sm" asChild>
            <Link href={`/review/${id}`}>
              <ArrowLeft className="h-4 w-4" /> Back to Editor
            </Link>
          </Button>
          <h1 className="hidden font-semibold sm:block">Resume Preview</h1>
          <div className="flex items-center gap-2">
            <Button variant="secondary" size="sm" asChild>
              <Link href={`/dashboard/${id}`}>
                <LayoutDashboard className="h-4 w-4" />
                Dashboard
              </Link>
            </Button>
            <Button size="sm" disabled={exporting} onClick={handleDownload}>
              {exported ? (
                <>
                  <Check className="h-4 w-4" /> Downloaded
                </>
              ) : (
                <>
                  <Download className="h-4 w-4" />
                  {exporting ? "Generating..." : "Download PDF"}
                </>
              )}
            </Button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-4 py-8">
        <p className="mb-6 text-center text-sm text-muted-foreground">
          Full-size preview — download matches this layout exactly (multi-page letter PDF when needed).
        </p>

        <div className="flex justify-center overflow-x-auto">
          <div className="rounded-sm bg-slate-200/80 p-6 shadow-2xl">
            <div id="resume-export-wrapper" ref={resumeRef} className="bg-white">
              <ResumePaper data={resume} highlightKeywords={highlightKeywords} />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
