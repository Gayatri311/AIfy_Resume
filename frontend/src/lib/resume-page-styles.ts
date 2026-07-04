export const LETTER_WIDTH = 816;
export const LETTER_HEIGHT = 1056;

/** Scale threshold below which we show a readability note (content still fully included). */
export const SMALL_TEXT_SCALE_THRESHOLD = 0.72;

export function computeOnePageScale(naturalHeight: number): number {
  if (naturalHeight <= LETTER_HEIGHT) return 1;
  return LETTER_HEIGHT / naturalHeight;
}

/** Natural resume layout — never clips content; wrapper scales to fit one page. */
export const ONE_PAGE = {
  page: {
    width: `${LETTER_WIDTH}px`,
    minHeight: `${LETTER_HEIGHT}px`,
    padding: "22px 34px",
    boxSizing: "border-box" as const,
    background: "#ffffff",
    color: "#0f172a",
  },
  name: { fontSize: "22px", fontWeight: 700, margin: 0, lineHeight: 1.15 },
  title: { fontSize: "11px", fontWeight: 700, letterSpacing: "0.1em", textTransform: "uppercase" as const },
  sectionTitle: {
    fontSize: "9.5px",
    fontWeight: 700,
    letterSpacing: "0.12em",
    textTransform: "uppercase" as const,
    marginBottom: "5px",
  },
  sectionGap: "11px",
  body: { fontSize: "10.5px", lineHeight: 1.45 },
  bullet: { fontSize: "10.5px", lineHeight: 1.45, marginBottom: "3px" },
  contact: { fontSize: "9.5px", lineHeight: 1.4 },
};

export function linkedinCompanyUrl(name: string, url?: string): string {
  if (url?.trim()) return url.trim();
  const slug = name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
  return `https://www.linkedin.com/company/${slug}`;
}
