"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { Sparkles, Save, FileText, Eye } from "lucide-react";
import { Navbar } from "@/components/layout/navbar";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ResumePaper } from "@/components/review/resume-paper";
import { ReviewInsightsPanel } from "@/components/review/review-insights-panel";
import { getResumeAnalysis, updateEnhancedResume } from "@/lib/api";
import { collectAllChanges } from "@/lib/resume-document";
import { buildHighlightKeywordsFromResume } from "@/lib/keyword-highlight";
import { normalizeEnhancedForSave, resumeDataEquals } from "@/lib/resume-save";
import type { ResumeData } from "@/types/resume";
import { useResumeStore } from "@/store/resume-store";
import { OriginalDocumentViewer } from "@/components/review/original-document-viewer";
import {
  AiResumeFullscreen,
  AiResumeFullscreenTrigger,
} from "@/components/review/ai-resume-fullscreen";

function cloneResumeData(data: ResumeData): ResumeData {
  return JSON.parse(JSON.stringify(data));
}

export default function ReviewPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const { analysis, setAnalysis } = useResumeStore();
  const [enhancedData, setEnhancedData] = useState<ResumeData | null>(null);
  const [savedSnapshot, setSavedSnapshot] = useState<ResumeData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [fullscreenOpen, setFullscreenOpen] = useState(false);

  useEffect(() => {
    if (!id) return;

    let cancelled = false;
    let pollTimer: ReturnType<typeof setInterval> | null = null;

    const load = async () => {
      try {
        const data = await getResumeAnalysis(id);
        if (cancelled) return;

        if (data.status === "processing" || data.status === "pending") {
          router.replace(`/processing/${id}`);
          return;
        }

        if (data.status === "failed") {
          router.replace(`/processing/${id}`);
          return;
        }

        if (pollTimer) {
          clearInterval(pollTimer);
          pollTimer = null;
        }

        setAnalysis(data);
        const normalized = normalizeEnhancedForSave(cloneResumeData(data.enhanced));
        setEnhancedData(normalized);
        setSavedSnapshot(cloneResumeData(normalized));
        setLoading(false);
      } catch (err) {
        if (cancelled) return;
        setLoadError(
          err instanceof Error ? err.message : "Failed to load resume. Is the backend running?"
        );
        setLoading(false);
        if (pollTimer) clearInterval(pollTimer);
      }
    };

    load();
    pollTimer = setInterval(load, 3000);

    return () => {
      cancelled = true;
      if (pollTimer) clearInterval(pollTimer);
    };
  }, [id, setAnalysis, router]);

  const changes = useMemo(
    () => (analysis ? collectAllChanges(analysis) : []),
    [analysis]
  );

  const highlightKeywords = useMemo(() => {
    if (!analysis) return [];
    if (analysis.highlight_keywords?.length) return analysis.highlight_keywords;
    return buildHighlightKeywordsFromResume(
      analysis.enhanced.skills,
      analysis.missing_keywords ?? []
    );
  }, [analysis]);

  const isDirty = useMemo(() => {
    if (!enhancedData || !savedSnapshot) return false;
    return !resumeDataEquals(enhancedData, savedSnapshot);
  }, [enhancedData, savedSnapshot]);

  const suggestions = analysis?.suggestions ?? [];

  const handleSave = async () => {
    if (!id || !enhancedData) return;
    setActionError(null);
    setSaveSuccess(false);
    setSaving(true);
    try {
      const payload = normalizeEnhancedForSave(enhancedData);
      const updated = await updateEnhancedResume(id, payload);
      setAnalysis(updated);
      const normalized = normalizeEnhancedForSave(cloneResumeData(updated.enhanced));
      setEnhancedData(normalized);
      setSavedSnapshot(cloneResumeData(normalized));
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 2500);
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "Failed to save resume.");
    } finally {
      setSaving(false);
    }
  };

  const handleEnhancedChange = (data: ResumeData) => {
    setSaveSuccess(false);
    setEnhancedData(normalizeEnhancedForSave(data));
  };

  const handlePreview = () => {
    if (isDirty) {
      const ok = window.confirm("You have unsaved edits. Save before preview?");
      if (ok) {
        handleSave().then(() => router.push(`/preview/${id}`));
        return;
      }
    }
    router.push(`/preview/${id}`);
  };

  if (loadError) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 px-4 text-center">
        <p className="text-destructive">{loadError}</p>
        <Button asChild variant="secondary">
          <Link href="/upload">Back to upload</Link>
        </Button>
      </div>
    );
  }

  if (loading || !analysis || !enhancedData) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar showCta={false} />

      <header className="border-b border-border bg-background">
        <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-3 sm:px-6">
          <div>
            <h1 className="text-lg font-semibold sm:text-xl">Resume Editor</h1>
            <p className="text-sm text-muted-foreground">
              Original on the left — AI-ready rewrite on the right.
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="info">
              AI Readiness: {Math.round(analysis.scores.ai_readiness)}%
            </Badge>
            <Badge variant="default">ATS: {Math.round(analysis.scores.ats_score)}%</Badge>
            {isDirty && <Badge variant="warning">Unsaved edits</Badge>}
            {saveSuccess && <Badge variant="success">Saved</Badge>}
            <Button variant="secondary" size="sm" onClick={handlePreview}>
              <Eye className="h-4 w-4" />
              Preview
            </Button>
            <Button size="sm" onClick={handleSave} disabled={saving || !isDirty}>
              <Save className="h-4 w-4" />
              {saving ? "Saving..." : "Save changes"}
            </Button>
          </div>
        </div>
        {actionError && (
          <div className="border-t border-destructive/30 bg-destructive/10 px-4 py-2 text-sm text-destructive sm:px-6">
            {actionError}
          </div>
        )}
      </header>

      <div className="grid grid-cols-1 items-start lg:grid-cols-2">
        <section className="border-b border-border lg:border-b-0 lg:border-r">
          <div className="flex items-center gap-2 border-b border-border bg-white px-4 py-2.5">
            <FileText className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm font-medium">Original Document</span>
            <Badge variant="outline" className="ml-auto max-w-[180px] truncate">
              {analysis.original_filename || "Uploaded file"}
            </Badge>
          </div>
          <OriginalDocumentViewer
            resumeId={id!}
            filename={analysis.original_filename}
            fileType={analysis.original_file_type}
          />
        </section>

        <section className="bg-[#eef0f3]">
          <div className="flex items-center gap-2 border-b border-border bg-white px-4 py-2.5">
            <Sparkles className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm font-medium">AI-Ready Resume</span>
            <div className="ml-auto flex items-center gap-2">
              <Badge variant="success">ATS formatted · editable</Badge>
              <AiResumeFullscreenTrigger onClick={() => setFullscreenOpen(true)} />
            </div>
          </div>
          <div className="flex justify-center overflow-x-auto px-4 py-6 sm:px-6 sm:py-8">
            <div className="rounded-sm bg-slate-200/80 p-6 shadow-2xl">
              <div className="bg-white">
                <ResumePaper
                  data={enhancedData}
                  editable
                  highlightKeywords={highlightKeywords}
                  onChange={handleEnhancedChange}
                />
              </div>
            </div>
          </div>
        </section>
      </div>

      <AiResumeFullscreen
        open={fullscreenOpen}
        onOpenChange={setFullscreenOpen}
        data={enhancedData}
        onChange={handleEnhancedChange}
        highlightKeywords={highlightKeywords}
        isDirty={isDirty}
        saving={saving}
        onSave={handleSave}
      />

      <ReviewInsightsPanel changes={changes} suggestions={suggestions} />

      <footer className="border-t border-border px-4 py-4 text-center text-sm text-muted-foreground sm:px-6">
        <button
          type="button"
          onClick={handlePreview}
          className="text-primary underline-offset-2 hover:underline"
        >
          Open preview & download PDF
        </button>
      </footer>
    </div>
  );
}
