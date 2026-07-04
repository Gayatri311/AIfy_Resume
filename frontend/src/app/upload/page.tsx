"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Upload, FileText, Link2, AlertCircle } from "lucide-react";
import { Navbar } from "@/components/layout/navbar";
import { Footer } from "@/components/layout/footer";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { uploadResume } from "@/lib/api";
import { cn } from "@/lib/utils";
import { ProcessingScreen, STEPS } from "@/components/processing/processing-screen";

const MAX_SIZE_MB = 10;
const ACCEPTED_TYPES = [
  "application/pdf",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
];

export default function UploadPage() {
  const router = useRouter();
  const [dragging, setDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [completedSteps, setCompletedSteps] = useState(0);
  const [insightIndex, setInsightIndex] = useState(0);

  useEffect(() => {
    if (!uploading) return;
    const insightTimer = setInterval(() => setInsightIndex((i) => i + 1), 4000);
    const stepTimer = setInterval(() => {
      setCompletedSteps((s) => Math.min(s + 1, STEPS.length - 1));
    }, 2000);
    return () => {
      clearInterval(insightTimer);
      clearInterval(stepTimer);
    };
  }, [uploading]);

  const validateFile = (f: File): string | null => {
    if (f.size > MAX_SIZE_MB * 1024 * 1024) {
      return `File exceeds ${MAX_SIZE_MB}MB limit`;
    }
    const ext = f.name.split(".").pop()?.toLowerCase();
    if (!["pdf", "docx"].includes(ext || "")) {
      return "Only PDF and DOCX files are supported";
    }
    return null;
  };

  const handleFile = useCallback((f: File) => {
    const err = validateFile(f);
    if (err) {
      setError(err);
      setFile(null);
      return;
    }
    setError(null);
    setFile(f);
  }, []);

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragging(false);
      const dropped = e.dataTransfer.files[0];
      if (dropped) handleFile(dropped);
    },
    [handleFile]
  );

  const handleUpload = async () => {
    if (!file) return;
    setCompletedSteps(0);
    setInsightIndex(0);
    setUploading(true);
    setError(null);
    try {
      const { id } = await uploadResume(file);
      router.push(`/processing/${id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Upload failed. Please try again.");
      setUploading(false);
    }
  };

  if (uploading) {
    return (
      <ProcessingScreen
        completedSteps={completedSteps}
        status="processing"
        insightIndex={insightIndex}
      />
    );
  }

  return (
    <div className="flex min-h-screen flex-col">
      <Navbar showCta={false} />
      <main className="flex flex-1 items-center justify-center px-4 py-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-2xl"
        >
          <div className="mb-8 text-center">
            <h1 className="text-3xl font-bold">Upload Your Resume</h1>
            <p className="mt-2 text-muted-foreground">
              PDF, DOCX, or LinkedIn Profile PDF — max {MAX_SIZE_MB}MB
            </p>
          </div>

          <Card
            className={cn(
              "border-2 border-dashed transition-colors",
              dragging ? "border-primary bg-primary/5" : "border-border",
              file && "border-primary/50"
            )}
            onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={onDrop}
          >
            <CardContent className="flex flex-col items-center p-12">
              <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10">
                <Upload className="h-8 w-8 text-primary" />
              </div>
              <p className="mb-2 text-lg font-medium">
                Drag and drop your resume here
              </p>
              <p className="mb-6 text-sm text-muted-foreground">or click to browse</p>
              <input
                type="file"
                accept=".pdf,.docx"
                className="hidden"
                id="file-upload"
                onChange={(e) => {
                  const f = e.target.files?.[0];
                  if (f) handleFile(f);
                }}
              />
              <Button variant="secondary" asChild>
                <label htmlFor="file-upload" className="cursor-pointer">
                  Choose File
                </label>
              </Button>

              {file && (
                <div className="mt-6 flex items-center gap-3 rounded-lg bg-muted px-4 py-3">
                  <FileText className="h-5 w-5 text-primary" />
                  <span className="text-sm font-medium">{file.name}</span>
                  <span className="text-xs text-muted-foreground">
                    ({(file.size / 1024 / 1024).toFixed(2)} MB)
                  </span>
                </div>
              )}

              {error && (
                <div className="mt-4 flex items-center gap-2 text-sm text-destructive">
                  <AlertCircle className="h-4 w-4" />
                  {error}
                </div>
              )}
            </CardContent>
          </Card>

          <div className="mt-6 grid grid-cols-3 gap-4">
            {[
              { icon: FileText, label: "PDF" },
              { icon: FileText, label: "DOCX" },
              { icon: Link2, label: "LinkedIn PDF" },
            ].map(({ icon: Icon, label }) => (
              <div
                key={label}
                className="flex flex-col items-center rounded-xl border border-border bg-card p-4 text-center"
              >
                <Icon className="mb-2 h-6 w-6 text-muted-foreground" />
                <span className="text-xs font-medium text-muted-foreground">{label}</span>
              </div>
            ))}
          </div>

          <Button
            className="mt-8 w-full"
            size="lg"
            disabled={!file || uploading}
            onClick={handleUpload}
          >
            {uploading ? "Uploading..." : "Start AI Analysis"}
          </Button>
        </motion.div>
      </main>
      <Footer />
    </div>
  );
}
