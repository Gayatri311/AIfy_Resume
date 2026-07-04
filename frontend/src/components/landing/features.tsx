"use client";

import { motion } from "framer-motion";
import {
  Gauge,
  FilePen,
  TrendingUp,
  Search,
  Brain,
  MessageSquare,
  GitCompare,
  FolderKanban,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

const features = [
  {
    icon: Gauge,
    title: "AI Readiness Score",
    description: "Real-time scoring based on actual recruiter data and current market requirements for your target roles.",
    color: "bg-violet-100 text-violet-600 dark:bg-violet-900/30",
  },
  {
    icon: FilePen,
    title: "Resume Rewrite",
    description: "One-click AI transformation of your bullet points into high-impact, data-driven achievement statements.",
    color: "bg-teal-100 text-teal-600 dark:bg-teal-900/30",
  },
  {
    icon: TrendingUp,
    title: "Skill Analysis",
    description: "Discover skill gaps and get personalized recommendations for certifications and learning paths.",
    color: "bg-amber-100 text-amber-600 dark:bg-amber-900/30",
  },
  {
    icon: Search,
    title: "ATS Optimization",
    description: "Identify missing keywords and formatting issues that cause ATS rejections before recruiters see your resume.",
    color: "bg-blue-100 text-blue-600 dark:bg-blue-900/30",
  },
  {
    icon: Brain,
    title: "Experience Enhancement",
    description: "Plausible AI framing of your existing work — never fabricated, always authentic extensions.",
    color: "bg-purple-100 text-purple-600 dark:bg-purple-900/30",
  },
  {
    icon: MessageSquare,
    title: "Interview Readiness",
    description: "15 tailored questions generated from your enhanced resume to prepare you for real interviews.",
    color: "bg-rose-100 text-rose-600 dark:bg-rose-900/30",
  },
  {
    icon: FolderKanban,
    title: "AI Project Suggestions",
    description: "Role-specific project ideas with tech stacks, architecture, and implementation roadmaps.",
    color: "bg-indigo-100 text-indigo-600 dark:bg-indigo-900/30",
  },
  {
    icon: GitCompare,
    title: "Resume Diff Comparison",
    description: "GitHub-style section-by-section diff review with accept, reject, edit, and explain for every change.",
    color: "bg-emerald-100 text-emerald-600 dark:bg-emerald-900/30",
  },
];

const steps = [
  { num: 1, title: "Upload", desc: "PDF, Docx, or LinkedIn Profile import." },
  { num: 2, title: "Analyze", desc: "AI dissects your experience and impact." },
  { num: 3, title: "Identify Gaps", desc: "Spot missing keywords and formatting errors." },
  { num: 4, title: "Enhance", desc: "Smart rewrite for maximum role impact." },
  { num: 5, title: "Build", desc: "Export in recruiter-approved templates." },
];

export function FeaturesSection() {
  return (
    <>
      <section id="how-it-works" className="py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-foreground sm:text-4xl">
              Your Path to Career Success
            </h2>
            <p className="mt-4 text-muted-foreground">
              From a static document to a dynamic career asset in five simple, automated steps.
            </p>
          </div>
          <div className="mt-16 flex flex-col items-center justify-between gap-8 md:flex-row">
            {steps.map((step, i) => (
              <motion.div
                key={step.num}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="relative flex flex-1 flex-col items-center text-center"
              >
                {i < steps.length - 1 && (
                  <div className="absolute left-[60%] top-6 hidden h-0.5 w-full bg-primary/20 md:block" />
                )}
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-lg font-bold text-primary">
                  {step.num}
                </div>
                <h3 className="mt-4 font-semibold">{step.title}</h3>
                <p className="mt-1 text-sm text-muted-foreground">{step.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <section id="features" className="bg-muted/30 py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-foreground sm:text-4xl">
              Master Your Career Dashboard
            </h2>
            <p className="mt-4 text-muted-foreground">
              Powerful features designed to put you ahead of the competition.
            </p>
          </div>
          <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {features.map((feature, i) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.05 }}
              >
                <Card className="h-full border-0 shadow-md transition-shadow hover:shadow-lg">
                  <CardContent className="p-6">
                    <div className={`mb-4 inline-flex rounded-xl p-3 ${feature.color}`}>
                      <feature.icon className="h-6 w-6" />
                    </div>
                    <h3 className="font-semibold text-foreground">{feature.title}</h3>
                    <p className="mt-2 text-sm text-muted-foreground leading-relaxed">
                      {feature.description}
                    </p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}
