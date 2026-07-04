import type { ResumeData, ExperienceItem } from "@/types/resume";

const CONTINUATION_FRAGMENT =
  /^(?:and|or|with|for|to|via|using|including|while|as|through|across|among|within|without|such|that|which|where|when|by|from|into|between|during)\b/i;

function looksLikeContinuationFragment(text: string): boolean {
  const t = text.trim();
  if (!t) return false;
  if (/^[a-z]/.test(t)) return true;
  return CONTINUATION_FRAGMENT.test(t);
}

function mergeContinuationFragments(bullets: string[]): string[] {
  const merged: string[] = [];
  for (const bullet of bullets) {
    const clean = bullet.replace(/^[\u2022\-\*•●▪◦]\s*/, "").trim();
    if (!clean) continue;
    if (merged.length && looksLikeContinuationFragment(clean)) {
      merged[merged.length - 1] = `${merged[merged.length - 1].replace(/\s+$/, "")} ${clean}`;
    } else {
      merged.push(clean);
    }
  }
  return merged;
}

function splitBullets(bullets: string[]): string[] {
  const split = bullets.flatMap((b) => {
    const text = (b || "").trim();
    if (!text) return [];
    if (text.includes("\n")) {
      return text
        .split("\n")
        .map((p) => p.replace(/^[\u2022\-\*•●▪◦]\s*/, "").trim())
        .filter(Boolean);
    }
    if (/[\u2022•●▪]\s+/.test(text)) {
      return text
        .split(/\s*[\u2022•●▪]\s+/)
        .map((p) => p.replace(/^[\u2022\-\*•●▪◦]\s*/, "").trim())
        .filter(Boolean);
    }
    return [text.replace(/^[\u2022\-\*•●▪◦]\s*/, "").trim()].filter(Boolean);
  });
  return mergeContinuationFragments(split);
}

/** Resolve experience bullets for display, preview, and export. */
export function getExperienceBullets(exp: ExperienceItem): string[] {
  return splitBullets(exp.bullets || []);
}

/** Split project description into bullet lines when formatted as bullets. */
export function getProjectBullets(description: string): string[] {
  if (!description?.trim()) return [];
  return splitBullets([description]);
}

export { splitBullets };

function formatPersonalHeader(data: ResumeData): string {
  const { personal } = data;
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
    .map((v) => v!.trim());

  if (contacts.length) lines.push(contacts.join(" | "));
  return lines.join("\n");
}

function formatExperience(data: ResumeData): string {
  if (!data.experience.length) return "";
  return data.experience
    .map((exp) => {
      const header =
        exp.start_date || exp.end_date
          ? `${exp.company} | ${exp.start_date} – ${exp.end_date}`.replace(/\s+\|$/g, "").trim()
          : exp.company;
      const lines = [header, exp.title, ...splitBullets(exp.bullets).map((b) => `• ${b}`)].filter(Boolean);
      return lines.join("\n");
    })
    .join("\n\n");
}

function formatProjects(data: ResumeData): string {
  if (!data.projects.length) return "";
  return data.projects
    .map((p) => {
      const lines = [p.title];
      if (p.description) lines.push(p.description);
      if (p.url) lines.push(p.url);
      return lines.filter(Boolean).join("\n");
    })
    .join("\n\n");
}

function formatEducation(data: ResumeData): string {
  if (!data.education.length) return "";
  return data.education
    .map((e) => {
      if (e.degree && e.institution) {
        return e.year ? `${e.degree} — ${e.institution}, ${e.year}` : `${e.degree} — ${e.institution}`;
      }
      return e.institution || e.degree;
    })
    .join("\n");
}

export function resumeDataToPlainText(data: ResumeData): string {
  const parts: string[] = [];
  const header = formatPersonalHeader(data);
  if (header) parts.push(header);

  if (data.summary?.trim()) {
    parts.push(`Professional Summary\n${data.summary.trim()}`);
  }
  const experience = formatExperience(data);
  if (experience) parts.push(`Professional Experience\n${experience}`);
  const projects = formatProjects(data);
  if (projects) parts.push(`Projects\n${projects}`);
  if (data.skills.length) {
    parts.push(`Skills\n${data.skills.join(", ")}`);
  }
  const education = formatEducation(data);
  if (education) parts.push(`Education\n${education}`);

  return parts.join("\n\n");
}
