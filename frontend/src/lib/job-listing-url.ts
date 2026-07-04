/** Verified job search URLs — uses resume-specific keywords when available. */

/** Strip LinkedIn-style pipe headlines down to a single job title for display. */
export function displayJobRole(role: string): string {
  const t = role.trim();
  if (!t) return role;
  if (t.includes("|")) return t.split("|")[0].trim();
  if (t.length > 55) return `${t.slice(0, 52).trim()}…`;
  return t;
}

export function buildJobListingUrl(
  company: string,
  role: string,
  searchKeywords?: string
): string {
  const cleanRole = displayJobRole(searchKeywords?.trim() || role);
  const query = encodeURIComponent(cleanRole.trim());
  const slug = company.toLowerCase().trim();

  const templates: Record<string, string> = {
    google: `https://www.google.com/about/careers/applications/jobs/results/?q=${query}`,
    microsoft: `https://careers.microsoft.com/us/en/search-results?keywords=${query}`,
    amazon: `https://www.amazon.jobs/en/search?base_query=${query}`,
    salesforce: `https://careers.salesforce.com/en/jobs/?search=${query}`,
    adobe: `https://careers.adobe.com/us/en/search-results?keywords=${query}`,
    stripe: `https://stripe.com/jobs/search?query=${query}`,
    hubspot: `https://www.hubspot.com/careers/jobs?query=${query}`,
    databricks: `https://www.databricks.com/company/careers/open-positions?keywords=${query}`,
    shopify: `https://www.shopify.com/careers/search?query=${query}`,
    atlassian: `https://www.atlassian.com/company/careers/all-jobs?search=${query}`,
  };

  for (const [key, url] of Object.entries(templates)) {
    if (slug.includes(key)) return url;
  }

  const keywords = encodeURIComponent(`${cleanRole} ${company}`.trim());
  return `https://www.linkedin.com/jobs/search/?keywords=${keywords}&f_TPR=r604800`;
}

export function resolveJobLink(company: {
  name: string;
  role: string;
  job_url?: string;
  search_keywords?: string;
}): string {
  const direct = company.job_url?.trim();
  if (direct?.startsWith("http://") || direct?.startsWith("https://")) {
    return direct;
  }
  return buildJobListingUrl(company.name, company.role, company.search_keywords);
}

export function sortByMatchScore(companies: import("@/types/resume").PotentialCompany[]) {
  return [...companies].sort((a, b) => (b.match_score ?? 0) - (a.match_score ?? 0));
}

function matchBadgeVariant(score: number): "success" | "info" | "outline" {
  if (score >= 90) return "success";
  if (score >= 80) return "info";
  return "outline";
}

export function matchScoreBadge(score?: number) {
  if (!score || score < 70) return null;
  return { label: `${score}% match`, variant: matchBadgeVariant(score) as "success" | "info" | "outline" };
}
