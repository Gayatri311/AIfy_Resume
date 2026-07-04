"use client";

import { useState } from "react";
import { Building2, Copy, Check, Mail } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CompanyOpportunityRow } from "@/components/dashboard/company-opportunity-row";
import { sortByMatchScore } from "@/lib/job-listing-url";
import type { ColdEmail, PotentialCompany } from "@/types/resume";

function CopyButton({ text, label }: { text: string; label: string }) {
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Button variant="outline" size="sm" onClick={copy}>
      {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
      {copied ? "Copied" : label}
    </Button>
  );
}

export function PotentialCompaniesSection({
  companies,
  outreachTip,
}: {
  companies: PotentialCompany[];
  outreachTip?: string;
}) {
  if (!companies.length) return null;

  const ranked = sortByMatchScore(companies);

  return (
    <Card className="mt-8">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Building2 className="h-5 w-5 text-primary" />
          Best Matching Jobs
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          Ranked by resume fit. Links open live job postings when available.
        </p>
      </CardHeader>
      <CardContent>
        {outreachTip && (
          <div className="mb-4 rounded-lg border border-primary/20 bg-primary/5 p-3 text-sm leading-relaxed">
            {outreachTip}
          </div>
        )}
        <div className="space-y-3">
          {ranked.map((company, i) => (
            <CompanyOpportunityRow key={`${company.name}-${company.role}-${i}`} company={company} index={i} />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

export function ColdEmailSection({ email }: { email: ColdEmail }) {
  if (!email?.body) return null;

  const fullEmail = `Subject: ${email.subject}\n\n${email.body}`;

  return (
    <Card className="mt-6">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Mail className="h-5 w-5 text-primary" />
          Cold Email Template
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          Attach your PDF resume. Personalize [Hiring Manager] and the first line for each company.
        </p>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <p className="mb-1 text-xs font-semibold uppercase text-muted-foreground">Subject</p>
          <p className="rounded-md border border-border bg-muted/30 px-3 py-2 text-sm font-medium">
            {email.subject}
          </p>
        </div>
        <div>
          <p className="mb-1 text-xs font-semibold uppercase text-muted-foreground">Body</p>
          <pre className="whitespace-pre-wrap rounded-md border border-border bg-muted/30 px-3 py-3 text-sm leading-relaxed font-sans">
            {email.body}
          </pre>
        </div>
        <div className="flex flex-wrap gap-2">
          <CopyButton text={email.subject} label="Copy subject" />
          <CopyButton text={email.body} label="Copy body" />
          <CopyButton text={fullEmail} label="Copy full email" />
        </div>
      </CardContent>
    </Card>
  );
}
