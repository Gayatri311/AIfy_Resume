import { LETTER_HEIGHT, LETTER_WIDTH } from "@/lib/resume-page-styles";

const PAGE_WIDTH_PX = LETTER_WIDTH;
const PAGE_HEIGHT_PX = LETTER_HEIGHT;
/** 96 CSS px per inch — matches browser letter layout (816px = 8.5in). */
const CSS_PX_PER_INCH = 96;
const LETTER_WIDTH_IN = PAGE_WIDTH_PX / CSS_PX_PER_INCH;
const LETTER_HEIGHT_IN = PAGE_HEIGHT_PX / CSS_PX_PER_INCH;

function captureScale(): number {
  if (typeof window === "undefined") return 4;
  return Math.max(4, Math.min(5, Math.round(window.devicePixelRatio * 2)));
}

const COLOR_PROPS = [
  "color",
  "background-color",
  "border-top-color",
  "border-right-color",
  "border-bottom-color",
  "border-left-color",
  "outline-color",
  "text-decoration-color",
  "fill",
  "stroke",
] as const;

function normalizeModernColors(root: HTMLElement, view: Window = window): void {
  const canvas = root.ownerDocument.createElement("canvas");
  const ctx = canvas.getContext("2d");
  if (!ctx) return;

  const toSafeColor = (color: string): string | null => {
    if (!color || color === "transparent" || color === "rgba(0, 0, 0, 0)") return color;
    try {
      ctx.fillStyle = "#000000";
      ctx.fillStyle = color;
      return ctx.fillStyle;
    } catch {
      return null;
    }
  };

  const nodes = [root, ...Array.from(root.querySelectorAll("*"))];
  for (const node of nodes) {
    if (!(node instanceof HTMLElement)) continue;
    const computed = view.getComputedStyle(node);
    for (const prop of COLOR_PROPS) {
      const value = computed.getPropertyValue(prop);
      if (!value || value === "transparent" || value === "rgba(0, 0, 0, 0)") continue;
      const safe = toSafeColor(value);
      if (safe) node.style.setProperty(prop, safe);
    }
    if (computed.boxShadow && computed.boxShadow !== "none") {
      node.style.boxShadow = "none";
    }
  }
}

function lockResumeWidth(root: HTMLElement): void {
  root.style.width = `${PAGE_WIDTH_PX}px`;
  root.style.minWidth = `${PAGE_WIDTH_PX}px`;
  root.style.maxWidth = `${PAGE_WIDTH_PX}px`;
  root.style.boxSizing = "border-box";
}

async function waitForLayout(): Promise<void> {
  await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  if (document.fonts?.ready) {
    await document.fonts.ready;
  }
}

/** Off-screen clone at letter width — same layout as preview, no scaling. */
function buildExportStage(source: HTMLElement): {
  page: HTMLElement;
  cleanup: () => void;
} {
  const clone = source.cloneNode(true) as HTMLElement;
  clone.style.margin = "0";
  clone.style.boxShadow = "none";
  clone.style.background = "#ffffff";
  lockResumeWidth(clone);

  const stage = document.createElement("div");
  stage.setAttribute("aria-hidden", "true");
  stage.style.cssText = [
    "position:fixed",
    "left:-12000px",
    "top:0",
    `width:${PAGE_WIDTH_PX}px`,
    "overflow:visible",
    "background:#ffffff",
  ].join(";");

  stage.appendChild(clone);
  document.body.appendChild(stage);

  return {
    page: clone,
    cleanup: () => {
      document.body.removeChild(stage);
    },
  };
}

async function captureResumePage(source: HTMLElement): Promise<{
  canvas: HTMLCanvasElement;
  scale: number;
}> {
  const html2canvas = (await import("html2canvas-pro")).default;
  const { page, cleanup } = buildExportStage(source);
  const scale = captureScale();

  try {
    await waitForLayout();
    normalizeModernColors(page);

    const canvas = await html2canvas(page, {
      scale,
      useCORS: true,
      allowTaint: true,
      backgroundColor: "#ffffff",
      logging: false,
      scrollX: 0,
      scrollY: 0,
      onclone: (clonedDoc, clonedElement) => {
        const view = clonedDoc.defaultView;
        if (!view || !(clonedElement instanceof HTMLElement)) return;
        normalizeModernColors(clonedElement, view);
        lockResumeWidth(clonedElement);
      },
    });

    return { canvas, scale };
  } finally {
    cleanup();
  }
}

async function canvasToPdf(
  canvas: HTMLCanvasElement,
  captureScaleValue: number,
  filename: string
): Promise<void> {
  const { jsPDF } = await import("jspdf");

  const cssHeight = canvas.height / captureScaleValue;
  const pageCount = Math.max(1, Math.ceil(cssHeight / PAGE_HEIGHT_PX));

  const pdf = new jsPDF({
    orientation: "portrait",
    unit: "in",
    format: "letter",
    compress: false,
  });

  for (let pageIndex = 0; pageIndex < pageCount; pageIndex++) {
    if (pageIndex > 0) {
      pdf.addPage("letter", "portrait");
    }

    const sliceTopCss = pageIndex * PAGE_HEIGHT_PX;
    const sliceHeightCss = Math.min(PAGE_HEIGHT_PX, cssHeight - sliceTopCss);
    const sliceHeightIn = sliceHeightCss / CSS_PX_PER_INCH;

    const sliceCanvas = document.createElement("canvas");
    sliceCanvas.width = canvas.width;
    sliceCanvas.height = Math.max(1, Math.round(sliceHeightCss * captureScaleValue));

    const ctx = sliceCanvas.getContext("2d");
    if (!ctx) throw new Error("Canvas context unavailable");

    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, sliceCanvas.width, sliceCanvas.height);
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = "high";
    ctx.drawImage(
      canvas,
      0,
      Math.round(sliceTopCss * captureScaleValue),
      canvas.width,
      sliceCanvas.height,
      0,
      0,
      sliceCanvas.width,
      sliceCanvas.height
    );

    const imgData = sliceCanvas.toDataURL("image/png");
    if (!imgData || imgData === "data:," || imgData.length < 100) {
      throw new Error("Failed to capture resume image");
    }

    pdf.addImage(
      imgData,
      "PNG",
      0,
      0,
      LETTER_WIDTH_IN,
      sliceHeightIn,
      undefined,
      "NONE"
    );
  }

  pdf.save(filename.endsWith(".pdf") ? filename : `${filename}.pdf`);
}

export async function downloadResumePdf(
  element: HTMLElement,
  filename: string,
  _options?: { watermark?: boolean }
): Promise<void> {
  const { canvas, scale } = await captureResumePage(element);
  await canvasToPdf(canvas, scale, filename);
}

export function getFormatStorageKey(resumeId: string): string {
  return `alfy-resume-format-${resumeId}`;
}

export function loadSavedFormat(resumeId: string): import("@/lib/resume-utils").ResumeFormat {
  if (typeof window === "undefined") return "classic";
  const saved = localStorage.getItem(getFormatStorageKey(resumeId));
  if (saved === "modern" || saved === "minimal" || saved === "classic") return saved;
  return "classic";
}

export function saveFormat(
  resumeId: string,
  format: import("@/lib/resume-utils").ResumeFormat
): void {
  localStorage.setItem(getFormatStorageKey(resumeId), format);
}
