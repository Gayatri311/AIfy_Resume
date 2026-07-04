"use client";

import { linkifyText } from "@/lib/linkify";
import { splitWithHighlights } from "@/lib/keyword-highlight";

/** Bold ATS keywords in resume text — no color, professional emphasis only. */
export function HighlightedText({
  text,
  keywords,
}: {
  text: string;
  keywords: string[];
}) {
  if (!text) return null;
  if (!keywords.length) return <>{linkifyText(text)}</>;

  const segments = splitWithHighlights(text, keywords);
  return (
    <>
      {segments.map((seg, i) =>
        seg.bold ? (
          <strong key={i} className="font-semibold text-gray-900">
            {seg.text}
          </strong>
        ) : (
          <span key={i}>{linkifyText(seg.text)}</span>
        )
      )}
    </>
  );
}
