import { ExternalLink } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { displayJobRole, matchScoreBadge, resolveJobLink } from "@/lib/job-listing-url";
import type { PotentialCompany } from "@/types/resume";

function isLivePosting(company: PotentialCompany): boolean {
  const url = company.job_url?.toLowerCase() || "";
  return (
    company.careers_hint === "Live job posting" ||
    url.includes("gh_jid=") ||
    url.includes("/jobs/view/") ||
    url.includes("/job?") ||
    (url.includes("greenhouse.io") && !url.includes("search"))
  );
}

export function CompanyOpportunityRow({
  company,
  index,
  compact = false,
}: {
  company: PotentialCompany;
  index: number;
  compact?: boolean;
}) {
  const roleLabel = displayJobRole(company.role);
  const jobLink = resolveJobLink(company);
  const match = matchScoreBadge(company.match_score);

  if (compact) {
    return (
      <div className="rounded-lg border border-border bg-card p-3">
        <div className="flex flex-wrap items-start justify-between gap-2">
          <div className="min-w-0 flex-1">
            <p className="text-sm font-semibold">
              {index + 1}. {company.name}
            </p>
            <a
              href={jobLink}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-0.5 inline-flex items-center gap-1 text-xs font-medium text-primary hover:underline"
            >
              {roleLabel}
              <ExternalLink className="h-3 w-3 shrink-0" />
            </a>
          </div>
          {match && <Badge variant={match.variant}>{match.label}</Badge>}
        </div>
        <p className="mt-2 text-xs leading-relaxed text-muted-foreground">
          <span className="font-medium text-foreground">Why you fit: </span>
          {company.fit_reason}
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div className="min-w-0 flex-1">
          <p className="font-semibold">
            {index + 1}. {company.name}
          </p>
          <a
            href={jobLink}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-0.5 inline-flex items-center gap-1 text-sm font-medium text-primary hover:underline"
          >
            {roleLabel}
            <ExternalLink className="h-3.5 w-3.5 shrink-0" />
          </a>
        </div>
        {match ? (
          <Badge variant={match.variant}>{match.label}</Badge>
        ) : isLivePosting(company) ? (
          <Badge variant="success">Live posting</Badge>
        ) : (
          <Badge variant="outline">Strong fit</Badge>
        )}
      </div>
      <p className="mt-2 text-sm text-muted-foreground">
        <span className="font-medium text-foreground">Why you fit: </span>
        {company.fit_reason}
      </p>
      <p className="mt-1 text-sm text-muted-foreground">
        <span className="font-medium text-foreground">Hiring signal: </span>
        {company.why_hiring}
      </p>
      <a
        href={jobLink}
        target="_blank"
        rel="noopener noreferrer"
        className="mt-2 inline-flex items-center gap-1 text-xs font-medium text-primary hover:underline"
      >
        View job posting
        <ExternalLink className="h-3 w-3" />
      </a>
    </div>
  );
}
