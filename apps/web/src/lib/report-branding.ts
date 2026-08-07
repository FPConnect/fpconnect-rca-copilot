import jsPDF from "jspdf";

const REPORT_LOGO_ASSET = "/branding/fpconnect-report-logo.svg";
const PAGE_MARGIN = 14;
const HEADER_Y = 10;
const HEADER_HEIGHT = 18;
const TITLE_Y = 39;
const SUBTITLE_Y = 46;
const CONTENT_START_Y = 56;
const FOOTER_HEIGHT = 12;

let reportLogoPromise: Promise<string | null> | null = null;

type ReportBrandingOptions = {
  title: string;
  subtitle?: string;
  rightLabel?: string;
  pageNumber?: number;
  totalPages?: number;
};

async function loadReportLogoDataUrl(): Promise<string | null> {
  if (typeof window === "undefined") {
    return null;
  }

  try {
    const response = await fetch(REPORT_LOGO_ASSET);
    if (!response.ok) {
      return null;
    }

    const svgMarkup = await response.text();
    const svgBlob = new Blob([svgMarkup], { type: "image/svg+xml;charset=utf-8" });
    const objectUrl = URL.createObjectURL(svgBlob);

    try {
      const image = new Image();
      image.decoding = "async";
      image.src = objectUrl;
      await image.decode();

      const canvas = document.createElement("canvas");
      const targetWidth = 1200;
      const targetHeight = Math.max(
        320,
        Math.round((image.naturalHeight / image.naturalWidth) * targetWidth),
      );
      canvas.width = targetWidth;
      canvas.height = targetHeight;

      const context = canvas.getContext("2d");
      if (!context) {
        return null;
      }

      context.clearRect(0, 0, targetWidth, targetHeight);
      context.drawImage(image, 0, 0, targetWidth, targetHeight);
      return canvas.toDataURL("image/png");
    } finally {
      URL.revokeObjectURL(objectUrl);
    }
  } catch {
    return null;
  }
}

async function getReportLogoDataUrl(): Promise<string | null> {
  if (!reportLogoPromise) {
    reportLogoPromise = loadReportLogoDataUrl();
  }

  return reportLogoPromise;
}

function drawReportFooter(
  doc: jsPDF,
  pageNumber?: number,
  totalPages?: number,
): void {
  const pageHeight = doc.internal.pageSize.getHeight();
  const pageWidth = doc.internal.pageSize.getWidth();

  doc.setDrawColor(203, 213, 225);
  doc.line(PAGE_MARGIN, pageHeight - FOOTER_HEIGHT, pageWidth - PAGE_MARGIN, pageHeight - FOOTER_HEIGHT);

  doc.setFont("helvetica", "normal");
  doc.setFontSize(8.5);
  doc.setTextColor(71, 85, 105);
  doc.text("FPConnect | Relatorio corporativo", PAGE_MARGIN, pageHeight - 5.4);

  if (pageNumber && totalPages) {
    doc.text(
      `Pagina ${pageNumber} de ${totalPages}`,
      pageWidth - PAGE_MARGIN,
      pageHeight - 5.4,
      { align: "right" },
    );
  }
}

export async function addReportBranding(
  doc: jsPDF,
  options: ReportBrandingOptions,
): Promise<number> {
  const pageWidth = doc.internal.pageSize.getWidth();
  const logoDataUrl = await getReportLogoDataUrl();

  doc.setFillColor(7, 19, 44);
  doc.roundedRect(
    PAGE_MARGIN,
    HEADER_Y,
    pageWidth - PAGE_MARGIN * 2,
    HEADER_HEIGHT,
    4,
    4,
    "F",
  );

  if (logoDataUrl) {
    doc.addImage(logoDataUrl, "PNG", PAGE_MARGIN + 4, HEADER_Y + 2.8, 40, 12.2, undefined, "FAST");
  } else {
    doc.setFont("helvetica", "bold");
    doc.setFontSize(12);
    doc.setTextColor(248, 250, 252);
    doc.text("FPConnect", PAGE_MARGIN + 4, HEADER_Y + 11.8);
  }

  doc.setFont("helvetica", "normal");
  doc.setFontSize(8.5);
  doc.setTextColor(191, 219, 254);
  doc.text(
    options.rightLabel ?? "Relatorio FPConnect",
    pageWidth - PAGE_MARGIN - 4,
    HEADER_Y + 6.8,
    { align: "right" },
  );

  doc.setFontSize(7.5);
  doc.setTextColor(226, 232, 240);
  doc.text(
    `Gerado em ${new Date().toLocaleString("pt-BR")}`,
    pageWidth - PAGE_MARGIN - 4,
    HEADER_Y + 12.4,
    { align: "right" },
  );

  doc.setFont("helvetica", "bold");
  doc.setFontSize(18);
  doc.setTextColor(15, 23, 42);
  doc.text(options.title, PAGE_MARGIN, TITLE_Y);

  if (options.subtitle) {
    doc.setFont("helvetica", "normal");
    doc.setFontSize(9.5);
    doc.setTextColor(71, 85, 105);
    doc.text(options.subtitle, PAGE_MARGIN, SUBTITLE_Y);
  }

  doc.setDrawColor(191, 219, 254);
  doc.line(PAGE_MARGIN, CONTENT_START_Y - 4, pageWidth - PAGE_MARGIN, CONTENT_START_Y - 4);

  drawReportFooter(doc, options.pageNumber, options.totalPages);
  return CONTENT_START_Y;
}

export function getReportContentBox(doc: jsPDF): {
  x: number;
  y: number;
  width: number;
  height: number;
} {
  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();

  return {
    x: PAGE_MARGIN,
    y: CONTENT_START_Y,
    width: pageWidth - PAGE_MARGIN * 2,
    height: pageHeight - CONTENT_START_Y - FOOTER_HEIGHT - 4,
  };
}