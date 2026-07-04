"use client";

import { useEffect, useState } from "react";
import { Download, FileText, Loader2 } from "lucide-react";
import { Document, Page, pdfjs } from "react-pdf";
import { Button } from "@/components/ui/button";
import { getOriginalResumeFileUrl } from "@/lib/api";
import "react-pdf/dist/Page/AnnotationLayer.css";
import "react-pdf/dist/Page/TextLayer.css";

pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  "pdfjs-dist/build/pdf.worker.min.mjs",
  import.meta.url
).toString();

interface OriginalDocumentViewerProps {
  resumeId: string;
  filename?: string;
  fileType?: "pdf" | "docx";
}

export function OriginalDocumentViewer({
  resumeId,
  filename,
  fileType = "pdf",
}: OriginalDocumentViewerProps) {
  const fileUrl = getOriginalResumeFileUrl(resumeId);
  const isPdf = fileType === "pdf" || (filename || "").toLowerCase().endsWith(".pdf");
  const [numPages, setNumPages] = useState(0);
  const [pageWidth, setPageWidth] = useState(640);
  const [loadError, setLoadError] = useState(false);

  useEffect(() => {
    const updateWidth = () => {
      const columnWidth = Math.min(window.innerWidth * 0.46, 720);
      setPageWidth(Math.max(columnWidth, 320));
    };
    updateWidth();
    window.addEventListener("resize", updateWidth);
    return () => window.removeEventListener("resize", updateWidth);
  }, []);

  if (!isPdf) {
    return (
      <div className="flex min-h-[320px] flex-col items-center justify-center gap-4 p-8 text-center">
        <FileText className="h-12 w-12 text-muted-foreground" />
        <div>
          <p className="font-medium">Word document uploaded</p>
          <p className="mt-1 text-sm text-muted-foreground">
            DOCX files can&apos;t be previewed in the browser. Download to view the original.
          </p>
        </div>
        <Button variant="secondary" size="sm" asChild>
          <a href={fileUrl} download={filename || "resume.docx"}>
            <Download className="h-4 w-4" />
            Download original
          </a>
        </Button>
      </div>
    );
  }

  if (loadError) {
    return (
      <div className="flex min-h-[320px] flex-col items-center justify-center gap-4 p-8 text-center">
        <FileText className="h-12 w-12 text-muted-foreground" />
        <p className="text-sm text-muted-foreground">Could not preview PDF inline.</p>
        <Button variant="secondary" size="sm" asChild>
          <a href={fileUrl} target="_blank" rel="noopener noreferrer">
            Open original PDF
          </a>
        </Button>
      </div>
    );
  }

  return (
    <div className="bg-[#525659] px-3 py-6 sm:px-4">
      <Document
        file={fileUrl}
        onLoadSuccess={({ numPages: pages }) => setNumPages(pages)}
        onLoadError={() => setLoadError(true)}
        loading={
          <div className="flex min-h-[400px] items-center justify-center">
            <Loader2 className="h-8 w-8 animate-spin text-white/70" />
          </div>
        }
      >
        {Array.from({ length: numPages }, (_, index) => (
          <div key={`page-${index + 1}`} className="mb-4 flex justify-center last:mb-0">
            <Page
              pageNumber={index + 1}
              width={pageWidth}
              renderTextLayer={false}
              renderAnnotationLayer={false}
              className="shadow-lg"
            />
          </div>
        ))}
      </Document>
    </div>
  );
}
