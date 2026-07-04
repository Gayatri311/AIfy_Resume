"use client";

import { useState } from "react";
import { HelpCircle, Lightbulb } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { SECTION_LABELS } from "@/lib/resume-document";
import type { ResumeSuggestion } from "@/types/resume";
import type { ChangeItem } from "@/lib/resume-document";

type Tab = "changes" | "suggestions";

type BadgeVariant = "default" | "outline" | "info" | "accent" | "success" | "warning" | "danger";

function sectionLabel(section: string): string {
  if (SECTION_LABELS[section]) return SECTION_LABELS[section];
  return section.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function sectionBadgeVariant(section: string): BadgeVariant {
  switch (section) {
    case "interview_ready":
      return "accent";
    case "personal":
      return "info";
    case "summary":
      return "default";
    case "experience":
      return "info";
    case "projects":
      return "accent";
    case "skills":
      return "warning";
    case "education":
      return "default";
    default:
      return "outline";
  }
}

function ChangeRow({
  section,
  sectionLabel: label,
  index,
  change,
}: {
  section: string;
  sectionLabel: string;
  index: number;
  change: ChangeItem["change"];
}) {
  return (
    <div className="rounded-lg border border-border bg-card p-3">
      <div className="mb-1.5 flex flex-wrap items-center gap-2">
        <Badge variant={sectionBadgeVariant(section)}>{label}</Badge>
        <span className="text-xs text-muted-foreground">#{index}</span>
      </div>
      <p className="text-sm leading-relaxed text-foreground">{change.why}</p>
      <div className="mt-2 flex flex-wrap gap-1.5">
        <Badge variant="outline">Confidence {change.confidence}%</Badge>
        <Badge
          variant={
            change.authenticity === "SAFE"
              ? "success"
              : change.authenticity === "STRETCH"
              ? "warning"
              : "danger"
          }
        >
          {change.authenticity}
        </Badge>
      </div>
    </div>
  );
}

function SuggestionRow({ item }: { item: ResumeSuggestion }) {
  const label = sectionLabel(item.section);
  const isInterview = item.section === "interview_ready";

  return (
    <div
      className={cn(
        "rounded-lg border bg-card p-3",
        isInterview ? "border-violet-200/80" : "border-border"
      )}
    >
      <div className="mb-1.5 flex flex-wrap items-center gap-2">
        <Badge variant={sectionBadgeVariant(item.section)}>
          {isInterview ? "Interview ready" : label}
        </Badge>
        <span className="text-sm font-medium text-foreground">{item.title}</span>
      </div>
      <p className="text-sm leading-relaxed text-foreground">{item.suggestion}</p>
      <p className="mt-2 text-xs text-muted-foreground">{item.why}</p>
    </div>
  );
}

export function ReviewInsightsPanel({
  changes,
  suggestions,
}: {
  changes: ChangeItem[];
  suggestions: ResumeSuggestion[];
}) {
  const [tab, setTab] = useState<Tab>("suggestions");

  const interviewSuggestions = suggestions.filter((s) => s.section === "interview_ready");
  const otherSuggestions = suggestions.filter((s) => s.section !== "interview_ready");
  const orderedSuggestions = [...interviewSuggestions, ...otherSuggestions];

  return (
    <div className="shrink-0 border-t border-border bg-muted/30">
      <div className="border-b border-border px-4 py-2 sm:px-6">
        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          Resume insights
        </p>
        <div className="mt-2 flex gap-1 rounded-lg bg-muted p-1">
          <button
            type="button"
            onClick={() => setTab("changes")}
            className={cn(
              "flex flex-1 items-center justify-center gap-1.5 rounded-md px-3 py-2 text-sm font-medium transition-colors",
              tab === "changes"
                ? "border border-border bg-background text-foreground"
                : "text-muted-foreground hover:text-foreground"
            )}
          >
            <HelpCircle className="h-4 w-4" />
            What changed & why
            <span className="text-xs text-muted-foreground">({changes.length})</span>
          </button>
          <button
            type="button"
            onClick={() => setTab("suggestions")}
            className={cn(
              "flex flex-1 items-center justify-center gap-1.5 rounded-md px-3 py-2 text-sm font-medium transition-colors",
              tab === "suggestions"
                ? "border border-border bg-background text-foreground"
                : "text-muted-foreground hover:text-foreground"
            )}
          >
            <Lightbulb className="h-4 w-4 text-violet-700" />
            Interview readiness
            <span className="text-xs text-muted-foreground">({orderedSuggestions.length})</span>
          </button>
        </div>
      </div>

      <div className="px-4 py-4 sm:px-6">
        {tab === "changes" ? (
          changes.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              AI rewrite notes will appear here after you upload a resume.
            </p>
          ) : (
            <div className="space-y-2">
              {changes.map((item) => (
                <ChangeRow
                  key={`${item.section}-${item.index}`}
                  section={item.section}
                  sectionLabel={item.sectionLabel}
                  index={item.index}
                  change={item.change}
                />
              ))}
            </div>
          )
        ) : orderedSuggestions.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            Action steps to back up your AI-ready resume will appear here.
          </p>
        ) : (
          <div className="space-y-2">
            {tab === "suggestions" && interviewSuggestions.length > 0 && (
              <p className="text-xs leading-relaxed text-muted-foreground">
                Your resume is positioned for AI roles — complete these steps so you can confidently defend every claim in interviews.
              </p>
            )}
            {orderedSuggestions.map((item, i) => (
              <SuggestionRow key={`${item.section}-${item.title}-${i}`} item={item} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
