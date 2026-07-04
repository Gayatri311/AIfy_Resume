"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { cn } from "@/lib/utils";

export function FitToPane({
  children,
  className,
  align = "top",
}: {
  children: React.ReactNode;
  className?: string;
  align?: "top" | "center";
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);
  const [scale, setScale] = useState(1);

  const measure = useCallback(() => {
    const container = containerRef.current;
    const content = contentRef.current;
    if (!container || !content) return;

    const naturalHeight = content.scrollHeight || content.offsetHeight;
    const naturalWidth = content.scrollWidth || content.offsetWidth;
    if (!naturalHeight || !naturalWidth) return;

    const pad = 8;
    const availableH = container.clientHeight - pad;
    const availableW = container.clientWidth - pad;
    const next = Math.min(availableW / naturalWidth, availableH / naturalHeight, 1);
    setScale(Number.isFinite(next) && next > 0 ? next : 1);
  }, []);

  useEffect(() => {
    measure();
    const container = containerRef.current;
    const content = contentRef.current;
    if (!container || !content) return;

    const observer = new ResizeObserver(measure);
    observer.observe(container);
    observer.observe(content);
    return () => observer.disconnect();
  }, [children, measure]);

  return (
    <div
      ref={containerRef}
      className={cn("h-full w-full overflow-hidden", className)}
    >
      <div
        className={cn(
          "flex h-full w-full",
          align === "center" ? "items-center justify-center" : "items-start justify-center"
        )}
      >
        <div
          ref={contentRef}
          style={{
            transform: scale < 1 ? `scale(${scale})` : undefined,
            transformOrigin: align === "center" ? "center center" : "top center",
          }}
        >
          {children}
        </div>
      </div>
    </div>
  );
}
