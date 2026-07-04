"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import {
  LayoutDashboard,
  FileBarChart,
  Settings,
  HelpCircle,
  LogOut,
  Lightbulb,
  Rocket,
  Laptop,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getResumeAnalysis } from "@/lib/api";
import type { ResumeAnalysis } from "@/types/resume";
import { cn } from "@/lib/utils";
import { ShareScoreCard } from "@/components/pricing/share-score-card";
import { PotentialCompaniesSection, ColdEmailSection } from "@/components/dashboard/outreach-section";

function ScoreGauge({ score, band }: { score: number; band: string }) {
  const circumference = 2 * Math.PI * 54;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="relative mx-auto h-36 w-36">
      <svg className="h-full w-full -rotate-90" viewBox="0 0 120 120">
        <circle cx="60" cy="60" r="54" fill="none" stroke="currentColor" strokeWidth="8" className="text-muted" />
        <circle
          cx="60"
          cy="60"
          r="54"
          fill="none"
          stroke="currentColor"
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="text-primary transition-all duration-1000"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-3xl font-bold">{score}</span>
        <span className="text-xs font-medium uppercase text-muted-foreground">{band}</span>
      </div>
    </div>
  );
}

function Sidebar({ active }: { active: string }) {
  const links = [
    { href: "#", icon: LayoutDashboard, label: "Dashboard" },
    { href: "#", icon: FileBarChart, label: "My Reports" },
    { href: "#", icon: FileBarChart, label: "Resume Analysis", active: true },
    { href: "#", icon: Settings, label: "Settings" },
  ];

  return (
    <aside className="hidden w-64 shrink-0 flex-col border-r border-border bg-card lg:flex">
      <div className="border-b border-border p-6">
        <h2 className="font-bold text-foreground">Alfy Resume</h2>
        <p className="text-xs text-muted-foreground">AI Career Coach</p>
      </div>
      <nav className="flex-1 space-y-1 p-4">
        {links.map((link) => (
          <Link
            key={link.label}
            href={link.href}
            className={cn(
              "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
              link.active || active === link.label
                ? "bg-primary text-primary-foreground"
                : "text-muted-foreground hover:bg-muted hover:text-foreground"
            )}
          >
            <link.icon className="h-4 w-4" />
            {link.label}
          </Link>
        ))}
      </nav>
      <div className="p-4">
        <Card className="border-primary/20 bg-primary/5">
          <CardContent className="p-4">
            <p className="text-sm font-semibold">Enhance another resume</p>
            <Button asChild size="sm" className="mt-3 w-full">
              <Link href="/upload">Upload new resume</Link>
            </Button>
          </CardContent>
        </Card>
        <div className="mt-4 space-y-2">
          <Link href="#" className="flex items-center gap-2 text-xs text-muted-foreground hover:text-foreground">
            <HelpCircle className="h-3.5 w-3.5" /> Help Center
          </Link>
          <button className="flex items-center gap-2 text-xs text-muted-foreground hover:text-foreground">
            <LogOut className="h-3.5 w-3.5" /> Sign Out
          </button>
        </div>
      </div>
    </aside>
  );
}

