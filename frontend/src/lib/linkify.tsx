import type { ReactNode } from "react";

const URL_REGEX =
  /(?:https?:\/\/|www\.)[^\s)\]>\"']+|(?:linkedin\.com\/(?:in|company)\/[\w\-/]+|github\.com\/[\w\-/]+|[\w.\-+]+@[\w.\-]+\.\w+)/gi;

function isUrl(part: string): boolean {
  return /^(?:https?:\/\/|www\.)/i.test(part) ||
    /^(?:linkedin\.com|github\.com)/i.test(part) ||
    /^[\w.\-+]+@[\w.\-]+\.\w+$/.test(part);
}

function hrefFor(part: string): string {
  if (/^[\w.\-+]+@[\w.\-]+\.\w+$/.test(part)) {
    return `mailto:${part}`;
  }
  return part.startsWith("http") ? part : `https://${part}`;
}

export function linkifyText(text: string): ReactNode[] {
  const parts = text.split(URL_REGEX);
  return parts.map((part, i) => {
    if (part && isUrl(part)) {
      const href = hrefFor(part);
      return (
        <a
          key={i}
          href={href}
          style={{ color: "inherit", textDecoration: "underline" }}
          target="_blank"
          rel="noopener noreferrer"
        >
          {part}
        </a>
      );
    }
    return part ? <span key={i}>{part}</span> : null;
  });
}

export function contactItems(personal: {
  location?: string;
  email?: string;
  phone?: string;
  linkedin?: string;
  website?: string;
  github?: string;
}): string[] {
  return [
    personal.location,
    personal.email,
    personal.phone,
    personal.linkedin,
    personal.github,
    personal.website,
  ].filter(Boolean) as string[];
}
