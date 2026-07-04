"use client";

import { AnimatePresence, motion } from "framer-motion";
import Link from "next/link";
import { Check, Loader2, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export const STEPS = [
  "Reading Resume",
  "Understanding Career Journey",
  "Identifying Transferable Skills",
  "Detecting Automation Opportunities",
  "Calculating ATS Score",
  "Finding AI Opportunities",
  "Building AI Career Narrative",
  "Creating Interview Preparation Plan",
] as const;

const INSIGHTS = [
  "Recruiters spend only 6 seconds on first resume review.",
  "Professional Experience is the most important section.",
  "82% of recruiters now search for AI-related skills.",
  "Quantified achievements increase interview callbacks by 40%.",
  "ATS systems reject 75% of resumes before human review.",
] as const;

export function ProcessingScreen({
  completedSteps,
  status,
  insightIndex,
  errorMessage,
  slowMessage,
  activeStepLabel,
}: {
  completedSteps: number;
  status: "processing" | "completed" | "failed";
  insightIndex: number;
  errorMessage?: string;
  slowMessage?: boolean;
  activeStepLabel?: string;
}) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-primary/5 via-background to-violet-50/30 px-4 dark:to-violet-950/20">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-lg"
      >
        <div className="mb-8 text-center">
          <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-primary/10 animate-pulse-ring">
            {status === "completed" ? (
              <Check className="h-10 w-10 text-emerald-500" />
            ) : status === "failed" ? (
              <AlertCircle className="h-10 w-10 text-destructive" />
            ) : (
              <Loader2 className="h-10 w-10 animate-spin text-primary" />
            )}
          </div>
          <h1 className="text-2xl font-bold">
            {status === "completed"
              ? "Analysis Complete!"
              : status === "failed"
              ? "Upload Failed"
              : "Alfying Your Resume..."}
          </h1>
          {status === "failed" ? (
            <p className="mt-3 text-sm text-destructive leading-relaxed max-w-md mx-auto">
              {errorMessage ||
                "Uploaded document does not appear to be a resume. Please try again by uploading your resume."}
            </p>
          ) : (
            <p className="mt-2 text-muted-foreground">
              {status === "completed"
                ? "Opening your resume editor..."
                : slowMessage
                ? activeStepLabel && activeStepLabel.length > 40
                  ? activeStepLabel
                  : "Still working — using smart fallbacks if AI quota is limited."
                : activeStepLabel
                ? `Current step: ${activeStepLabel}`
                : "Estimated time: 15–30 seconds"}
            </p>
          )}
        </div>

        {status === "failed" ? (
          <div className="flex justify-center">
            <Button asChild size="lg">
              <Link href="/upload">Upload Resume Again</Link>
            </Button>
          </div>
        ) : (
        <>
        <div className="rounded-2xl border border-border bg-card p-6 shadow-xl">
          <div className="space-y-4">
            {STEPS.map((step, i) => {
              const done = i < completedSteps;
              const active = i === completedSteps && status === "processing";
              return (
                <motion.div
                  key={step}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className={cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2 transition-colors",
                    active && "bg-primary/5",
                    done && "text-emerald-600 dark:text-emerald-400"
                  )}
                >
                  <div
                    className={cn(
                      "flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs",
                      done
                        ? "bg-emerald-100 text-emerald-600 dark:bg-emerald-900/30"
                        : active
                        ? "bg-primary/20 text-primary"
                        : "bg-muted text-muted-foreground"
                    )}
                  >
                    {done ? <Check className="h-3.5 w-3.5" /> : i + 1}
                  </div>
                  <span className={cn("text-sm", !done && !active && "text-muted-foreground")}>
                    {step}
                  </span>
                  {active && <Loader2 className="ml-auto h-4 w-4 animate-spin text-primary" />}
                </motion.div>
              );
            })}
          </div>
        </div>

        <div className="mt-8 h-16 text-center">
          <AnimatePresence mode="wait">
            <motion.p
              key={insightIndex}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="text-sm italic text-muted-foreground"
            >
              &ldquo;{INSIGHTS[insightIndex % INSIGHTS.length]}&rdquo;
            </motion.p>
          </AnimatePresence>
        </div>
        </>
        )}
      </motion.div>
    </div>
  );
}