export default function DashboardPage() {
  const { id } = useParams<{ id: string }>();
  const [analysis, setAnalysis] = useState<ResumeAnalysis | null>(null);

  useEffect(() => {
    if (id) getResumeAnalysis(id).then(setAnalysis);
  }, [id]);

  if (!analysis) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  const {
    scores,
    gap_analysis,
    suggested_projects,
    next_actions,
    confidence_strengths,
    experience_gaps,
    potential_companies,
    cold_email,
    outreach_tip,
  } = analysis;

  return (
    <div className="flex min-h-screen bg-muted/30">
      <Sidebar active="Resume Analysis" />
      <main className="flex-1 overflow-auto p-6 lg:p-8">
        <div className="mx-auto max-w-6xl">
          <div className="mb-8 grid gap-6 lg:grid-cols-3 lg:items-start">
            <div className="space-y-6 lg:col-span-2">
              <Card className="lg:self-start">
                <CardHeader>
                  <CardTitle>Your AI Readiness</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-col items-center gap-8 sm:flex-row">
                    <ScoreGauge score={scores.ai_readiness} band={scores.band} />
                    <div className="flex-1">
                      <p className="text-sm text-muted-foreground leading-relaxed">
                        You&apos;ve integrated AI terminology well into your experience narrative.
                        To reach 80+, add technical &ldquo;hard-proof&rdquo; projects that demonstrate
                        hands-on AI application aligned with your enhanced claims.
                      </p>
                      <div className="mt-4 grid gap-4 sm:grid-cols-2">
                        <div>
                          <p className="mb-2 text-xs font-semibold uppercase text-muted-foreground">
                            Confidence Check
                          </p>
                          {(confidence_strengths || []).map((s) => (
                            <div key={s.label} className="mb-2 flex items-center justify-between text-sm">
                              <span>{s.label}</span>
                              <Badge variant="success">{s.level}</Badge>
                            </div>
                          ))}
                        </div>
                        <div>
                          <p className="mb-2 text-xs font-semibold uppercase text-muted-foreground">
                            Experience Gaps
                          </p>
                          {(experience_gaps || []).map((g) => (
                            <div key={g.label} className="mb-2 flex items-center justify-between text-sm">
                              <span>{g.label}</span>
                              <Badge variant={g.level === "MISSING" ? "danger" : "warning"}>
                                {g.level}
                              </Badge>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="overflow-hidden">
                <CardContent className="p-0">
                  <div className="grid lg:grid-cols-3">
                    <div className="p-8 lg:col-span-2">
                      <Badge className="mb-4">Priority Action</Badge>
                      <h3 className="text-xl font-bold">Bridge the &ldquo;Hard Skill&rdquo; Gap</h3>
                      <p className="mt-3 text-muted-foreground leading-relaxed">
                        Your resume claims AI proficiency, but your portfolio lacks a central anchor project.
                        Complete a hands-on project to provide technical evidence recruiters expect.
                      </p>
                      <div className="mt-6 flex flex-wrap gap-3">
                        <Button asChild>
                          <Link href={`/interview/${id}`}>Start Project Guide</Link>
                        </Button>
                        <Button variant="secondary" asChild>
                          <Link href={`/preview/${id}`}>View Final Resume</Link>
                        </Button>
                      </div>
                      {gap_analysis.missing_skills.length > 0 && (
                        <div className="mt-6">
                          <p className="text-sm font-medium">Missing Skills</p>
                          <div className="mt-2 flex flex-wrap gap-2">
                            {gap_analysis.missing_skills.map((s) => (
                              <Badge key={s} variant="danger">{s}</Badge>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                    <div className="hidden items-center justify-center bg-muted/50 p-8 lg:flex">
                      <Laptop className="h-24 w-24 text-muted-foreground/30" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="space-y-6">
              <ShareScoreCard
                score={scores.ai_readiness}
                band={scores.band}
                name={analysis.original.personal.name}
              />

              <Card className="border-0 bg-gradient-to-br from-primary to-violet-600 text-white">
                <CardContent className="p-6">
                  <Lightbulb className="mb-3 h-6 w-6" />
                  <p className="font-semibold">Expert Tips</p>
                  <p className="mt-2 text-sm opacity-90">
                    Interviewers will ask HOW you used AI. Prepare a specific example with tools,
                    prompts, and measurable outcomes.
                  </p>
                  <div className="mt-4 rounded-lg bg-white/10 p-3 text-xs">
                    <p className="font-medium">Golden Phrase</p>
                    <p className="mt-1 opacity-90">
                      &ldquo;I leveraged AI-assisted workflows to automate [task], reducing manual effort by [X]% using [tool/method].&rdquo;
                    </p>
                  </div>
                </CardContent>
              </Card>

              {suggested_projects[0] && (
                <Card className="border-blue-200 bg-blue-50/50 dark:border-blue-900 dark:bg-blue-950/20">
                  <CardContent className="p-6">
                    <Rocket className="mb-3 h-6 w-6 text-blue-600" />
                    <p className="font-semibold">Next Best Project</p>
                    <p className="mt-2 text-sm text-muted-foreground">
                      {suggested_projects[0].title}
                    </p>
                    <Button variant="outline" size="sm" className="mt-4">
                      View Project Guide
                    </Button>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>

          <div className="mb-6 grid gap-4 sm:grid-cols-4">
            {[
              { label: "ATS Score", value: scores.ats_score },
              { label: "AI Terminology", value: scores.ai_terminology },
              { label: "Technical Depth", value: scores.technical_depth },
              { label: "Measurable Impact", value: scores.measurable_achievements },
            ].map((metric) => (
              <Card key={metric.label}>
                <CardContent className="p-4 text-center">
                  <p className="text-2xl font-bold text-primary">{metric.value}</p>
                  <p className="text-xs text-muted-foreground">{metric.label}</p>
                </CardContent>
              </Card>
            ))}
          </div>

          {next_actions.length > 0 && (
            <div className="mt-8">
              <h3 className="mb-4 text-lg font-semibold">Next Best Actions</h3>
              <div className="grid gap-4 sm:grid-cols-3">
                {next_actions.map((action) => (
                  <Card key={action.title}>
                    <CardContent className="p-4">
                      <Badge variant="outline" className="mb-2 capitalize">{action.type}</Badge>
                      <p className="font-medium">{action.title}</p>
                      <p className="mt-1 text-sm text-muted-foreground">{action.description}</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}

          <PotentialCompaniesSection
            companies={potential_companies ?? []}
            outreachTip={outreach_tip}
          />

          {cold_email && <ColdEmailSection email={cold_email} />}
        </div>
      </main>
    </div>
  );
}
