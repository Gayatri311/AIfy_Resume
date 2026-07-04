"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { getResumeAnalysis } from "@/lib/api";
import { ProcessingScreen, STEPS } from "@/components/processing/processing-screen";

export default function ProcessingPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [completedSteps, setCompletedSteps] = useState(0);
  const [insightIndex, setInsightIndex] = useState(0);
  const [status, setStatus] = useState<"processing" | "completed" | "failed">("processing");
  const [serverDone, setServerDone] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [slowMessage, setSlowMessage] = useState(false);
  const [serverStepLabel, setServerStepLabel] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;

    const poll = async () => {
      try {
        const data = await getResumeAnalysis(id);
        if (data.status === "completed") {
          setServerDone(true);
          return true;
        }
        if (data.status === "failed") {
          setStatus("failed");
          setErrorMessage(
            data.current_step ||
              "Uploaded document does not appear to be a resume. Please try again by uploading your resume."
          );
          return true;
        }
        if (data.current_step && data.current_step !== "Complete") {
          setServerStepLabel(data.current_step);
          const idx = STEPS.findIndex((s) => s === data.current_step);
          if (idx >= 0) {
            setCompletedSteps((s) => Math.max(s, idx));
          }
        }
        if (data.progress > 0) {
          const step = Math.min(
            Math.floor((data.progress / 100) * STEPS.length),
            STEPS.length - 1
          );
          setCompletedSteps((s) => Math.max(s, step));
        }
        return false;
      } catch {
        return false;
      }
    };

    poll();

    const pollTimer = setInterval(async () => {
      const done = await poll();
      if (done) {
        clearInterval(pollTimer);
      }
    }, 2000);

    const slowTimer = setTimeout(() => setSlowMessage(true), 30000);
    const verySlowTimer = setTimeout(() => {
      setSlowMessage(true);
      setServerStepLabel((label) => label || "Still processing — if this takes more than 2 minutes, restart the backend and try again.");
    }, 120000);

    return () => {
      clearInterval(pollTimer);
      clearTimeout(slowTimer);
      clearTimeout(verySlowTimer);
    };
  }, [id]);

  // Gentle checklist animation while waiting — never ahead of server-reported progress.
  useEffect(() => {
    if (status !== "processing" || serverDone) return;
    const stepTimer = setInterval(() => {
      setCompletedSteps((s) => Math.min(s + 1, STEPS.length - 2));
    }, 3500);
    return () => clearInterval(stepTimer);
  }, [serverDone, status]);

  // Navigate as soon as the backend finishes — don't wait for checklist animation.
  useEffect(() => {
    if (!serverDone || !id) return;
    setCompletedSteps(STEPS.length);
    setStatus("completed");
    const t = setTimeout(() => router.push(`/review/${id}`), 500);
    return () => clearTimeout(t);
  }, [serverDone, router, id]);

  useEffect(() => {
    const insightTimer = setInterval(() => setInsightIndex((i) => i + 1), 4000);
    return () => clearInterval(insightTimer);
  }, []);

  return (
    <ProcessingScreen
      completedSteps={Math.min(completedSteps, STEPS.length)}
      status={status}
      insightIndex={insightIndex}
      errorMessage={errorMessage}
      slowMessage={slowMessage}
      activeStepLabel={serverStepLabel ?? undefined}
    />
  );
}
