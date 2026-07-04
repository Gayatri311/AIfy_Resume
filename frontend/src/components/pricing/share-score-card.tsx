"use client";

import { useState } from "react";
import { Share2, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";

interface ShareScoreCardProps {
  score: number;
  band: string;
  name?: string;
}

export function ShareScoreCard({ score, band, name }: ShareScoreCardProps) {
  const [copied, setCopied] = useState(false);

  const shareText = `My resume AI Readiness Score is ${score}/100 (${band}) — check yours at Alfy Resume`;

  const handleShare = async () => {
    const url = typeof window !== "undefined" ? window.location.origin : "";
    const text = `${shareText}\n${url}/upload`;

    if (navigator.share) {
      try {
        await navigator.share({ title: "My AI Readiness Score", text, url: `${url}/upload` });
        return;
      } catch {
        /* user cancelled */
      }
    }

    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  return (
    <Card className="border-primary/20 bg-gradient-to-br from-primary/5 to-violet-500/5">
      <CardContent className="p-6">
        <div className="flex flex-col items-center text-center sm:flex-row sm:text-left sm:items-center sm:justify-between gap-4">
          <div>
            <Badge className="mb-2">Share your progress</Badge>
            <p className="font-semibold">
              {name ? `${name.split(" ")[0]}'s` : "Your"} AI Readiness: {score}/100
            </p>
            <p className="mt-1 text-sm text-muted-foreground">
              Post your score on LinkedIn — job seekers love before/after transformations.
            </p>
          </div>
          <div className="flex h-20 w-20 shrink-0 items-center justify-center rounded-full border-4 border-primary bg-background">
            <span className="text-2xl font-bold text-primary">{score}</span>
          </div>
        </div>
        <Button className="mt-4 w-full sm:w-auto" onClick={handleShare}>
          {copied ? (
            <>
              <Check className="h-4 w-4" /> Copied!
            </>
          ) : (
            <>
              <Share2 className="h-4 w-4" /> Share score
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  );
}
