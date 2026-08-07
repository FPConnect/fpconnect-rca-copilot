type CsvValue = string | number | boolean | null | undefined;

export type CsvRow = Record<string, CsvValue>;

function escapeCsvValue(value: CsvValue): string {
  if (value === null || value === undefined) {
    return "";
  }

  const normalized = String(value).replace(/\r?\n/g, " ").trim();
  if (/[",;]/.test(normalized)) {
    return `"${normalized.replace(/"/g, '""')}"`;
  }
  return normalized;
}

function buildCsv(rows: CsvRow[]): string {
  if (rows.length === 0) {
    return "";
  }

  const headers = Array.from(
    rows.reduce((set, row) => {
      Object.keys(row).forEach((key) => set.add(key));
      return set;
    }, new Set<string>()),
  );

  const lines = [
    headers.join(";"),
    ...rows.map((row) => headers.map((header) => escapeCsvValue(row[header])).join(";")),
  ];

  return lines.join("\r\n");
}

function triggerDownload(filename: string, content: string, mimeType: string): void {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

export function downloadCsv(filename: string, rows: CsvRow[]): void {
  triggerDownload(filename, `\uFEFF${buildCsv(rows)}`, "text/csv;charset=utf-8");
}

export function downloadMultiSectionCsv(
  filename: string,
  sections: Array<{ title: string; rows: CsvRow[] }>,
): void {
  const sectionContent = sections
    .filter((section) => section.rows.length > 0)
    .map((section) => [`# ${section.title}`, buildCsv(section.rows)].filter(Boolean).join("\r\n"))
    .join("\r\n\r\n");

  triggerDownload(filename, `\uFEFF${sectionContent}`, "text/csv;charset=utf-8");
}
