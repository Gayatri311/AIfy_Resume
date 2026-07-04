import { API_URL, apiUnreachableMessage } from "./utils";
import type { ResumeAnalysis } from "@/types/resume";

async function apiFetch(input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
  try {
    return await fetch(input, init);
  } catch {
    throw new Error(apiUnreachableMessage());
  }
}

export async function uploadResume(file: File): Promise<{ id: string }> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await apiFetch(`${API_URL}/api/v1/resumes/upload`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    const detail = err.detail;
    const message =
      typeof detail === "string"
        ? detail
        : Array.isArray(detail)
        ? detail.map((d: { msg?: string }) => d.msg).filter(Boolean).join(". ")
        : "Upload failed";
    throw new Error(message || "Upload failed");
  }

  return res.json();
}

export function getOriginalResumeFileUrl(id: string): string {
  return `${API_URL}/api/v1/resumes/${id}/file`;
}

export async function getResumeAnalysis(id: string): Promise<ResumeAnalysis> {
  const res = await apiFetch(`${API_URL}/api/v1/resumes/${id}`, {
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error("Failed to fetch analysis");
  }

  return res.json();
}

export async function updateSectionDiff(
  id: string,
  section: string,
  data: { enhanced: string; accepted?: boolean }
): Promise<ResumeAnalysis> {
  const res = await apiFetch(`${API_URL}/api/v1/resumes/${id}/sections/${section}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to update section");
  }
  return res.json();
}

export async function regenerateSection(
  id: string,
  section: string
): Promise<ResumeAnalysis> {
  const res = await apiFetch(`${API_URL}/api/v1/resumes/${id}/sections/${section}/regenerate`, {
    method: "POST",
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to regenerate section");
  }
  return res.json();
}

export async function updateEnhancedResume(
  id: string,
  enhanced: ResumeAnalysis["enhanced"]
): Promise<ResumeAnalysis> {
  const res = await apiFetch(`${API_URL}/api/v1/resumes/${id}/enhanced`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ enhanced }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to save resume");
  }
  return res.json();
}

export async function updateEnhancedDocument(
  id: string,
  enhanced: string
): Promise<ResumeAnalysis> {
  const res = await apiFetch(`${API_URL}/api/v1/resumes/${id}/document`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ enhanced }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to save resume");
  }
  return res.json();
}

export async function exportResume(
  id: string,
  format: "pdf" | "docx"
): Promise<Blob> {
  const res = await apiFetch(`${API_URL}/api/v1/resumes/${id}/export?format=${format}`);
  if (!res.ok) throw new Error("Export failed");
  return res.blob();
}
