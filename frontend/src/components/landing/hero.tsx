"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Play, Sparkles, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";

export function HeroSection() {
  return (
    <section className="relative overflow-hidden py-16 lg:py-24">
      <div className="absolute inset-0 -z-10 bg-gradient-to-br from-primary/5 via-background to-violet-50/50 dark:to-violet-950/20" />
      <div className="mx-auto grid max-w-7xl items-center gap-12 px-4 sm:px-6 lg:grid-cols-2 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <Badge className="mb-6 bg-primary/10 text-primary border-0 px-4 py-1.5 text-xs uppercase tracking-wider">
            ✨ The Expert Mentor Platform
          </Badge>
          <h1 className="text-4xl font-extrabold tracking-tight text-foreground sm:text-5xl lg:text-6xl">
            Transform Your Resume Into an{" "}
            <span className="bg-gradient-to-r from-primary to-violet-500 bg-clip-text text-transparent">
              AI-Ready
            </span>{" "}
            Career
          </h1>
          <p className="mt-6 text-lg text-muted-foreground leading-relaxed">
            Get hired faster by translating your experience into recruiter-friendly AI narratives.
            Optimized by expert algorithms to help you bypass ATS filters and land more interviews.
          </p>
          <div className="mt-8 flex flex-wrap gap-4">
            <Button asChild size="lg">
              <Link href="/upload">Alfy My Resume</Link>
            </Button>
            <Button variant="secondary" size="lg">
              <Play className="h-4 w-4 fill-primary text-primary" />
              Watch Demo
            </Button>
          </div>
          <div className="mt-8 flex items-center gap-3">
            <div className="flex -space-x-2">
              {["A", "B", "C"].map((l, i) => (
                <div
                  key={l}
                  className="flex h-8 w-8 items-center justify-center rounded-full border-2 border-background bg-primary/20 text-xs font-bold text-primary"
                  style={{ zIndex: 3 - i }}
                >
                  {l}
                </div>
              ))}
            </div>
            <p className="text-sm text-muted-foreground">
              Free AI readiness scan · No credit card required
            </p>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="relative"
        >
          <div className="absolute -right-4 top-8 z-10">
            <div className="flex items-center gap-2 rounded-full bg-emerald-50 px-3 py-1.5 text-xs font-medium text-emerald-700 shadow-lg dark:bg-emerald-900/30 dark:text-emerald-400">
              <CheckCircle2 className="h-4 w-4" />
              ATS Gap Identified
            </div>
          </div>
          <div className="rounded-2xl border border-border bg-card p-6 shadow-2xl shadow-primary/10">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                  Resume Analysis
                </p>
                <p className="font-semibold text-foreground">Senior Software Engineer</p>
              </div>
              <div className="rounded-xl bg-primary/10 px-4 py-2 text-center">
                <p className="text-2xl font-bold text-primary">88</p>
                <p className="text-[10px] font-medium uppercase text-muted-foreground">ATS Score</p>
              </div>
            </div>
            <div className="mb-4 flex items-center justify-between rounded-lg bg-muted/50 p-3">
              <div className="flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-primary" />
                <span className="text-sm">AI Readiness</span>
              </div>
              <span className="text-sm font-semibold text-emerald-600">High</span>
            </div>
            <div className="space-y-3">
              <div>
                <div className="mb-1 flex justify-between text-xs">
                  <span>Impact score</span>
                  <span className="font-medium">75%</span>
                </div>
                <Progress value={75} className="h-2" />
              </div>
              <div>
                <div className="mb-1 flex justify-between text-xs">
                  <span>Grammar</span>
                  <span className="font-medium">100%</span>
                </div>
                <Progress value={100} className="h-2 [&>div]:bg-teal-500" />
              </div>
            </div>
            <div className="mt-4 rounded-lg border border-primary/20 bg-primary/5 p-3 text-xs text-muted-foreground">
              Enhanced &ldquo;Managed a team&rdquo; to &ldquo;Spearheaded a multidisciplinary team of 10+,
              increasing output by 25%.&rdquo;
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
