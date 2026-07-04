"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  LETTER_WIDTH,
  LETTER_HEIGHT,
  computeOnePageScale,
  SMALL_TEXT_SCALE_THRESHOLD,
} from "@/lib/resume-page-styles";

export const RESUME_LETTER_VIEWPORT_ID = "resume-letter-viewport";

const PAGE_SELECTOR = ".resume-export-page, .resume-page";

/** Scales content to fit a letter page — used for PDF export staging, not on-screen preview. */
export function OnePageResumeFrame({
  children,
  showScaleNote = true,
}: {
  children: React.ReactNode;
  showScaleNote?: boolean;
}) {
  const contentRef = useRef<HTMLDivElement>(null);
  const [scale, setScale] = useState(1);

  const measure = useCallback(() => {
    const page = contentRef.current?.querySelector(PAGE_SELECTOR) as HTMLElement | null;
    if (!page) return;
    const height = page.scrollHeight || page.offsetHeight;
    setScale(computeOnePageScale(height));
  }, []);

  useEffect(() => {
    measure();
    const page = contentRef.current?.querySelector(PAGE_SELECTOR);
    if (!page) return;

    const observer = new ResizeObserver(measure);
    observer.observe(page);
    return () => observer.disconnect();
  }, [children, measure]);

  const isScaled = scale < 1;

  return (
    <div className="flex flex-col items-center">
      {showScaleNote && isScaled && (
        <p className="mb-2 max-w-md text-center text-xs text-muted-foreground">
          Scaled to fit one letter page for export.
          {scale < SMALL_TEXT_SCALE_THRESHOLD && (
            <> Consider trimming the longest bullets for larger text in the PDF.</>
          )}
        </p>
      )}
      <div
        id={RESUME_LETTER_VIEWPORT_ID}
        data-resume-export-target
        className="relative bg-white shadow-sm"
        style={{
          width: LETTER_WIDTH,
          height: LETTER_HEIGHT,
          overflow: "hidden",
        }}
      >
        <div
          ref={contentRef}
          style={{
            transform: isScaled ? `scale(${scale})` : undefined,
            transformOrigin: "top left",
            width: LETTER_WIDTH,
          }}
        >
          {children}
        </div>
      </div>
    </div>
  );
}

export function measureOnePageScale(pageElement: HTMLElement): number {
  const naturalHeight = pageElement.scrollHeight || pageElement.offsetHeight;
  return computeOnePageScale(naturalHeight);
}

export { LETTER_WIDTH, LETTER_HEIGHT };
