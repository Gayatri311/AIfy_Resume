"use client";

import { Maximize2, Save, X } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogTitle,
} from "@/components/ui/dialog";
import { ResumePaper } from "@/components/review/resume-paper";
import type { ResumeData } from "@/types/resume";

interface AiResumeFullscreenProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  data: ResumeData;
  onChange: (data: ResumeData) => void;
  highlightKeywords?: string[];
  isDirty?: boolean;
  saving?: boolean;
  onSave?: () => void;
}

export function AiResumeFullscreen({
  open,
  onOpenChange,
  data,
  onChange,
  highlightKeywords,
  isDirty,
  saving,
  onSave,
}: AiResumeFullscreenProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        className="fixed inset-0 left-0 top-0 z-50 flex h-[100dvh] w-[100vw] max-w-none translate-x-0 translate-y-0 flex-col gap-0 overflow-hidden rounded-none border-0 p-0 shadow-none data-[state=open]:zoom-in-100 data-[state=closed]:zoom-out-100 [&>button.absolute]:hidden"
        aria-describedby="ai-resume-fullscreen-desc"
      >
        <DialogTitle className="sr-only">AI-ready resume full screen editor</DialogTitle>
        <DialogDescription id="ai-resume-fullscreen-desc" className="sr-only">
          View and edit your AI-ready resume in full screen.
        </DialogDescription>

        <header className="flex shrink-0 flex-wrap items-center justify-between gap-3 border-b border-border bg-background px-4 py-3 sm:px-6">
          <div>
            <p className="text-sm font-semibold">AI-Ready Resume</p>
            <p className="text-xs text-muted-foreground">Full screen — edit and scroll freely</p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            {isDirty && <Badge variant="warning">Unsaved edits</Badge>}
            {onSave && (
              <Button size="sm" onClick={onSave} disabled={saving || !isDirty}>
                <Save className="h-4 w-4" />
                {saving ? "Saving..." : "Save changes"}
              </Button>
            )}
            <Button
              variant="outline"
              size="sm"
              onClick={() => onOpenChange(false)}
              aria-label="Close full screen"
            >
              <X className="h-4 w-4" />
              Close
            </Button>
          </div>
        </header>

        <div className="min-h-0 flex-1 overflow-auto bg-[#eef0f3] px-4 py-6 sm:px-8 sm:py-10">
          <div className="mx-auto flex justify-center">
            <div className="rounded-sm bg-slate-200/80 p-6 shadow-2xl">
              <div className="bg-white">
                <ResumePaper
                  data={data}
                  editable
                  highlightKeywords={highlightKeywords}
                  onChange={onChange}
                />
              </div>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

interface AiResumeFullscreenTriggerProps {
  onClick: () => void;
}

export function AiResumeFullscreenTrigger({ onClick }: AiResumeFullscreenTriggerProps) {
  return (
    <Button variant="outline" size="sm" onClick={onClick} aria-label="Open full screen editor">
      <Maximize2 className="h-4 w-4" />
      <span className="hidden sm:inline">Full screen</span>
    </Button>
  );
}
