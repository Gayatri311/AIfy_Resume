import type { ResumeData } from "@/types/resume";

/** Prepare enhanced resume for save/export — drop empty invented sections. */
export function normalizeEnhancedForSave(data: ResumeData): ResumeData {
  const projects = (data.projects || []).filter(
    (p) => (p.title || "").trim() && (p.description || "").trim()
  );

  const experience = (data.experience || []).map((exp) => ({
    ...exp,
    bullets: (exp.bullets || []).map((b) => b.trim()).filter(Boolean),
  }));

  return {
    ...data,
    projects,
    experience,
    skills: (data.skills || []).map((s) => s.trim()).filter(Boolean),
  };
}

export function resumeDataEquals(a: ResumeData, b: ResumeData): boolean {
  return JSON.stringify(normalizeEnhancedForSave(a)) === JSON.stringify(normalizeEnhancedForSave(b));
}
