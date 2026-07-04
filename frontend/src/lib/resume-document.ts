import type { ResumeAnalysis, ChangeExplanation } from "@/types/resume";
import { stripNoChangeNote } from "@/lib/resume-utils";

export const SECTION_ORDER = ["summary", "experience", "projects", "skills", "education"] as const;

export const SECTION_LABELS: Record<string, string> = {
  summary: "Professional Summary",
  experience: "Professional Experience",
  projects: "Projects",
  skills: "Skills",
  education: "Education",
  personal: "Contact",
  general: "General",
  interview_ready: "Interview readiness",
};

const DEFAULT_HEADINGS: Record<string, string> = {
  summary: "Professional Summary",
  experience: "Professional Experience",
  projects: "Projects",
  skills: "Skills",
  education: "Education",
};

const EMPTY_LABELS: Record<string, string> = {
  summary: "No summary found in your resume.",
  experience: "No professional experience found in your resume.",
  projects: "No projects listed in your resume.",
  skills: "No skills listed in your resume.",
  education: "No education listed in your resume.",
};

function formatPersonalHeader(analysis: ResumeAnalysis): string {
  const personal = analysis.enhanced.personal?.name
    ? analysis.enhanced.personal
    : analysis.original.personal;
  const lines: string[] = [];
  if (personal.name) lines.push(personal.name.trim());
  if (personal.title) lines.push(personal.title.trim());

  const contacts = [
    personal.phone,
    personal.email,
    personal.location,
    personal.linkedin,
    personal.github,
    personal.website,
  ]
    .filter(Boolean)
    .map((value) => value!.trim());

  if (contacts.length) lines.push(contacts.join(" | "));
  return lines.join("\n");
}

function isEmptySection(text: string, section: string): boolean {
  const clean = text.trim();
  return !clean || clean === EMPTY_LABELS[section];
}

function sectionHeading(original: string, section: string): string {
  if (original && !isEmptySection(original, section)) {
    const first = original.split("\n", 1)[0]?.trim();
    if (first) return first;
  }
  return DEFAULT_HEADINGS[section] || section;
}

function formatSectionBlock(original: string, enhanced: string, section: string): string {
  const body = stripNoChangeNote(enhanced).trim();
  if (!body || isEmptySection(body, section)) return "";

  const heading = sectionHeading(original, section);
  const firstLine = body.split("\n", 1)[0]?.trim().toLowerCase();
  if (firstLine === heading.toLowerCase()) return body;
  return `${heading}\n${body}`;
}

export function buildFullOriginal(analysis: ResumeAnalysis): string {
  if (analysis.full_original?.trim()) return analysis.full_original;

  const parts: string[] = [];
  const header = formatPersonalHeader(analysis);
  if (header) parts.push(header);

  for (const section of SECTION_ORDER) {
    const diff = analysis.diffs.find((d) => d.section === section);
    if (!diff?.original || isEmptySection(diff.original, section)) continue;
    parts.push(diff.original.trim());
  }

  return parts.join("\n\n");
}

export function buildFullEnhanced(analysis: ResumeAnalysis): string {
  if (analysis.full_enhanced?.trim()) return analysis.full_enhanced;

  const parts: string[] = [];
  const header = formatPersonalHeader(analysis);
  if (header) parts.push(header);

  for (const section of SECTION_ORDER) {
    const diff = analysis.diffs.find((d) => d.section === section);
    if (!diff) continue;
    const block = formatSectionBlock(diff.original, diff.enhanced, section);
    if (block) parts.push(block);
  }

  return parts.join("\n\n");
}

export interface ChangeItem {
  section: string;
  sectionLabel: string;
  change: ChangeExplanation;
  index: number;
}

export function collectAllChanges(analysis: ResumeAnalysis): ChangeItem[] {
  const items: ChangeItem[] = [];
  let index = 1;

  for (const section of SECTION_ORDER) {
    const diff = analysis.diffs.find((d) => d.section === section);
    if (!diff?.changes?.length) continue;

    for (const change of diff.changes) {
      items.push({
        section,
        sectionLabel: SECTION_LABELS[section] || section,
        change,
        index: index++,
      });
    }
  }

  return items;
}
