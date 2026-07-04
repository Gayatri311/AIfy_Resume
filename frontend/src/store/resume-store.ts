import { create } from "zustand";
import type { ResumeAnalysis } from "@/types/resume";

interface ResumeStore {
  analysis: ResumeAnalysis | null;
  setAnalysis: (analysis: ResumeAnalysis) => void;
}

export const useResumeStore = create<ResumeStore>((set) => ({
  analysis: null,
  setAnalysis: (analysis) => set({ analysis }),
}));
