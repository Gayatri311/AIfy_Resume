/** Bold important ATS keywords in resume text for preview/PDF visibility. */

function escapeRegex(text: string): string {
  return text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

export function buildHighlightKeywordsFromResume(
  skills: string[],
  extra: string[] = []
): string[] {
  const seen = new Set<string>();
  const keywords: string[] = [];

  const add = (term: string) => {
    const t = term.trim();
    if (!t || t.length < 2) return;
    const key = t.toLowerCase();
    if (seen.has(key)) return;
    seen.add(key);
    keywords.push(t);
  };

  for (const skill of skills) {
    add(skill);
    for (const part of skill.split(/[,/|]/)) add(part.trim());
  }
  for (const term of extra) add(term);

  return keywords.sort((a, b) => b.length - a.length);
}

export interface TextSegment {
  text: string;
  bold?: boolean;
}

export function splitWithHighlights(text: string, keywords: string[]): TextSegment[] {
  if (!text || !keywords.length) return [{ text }];

  const sorted = [...keywords].sort((a, b) => b.length - a.length);
  const pattern = sorted.map(escapeRegex).join("|");
  if (!pattern) return [{ text }];

  const regex = new RegExp(`(${pattern})`, "gi");
  const parts = text.split(regex);
  if (parts.length <= 1) return [{ text }];

  const lowerSet = new Set(sorted.map((k) => k.toLowerCase()));

  return parts
    .filter((p) => p.length > 0)
    .map((part) => ({
      text: part,
      bold: lowerSet.has(part.toLowerCase()),
    }));
}
