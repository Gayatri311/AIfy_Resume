export const NO_CHANGE_NOTE =
  "\n\n—\nNote: No change required for this section.";

export function stripNoChangeNote(text: string): string {
  return text.replace(NO_CHANGE_NOTE, "").trim();
}

export type ResumeFormat = "classic" | "modern" | "minimal";

export const RESUME_FORMATS: {
  id: ResumeFormat;
  name: string;
  description: string;
}[] = [
  {
    id: "classic",
    name: "Classic Professional",
    description: "Indigo accents, clean ATS-friendly layout",
  },
  {
    id: "modern",
    name: "Modern Executive",
    description: "Navy header band with teal highlights",
  },
  {
    id: "minimal",
    name: "Minimal Serif",
    description: "Black & white, timeless serif typography",
  },
];
