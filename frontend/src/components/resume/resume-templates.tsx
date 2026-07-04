import type { ResumeData } from "@/types/resume";
import { contactItems, linkifyText } from "@/lib/linkify";
import { getExperienceBullets, getProjectBullets } from "@/lib/resume-format";
import { splitWithHighlights } from "@/lib/keyword-highlight";
import { ONE_PAGE } from "@/lib/resume-page-styles";

function HighlightedText({ text, keywords }: { text: string; keywords: string[] }) {
  const segments = splitWithHighlights(text, keywords);
  return (
    <>
      {segments.map((seg, i) =>
        seg.bold ? (
          <strong key={i} style={{ fontWeight: 700 }}>
            {seg.text}
          </strong>
        ) : (
          <span key={i}>{linkifyText(seg.text)}</span>
        )
      )}
    </>
  );
}

function BulletLines({
  items,
  style,
  keywords = [],
}: {
  items: string[];
  style?: React.CSSProperties;
  keywords?: string[];
}) {
  if (!items.length) return null;
  return (
    <div style={{ marginTop: "4px", ...style }}>
      {items.map((part, k) => (
        <div
          key={k}
          style={{
            display: "flex",
            alignItems: "flex-start",
            gap: "6px",
            ...ONE_PAGE.bullet,
            marginBottom: "2px",
          }}
        >
          <span style={{ flexShrink: 0, width: "12px", fontWeight: 700 }}>•</span>
          <span style={{ flex: 1 }}>
            <RichText text={part} keywords={keywords} />
          </span>
        </div>
      ))}
    </div>
  );
}

interface TemplateProps {
  data: ResumeData;
  highlightKeywords?: string[];
}

function ContactLine({ data }: { data: ResumeData["personal"] }) {
  const items = contactItems(data);
  if (!items.length) return null;
  return (
    <p style={{ ...ONE_PAGE.contact, color: "#64748b", margin: 0 }}>
      {items.map((item, i) => (
        <span key={i}>
          {i > 0 && "  ·  "}
          {linkifyText(item)}
        </span>
      ))}
    </p>
  );
}

function RichText({ text, keywords = [] }: { text: string; keywords?: string[] }) {
  return (
    <span style={{ whiteSpace: "pre-wrap" }}>
      {text.split("\n").map((line, i) => (
        <span key={i}>
          {i > 0 && <br />}
          <HighlightedText text={line} keywords={keywords} />
        </span>
      ))}
    </span>
  );
}

function SectionTitle({
  children,
  className,
  style,
}: {
  children: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
}) {
  return (
    <h2 className={className} style={style}>
      {children}
    </h2>
  );
}

