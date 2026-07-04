"use client";

const BULLET_PREFIX = /^[\u2022\-\*•●▪◦]\s*/;

function stripBullet(line: string): string {
  return line.replace(BULLET_PREFIX, "").trim();
}

function isBulletLine(line: string): boolean {
  return BULLET_PREFIX.test(line.trim());
}

function parseBlocks(text: string): string[][] {
  return text
    .split(/\n\s*\n/)
    .map((block) => block.split("\n").map((l) => l.trim()).filter(Boolean))
    .filter((lines) => lines.length > 0);
}

function ExperienceBlock({ lines }: { lines: string[] }) {
  const headerLines: string[] = [];
  const bullets: string[] = [];

  for (const line of lines) {
    if (isBulletLine(line)) {
      bullets.push(stripBullet(line));
    } else if (bullets.length === 0) {
      headerLines.push(line);
    } else {
      bullets.push(stripBullet(line));
    }
  }

  return (
    <div className="space-y-2">
      {headerLines.map((line, i) => (
        <p key={`h-${i}`} className={i === 0 ? "font-medium text-foreground" : "text-sm text-muted-foreground"}>
          {line}
        </p>
      ))}
      {bullets.length > 0 && (
        <ul className="list-disc space-y-1.5 pl-5">
          {bullets.map((bullet, i) => (
            <li key={`b-${i}`} className="text-sm leading-relaxed">
              {bullet}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function ProjectBlock({ lines }: { lines: string[] }) {
  const [title, ...rest] = lines;
  const bullets: string[] = [];
  const other: string[] = [];

  for (const line of rest) {
    if (isBulletLine(line)) {
      bullets.push(stripBullet(line));
    } else if (line.toLowerCase().startsWith("tech:")) {
      other.push(line);
    } else {
      other.push(line);
    }
  }

  return (
    <div className="space-y-2">
      <p className="font-medium">{title}</p>
      {other.map((line, i) => (
        <p key={`o-${i}`} className="text-sm leading-relaxed">
          {line}
        </p>
      ))}
      {bullets.length > 0 && (
        <ul className="list-disc space-y-1.5 pl-5">
          {bullets.map((bullet, i) => (
            <li key={`b-${i}`} className="text-sm leading-relaxed">
              {bullet}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export function SectionTextView({
  text,
  section,
  muted = false,
}: {
  text: string;
  section: string;
  muted?: boolean;
}) {
  const className = muted ? "text-muted-foreground" : "";

  if (section === "experience") {
    const blocks = parseBlocks(text);
    return (
      <div className={`space-y-5 font-sans ${className}`}>
        {blocks.map((lines, i) => (
          <ExperienceBlock key={i} lines={lines} />
        ))}
      </div>
    );
  }

  if (section === "projects") {
    const blocks = parseBlocks(text);
    return (
      <div className={`space-y-5 font-sans ${className}`}>
        {blocks.map((lines, i) => (
          <ProjectBlock key={i} lines={lines} />
        ))}
      </div>
    );
  }

  if (section === "skills") {
    const skills = text.split(/[,•|]/).map((s) => s.trim()).filter(Boolean);
    return (
      <ul className={`flex flex-wrap gap-2 font-sans ${className}`}>
        {skills.map((skill) => (
          <li key={skill} className="rounded-md bg-muted px-2 py-1 text-sm">
            {skill}
          </li>
        ))}
      </ul>
    );
  }

  if (section === "education") {
    const lines = text.split("\n").map((l) => l.trim()).filter(Boolean);
    return (
      <ul className={`list-disc space-y-1 pl-5 font-sans ${className}`}>
        {lines.map((line, i) => (
          <li key={i} className="text-sm leading-relaxed">
            {line}
          </li>
        ))}
      </ul>
    );
  }

  return (
    <p className={`whitespace-pre-wrap font-sans text-sm leading-relaxed ${className}`}>
      {text}
    </p>
  );
}