export function ClassicTemplate({ data, highlightKeywords = [] }: TemplateProps) {
  const { personal, summary, experience, projects, skills, education } = data;
  const kw = highlightKeywords;
  const accent = "#6366f1";

  return (
    <div
      className="resume-page"
      style={{
        ...ONE_PAGE.page,
        fontFamily: "Georgia, 'Times New Roman', serif",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <h1 style={{ ...ONE_PAGE.name }}>
            {personal.name}
          </h1>
          <p
            style={{
              marginTop: "4px",
              ...ONE_PAGE.title,
              color: accent,
            }}
          >
            {personal.title}
          </p>
          <div style={{ marginTop: "6px" }}>
            <ContactLine data={personal} />
          </div>
        </div>
      </div>

      {summary && (
        <section style={{ marginTop: ONE_PAGE.sectionGap }}>
          <SectionTitle
            style={{
              ...ONE_PAGE.sectionTitle,
              color: accent,
            }}
          >
            Summary
          </SectionTitle>
          <p style={{ ...ONE_PAGE.body, margin: 0 }}>
            <RichText text={summary} keywords={kw} />
          </p>
        </section>
      )}

      {experience.length > 0 && (
        <section style={{ marginTop: ONE_PAGE.sectionGap }}>
          <SectionTitle
            style={{
              ...ONE_PAGE.sectionTitle,
              color: accent,
            }}
          >
            Professional Experience
          </SectionTitle>
          {experience.map((exp, i) => (
            <div key={i} style={{ marginBottom: "8px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
                <span style={{ fontSize: "11px", fontWeight: 700 }}>{exp.company}</span>
                <span style={{ fontSize: "9px", color: accent, fontWeight: 600 }}>
                  {exp.start_date} — {exp.end_date}
                </span>
              </div>
              <p style={{ fontSize: "10px", fontStyle: "italic", color: "#475569", margin: "1px 0 4px" }}>
                {exp.title}
              </p>
              <BulletLines items={getExperienceBullets(exp)} keywords={kw} />
            </div>
          ))}
        </section>
      )}

      {projects.length > 0 && (
        <section style={{ marginTop: ONE_PAGE.sectionGap }}>
          <SectionTitle
            style={{
              ...ONE_PAGE.sectionTitle,
              color: accent,
            }}
          >
            Projects
          </SectionTitle>
          {projects.map((proj, i) => (
            <div
              key={i}
              style={{
                marginBottom: "6px",
                padding: "6px 8px",
                borderLeft: `3px solid #34d399`,
                background: "#f0fdf4",
              }}
            >
              <p style={{ fontSize: "10px", fontWeight: 700, margin: 0 }}>{proj.title}</p>
              <BulletLines
                items={
                  getProjectBullets(proj.description).length
                    ? getProjectBullets(proj.description)
                    : proj.description
                    ? [proj.description]
                    : []
                }
                style={{ marginTop: "6px" }}
              />
              {proj.url && !proj.description.includes(proj.url) && (
                <p style={{ fontSize: "9px", margin: "2px 0 0", color: accent }}>
                  <RichText text={proj.url} />
                </p>
              )}
            </div>
          ))}
        </section>
      )}

      {skills.length > 0 && (
        <section style={{ marginTop: ONE_PAGE.sectionGap }}>
          <SectionTitle
            style={{
              ...ONE_PAGE.sectionTitle,
              color: accent,
            }}
          >
            Skills
          </SectionTitle>
          <p style={{ ...ONE_PAGE.body, margin: 0 }}>
            {skills.map((s, i) => (
              <span key={s}>
                {i > 0 && "  ·  "}
                <strong>{s}</strong>
              </span>
            ))}
          </p>
        </section>
      )}

      {education.length > 0 && (
        <section style={{ marginTop: ONE_PAGE.sectionGap }}>
          <SectionTitle
            style={{
              ...ONE_PAGE.sectionTitle,
              color: accent,
            }}
          >
            Education
          </SectionTitle>
          {education.map((edu, i) => (
            <p key={i} style={{ ...ONE_PAGE.body, margin: "0 0 2px" }}>
              <strong>{edu.degree}</strong>
              {edu.institution ? ` — ${edu.institution}` : ""}
              {edu.year ? `, ${edu.year}` : ""}
            </p>
          ))}
        </section>
      )}
    </div>
  );
}

export function ModernTemplate({ data, highlightKeywords = [] }: TemplateProps) {
  const { personal, summary, experience, projects, skills, education } = data;
  const kw = highlightKeywords;
  const navy = "#0f172a";
  const teal = "#0d9488";

  return (
    <div
      className="resume-page"
      style={{
        ...ONE_PAGE.page,
        padding: 0,
        fontFamily: "Helvetica, Arial, sans-serif",
      }}
    >
      <div style={{ background: navy, color: "#fff", padding: "16px 32px" }}>
        <h1 style={{ ...ONE_PAGE.name, fontSize: "22px" }}>{personal.name}</h1>
        <p
          style={{
            marginTop: "4px",
            fontSize: "10px",
            fontWeight: 500,
            color: "#5eead4",
            letterSpacing: "0.06em",
            textTransform: "uppercase",
          }}
        >
          {personal.title}
        </p>
        <p style={{ marginTop: "6px", ...ONE_PAGE.contact, color: "#cbd5e1" }}>
          {contactItems(personal).map((item, i) => (
            <span key={i}>
              {i > 0 && "  ·  "}
              {linkifyText(item)}
            </span>
          ))}
        </p>
      </div>

      <div style={{ padding: "14px 32px 20px" }}>
        {summary && (
          <section>
            <h2 style={{ ...ONE_PAGE.sectionTitle, color: teal }}>SUMMARY</h2>
            <p style={{ ...ONE_PAGE.body, margin: 0, color: "#334155" }}>
              <RichText text={summary} keywords={kw} />
            </p>
          </section>
        )}

        {experience.length > 0 && (
          <section style={{ marginTop: ONE_PAGE.sectionGap }}>
            <h2 style={{ ...ONE_PAGE.sectionTitle, color: teal }}>EXPERIENCE</h2>
            {experience.map((exp, i) => (
              <div key={i} style={{ marginBottom: "8px", borderLeft: `3px solid ${teal}`, paddingLeft: "10px" }}>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span style={{ fontSize: "11px", fontWeight: 700, color: navy }}>{exp.company}</span>
                  <span style={{ fontSize: "9px", color: "#64748b" }}>
                    {exp.start_date} – {exp.end_date}
                  </span>
                </div>
                <p style={{ fontSize: "10px", color: teal, margin: "1px 0 4px", fontWeight: 600 }}>{exp.title}</p>
                <BulletLines items={getExperienceBullets(exp)} keywords={kw} />
              </div>
            ))}
          </section>
        )}

        {projects.length > 0 && (
          <section style={{ marginTop: "24px" }}>
            <h2 style={{ fontSize: "11px", fontWeight: 700, color: teal, letterSpacing: "0.1em", marginBottom: "12px" }}>
              PROJECTS
            </h2>
            {projects.map((proj, i) => (
              <div key={i} style={{ marginBottom: "10px", background: "#f0fdfa", padding: "12px", borderRadius: "6px" }}>
                <p style={{ fontSize: "12px", fontWeight: 700, margin: 0, color: navy }}>{proj.title}</p>
                <BulletLines
                  items={
                    getProjectBullets(proj.description).length
                      ? getProjectBullets(proj.description)
                      : proj.description
                      ? [proj.description]
                      : []
                  }
                  style={{ marginTop: "6px" }}
                />
                {proj.url && (
                  <p style={{ fontSize: "11px", margin: "4px 0 0", color: teal }}>
                    <RichText text={proj.url} />
                  </p>
                )}
              </div>
            ))}
          </section>
        )}

        {skills.length > 0 && (
          <section style={{ marginTop: "24px" }}>
            <h2 style={{ fontSize: "11px", fontWeight: 700, color: teal, letterSpacing: "0.1em", marginBottom: "8px" }}>
              SKILLS
            </h2>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
              {skills.map((s) => (
                <span
                  key={s}
                  style={{
                    fontSize: "11px",
                    padding: "4px 10px",
                    background: "#f1f5f9",
                    borderRadius: "4px",
                    color: navy,
                  }}
                >
                  {s}
                </span>
              ))}
            </div>
          </section>
        )}

        {education.length > 0 && (
          <section style={{ marginTop: "24px" }}>
            <h2 style={{ fontSize: "11px", fontWeight: 700, color: teal, letterSpacing: "0.1em", marginBottom: "8px" }}>
              EDUCATION
            </h2>
            {education.map((edu, i) => (
              <p key={i} style={{ fontSize: "12px", margin: "0 0 4px", color: "#334155" }}>
                <strong>{edu.degree}</strong> — {edu.institution}{edu.year ? `, ${edu.year}` : ""}
              </p>
            ))}
          </section>
        )}
      </div>
    </div>
  );
}

export function MinimalTemplate({ data, highlightKeywords = [] }: TemplateProps) {
  const { personal, summary, experience, projects, skills, education } = data;
  const kw = highlightKeywords;

  return (
    <div
      className="resume-page"
      style={{
        ...ONE_PAGE.page,
        fontFamily: "'Times New Roman', Times, serif",
        color: "#000000",
      }}
    >
      <div style={{ textAlign: "center", borderBottom: "2px solid #000", paddingBottom: "10px" }}>
        <h1 style={{ ...ONE_PAGE.name, fontSize: "20px", letterSpacing: "0.02em" }}>
          {personal.name}
        </h1>
        <p style={{ fontSize: "10px", margin: "4px 0 0", fontStyle: "italic" }}>{personal.title}</p>
        <p style={{ ...ONE_PAGE.contact, margin: "6px 0 0", color: "#444" }}>
          {contactItems(personal).map((item, i) => (
            <span key={i}>
              {i > 0 && " | "}
              {linkifyText(item)}
            </span>
          ))}
        </p>
      </div>

      {summary && (
        <section style={{ marginTop: ONE_PAGE.sectionGap }}>
          <h2 style={{ ...ONE_PAGE.sectionTitle, textTransform: "uppercase" }}>Summary</h2>
          <p style={{ ...ONE_PAGE.body, margin: 0 }}>
            <RichText text={summary} keywords={kw} />
          </p>
        </section>
      )}

      {experience.length > 0 && (
        <section style={{ marginTop: "22px" }}>
          <h2 style={{ fontSize: "12px", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "10px" }}>
            Experience
          </h2>
          {experience.map((exp, i) => (
            <div key={i} style={{ marginBottom: "14px" }}>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ fontSize: "12px", fontWeight: 700 }}>{exp.company}</span>
                <span style={{ fontSize: "11px" }}>{exp.start_date} – {exp.end_date}</span>
              </div>
              <p style={{ fontSize: "12px", fontStyle: "italic", margin: "2px 0 6px" }}>{exp.title}</p>
              <BulletLines items={getExperienceBullets(exp)} keywords={kw} />
            </div>
          ))}
        </section>
      )}

      {projects.length > 0 && (
        <section style={{ marginTop: "22px" }}>
          <h2 style={{ fontSize: "12px", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "10px" }}>
            Projects
          </h2>
          {projects.map((proj, i) => (
            <div key={i} style={{ marginBottom: "10px" }}>
              <p style={{ fontSize: "12px", fontWeight: 700, margin: 0 }}>{proj.title}</p>
              <BulletLines
                items={
                  getProjectBullets(proj.description).length
                    ? getProjectBullets(proj.description)
                    : proj.description
                    ? [proj.description]
                    : []
                }
                style={{ marginTop: "4px" }}
              />
              {proj.url && (
                <p style={{ fontSize: "11px", margin: "2px 0 0" }}>
                  <RichText text={proj.url} />
                </p>
              )}
            </div>
          ))}
        </section>
      )}

      {skills.length > 0 && (
        <section style={{ marginTop: "22px" }}>
          <h2 style={{ fontSize: "12px", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "8px" }}>
            Skills
          </h2>
          <p style={{ fontSize: "12px", margin: 0 }}>{skills.join(", ")}</p>
        </section>
      )}

      {education.length > 0 && (
        <section style={{ marginTop: "22px" }}>
          <h2 style={{ fontSize: "12px", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "8px" }}>
            Education
          </h2>
          {education.map((edu, i) => (
            <p key={i} style={{ fontSize: "12px", margin: "0 0 4px" }}>
              {edu.degree}{edu.institution ? `, ${edu.institution}` : ""}{edu.year ? ` (${edu.year})` : ""}
            </p>
          ))}
        </section>
      )}
    </div>
  );
}

export function ResumeTemplate({
  format,
  data,
  highlightKeywords = [],
}: {
  format: "classic" | "modern" | "minimal";
  data: ResumeData;
  highlightKeywords?: string[];
}) {
  switch (format) {
    case "modern":
      return <ModernTemplate data={data} highlightKeywords={highlightKeywords} />;
    case "minimal":
      return <MinimalTemplate data={data} highlightKeywords={highlightKeywords} />;
    default:
      return <ClassicTemplate data={data} highlightKeywords={highlightKeywords} />;
  }
}
