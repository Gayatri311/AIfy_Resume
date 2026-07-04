"use client";

import { Plus, Trash2 } from "lucide-react";
import type {
  ResumeData,
  ExperienceItem,
  ProjectItem,
  EducationItem,
  PersonalDetails,
} from "@/types/resume";
import { contactItems, linkifyText } from "@/lib/linkify";
import { getExperienceBullets, getProjectBullets } from "@/lib/resume-format";
import { HighlightedText } from "@/components/resume/highlighted-text";
import { getResumeStyles, EDITABLE_FIELD } from "@/lib/resume-styles";
import { cn } from "@/lib/utils";

type ResumeStyles = ReturnType<typeof getResumeStyles>;

function SectionHeading({
  children,
  styles,
}: {
  children: React.ReactNode;
  styles: ResumeStyles;
}) {
  return <h2 className={styles.sectionHeading}>{children}</h2>;
}

function EditableField({
  value,
  onChange,
  className,
  multiline = false,
  readOnly = false,
  placeholder,
  highlightKeywords,
}: {
  value: string;
  onChange?: (value: string) => void;
  className?: string;
  multiline?: boolean;
  readOnly?: boolean;
  placeholder?: string;
  highlightKeywords?: string[];
}) {
  const display = value || placeholder || "";
  const useHighlights = readOnly && highlightKeywords && highlightKeywords.length > 0;

  if (readOnly) {
    if (multiline) {
      return (
        <p className={cn("whitespace-pre-wrap", className)}>
          {useHighlights ? (
            <HighlightedText text={display} keywords={highlightKeywords} />
          ) : (
            display
          )}
        </p>
      );
    }
    return (
      <span className={className}>
        {useHighlights ? (
          <HighlightedText text={display} keywords={highlightKeywords} />
        ) : (
          display
        )}
      </span>
    );
  }

  const shared = EDITABLE_FIELD;

  if (multiline) {
    return (
      <textarea
        value={value}
        onChange={(e) => onChange?.(e.target.value)}
        placeholder={placeholder}
        rows={Math.max(3, value.split("\n").length + 1)}
        className={cn(shared, "resize-none leading-relaxed", className)}
      />
    );
  }

  return (
    <input
      type="text"
      value={value}
      onChange={(e) => onChange?.(e.target.value)}
      placeholder={placeholder}
      className={cn(shared, className)}
    />
  );
}

function PersonalHeader({
  personal,
  readOnly,
  onChange,
  styles,
}: {
  personal: PersonalDetails;
  readOnly?: boolean;
  onChange?: (personal: PersonalDetails) => void;
  styles: ResumeStyles;
}) {
  const update = (patch: Partial<PersonalDetails>) =>
    onChange?.({ ...personal, ...patch });

  const contacts = contactItems(personal);

  return (
    <header className={styles.header}>
      <EditableField
        value={personal.name}
        onChange={readOnly ? undefined : (v) => update({ name: v })}
        readOnly={readOnly}
        placeholder="Your name"
        className={styles.name}
      />
      <EditableField
        value={personal.title}
        onChange={readOnly ? undefined : (v) => update({ title: v })}
        readOnly={readOnly}
        placeholder="Professional title"
        className={styles.headline}
      />
      {readOnly ? (
        contacts.length > 0 && (
          <p className={styles.contact}>
            {contacts.map((item, i) => (
              <span key={i} className="inline-flex items-center">
                {i > 0 && (
                  <span className={cn(styles.contactSep, "mx-3")} aria-hidden>
                    |
                  </span>
                )}
                {linkifyText(item)}
              </span>
            ))}
          </p>
        )
      ) : (
        <div className={styles.contact}>
          {(
            [
              ["email", "Email"],
              ["phone", "Phone"],
              ["location", "Location"],
              ["linkedin", "LinkedIn"],
              ["github", "GitHub"],
              ["website", "Website"],
            ] as const
          ).map(([key, label], i) => (
            <span key={key} className="inline-flex items-center">
              {i > 0 && (
                <span className={cn(styles.contactSep, "mx-3")} aria-hidden>
                  |
                </span>
              )}
              <EditableField
                value={personal[key] || ""}
                onChange={(v) => update({ [key]: v || undefined })}
                placeholder={label}
                className={styles.contactInput}
              />
            </span>
          ))}
        </div>
      )}
    </header>
  );
}

function ExperienceSection({
  experience,
  readOnly,
  onChange,
  styles,
  highlightKeywords,
}: {
  experience: ExperienceItem[];
  readOnly?: boolean;
  onChange?: (experience: ExperienceItem[]) => void;
  styles: ResumeStyles;
  highlightKeywords?: string[];
}) {
  if (!experience.length && readOnly) return null;

  const updateJob = (index: number, patch: Partial<ExperienceItem>) => {
    const next = experience.map((item, i) => (i === index ? { ...item, ...patch } : item));
    onChange?.(next);
  };

  return (
    <section className={styles.section}>
      <SectionHeading styles={styles}>Professional Experience</SectionHeading>
      {experience.length === 0 && !readOnly && (
        <p className="text-sm text-gray-400">No experience entries yet.</p>
      )}
      <div className={styles.entryGap}>
        {experience.map((exp, i) => (
          <article key={i} className={cn("group", styles.jobBlock)}>
            <div className={styles.jobHeader}>
              <EditableField
                value={exp.company}
                onChange={readOnly ? undefined : (v) => updateJob(i, { company: v })}
                readOnly={readOnly}
                className={styles.company}
                placeholder="Company"
              />
              <div className={cn("flex shrink-0 items-center gap-1", styles.dates)}>
                <EditableField
                  value={exp.start_date}
                  onChange={readOnly ? undefined : (v) => updateJob(i, { start_date: v })}
                  readOnly={readOnly}
                  placeholder="Start"
                  className="w-20 text-right"
                />
                <span>–</span>
                <EditableField
                  value={exp.end_date}
                  onChange={readOnly ? undefined : (v) => updateJob(i, { end_date: v })}
                  readOnly={readOnly}
                  placeholder="End"
                  className="w-20"
                />
              </div>
            </div>
            <EditableField
              value={exp.title}
              onChange={readOnly ? undefined : (v) => updateJob(i, { title: v })}
              readOnly={readOnly}
              className={styles.jobTitle}
              highlightKeywords={highlightKeywords}
              placeholder="Job title"
            />
            <ul className={cn(styles.bulletList, "list-none pl-0")}>
              {getExperienceBullets(exp).map((bullet, k) => (
                <li key={k} className={styles.bulletItem}>
                  <span className={styles.bulletMarker} aria-hidden>
                    •
                  </span>
                  <EditableField
                    value={bullet}
                    onChange={
                      readOnly
                        ? undefined
                        : (v) => {
                            const flat = getExperienceBullets(exp);
                            flat[k] = v;
                            updateJob(i, { bullets: flat });
                          }
                    }
                    readOnly={readOnly}
                    multiline
                    className={styles.bulletText}
                    highlightKeywords={highlightKeywords}
                    placeholder="Achievement or responsibility"
                  />
                  {!readOnly && (
                    <button
                      type="button"
                      onClick={() => {
                        const flat = getExperienceBullets(exp).filter((_, idx) => idx !== k);
                        updateJob(i, { bullets: flat });
                      }}
                      className="mt-1 rounded p-0.5 text-gray-400 opacity-0 transition hover:text-red-500 group-hover:opacity-100"
                      aria-label="Remove bullet"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  )}
                </li>
              ))}
            </ul>
            {!readOnly && (
              <button
                type="button"
                onClick={() =>
                  updateJob(i, { bullets: [...getExperienceBullets(exp), ""] })
                }
                className={cn("mt-2 flex items-center gap-1 hover:text-gray-700", styles.auxiliary)}
              >
                <Plus className="h-3.5 w-3.5" /> Add bullet
              </button>
            )}
          </article>
        ))}
      </div>
    </section>
  );
}

function ProjectsSection({
  projects,
  readOnly,
  onChange,
  styles,
  highlightKeywords,
}: {
  projects: ProjectItem[];
  readOnly?: boolean;
  onChange?: (projects: ProjectItem[]) => void;
  styles: ResumeStyles;
  highlightKeywords?: string[];
}) {
  if (!projects.length) return null;

  const updateProject = (index: number, patch: Partial<ProjectItem>) => {
    onChange?.(projects.map((p, i) => (i === index ? { ...p, ...patch } : p)));
  };

  return (
    <section className={styles.section}>
      <SectionHeading styles={styles}>Projects</SectionHeading>
      <div className={styles.projectGap}>
        {projects.map((proj, i) => (
          <article key={i} className={styles.projectBlock}>
            <EditableField
              value={proj.title}
              onChange={readOnly ? undefined : (v) => updateProject(i, { title: v })}
              readOnly={readOnly}
              className={styles.projectTitle}
              highlightKeywords={highlightKeywords}
              placeholder="Project name"
            />
            {readOnly ? (
              getProjectBullets(proj.description).length > 0 ? (
                <ul className={cn(styles.bulletList, "list-none pl-0")}>
                  {getProjectBullets(proj.description).map((line, k) => (
                    <li key={k} className={styles.bulletItem}>
                      <span className={styles.bulletMarker} aria-hidden>
                        •
                      </span>
                      <span className={styles.bulletText}>
                        {highlightKeywords?.length ? (
                          <HighlightedText text={line} keywords={highlightKeywords} />
                        ) : (
                          line
                        )}
                      </span>
                    </li>
                  ))}
                </ul>
              ) : (
                proj.description && (
                  <EditableField
                    value={proj.description}
                    readOnly
                    multiline
                    className={styles.projectBody}
                    highlightKeywords={highlightKeywords}
                  />
                )
              )
            ) : (
              <EditableField
                value={proj.description}
                onChange={(v) => updateProject(i, { description: v })}
                multiline
                className={styles.projectBody}
                placeholder="What you built and the impact"
              />
            )}
            {(proj.url || !readOnly) && (
              <EditableField
                value={proj.url || ""}
                onChange={readOnly ? undefined : (v) => updateProject(i, { url: v || undefined })}
                readOnly={readOnly}
                className={styles.projectUrl}
                placeholder="Project URL (optional)"
              />
            )}
          </article>
        ))}
      </div>
    </section>
  );
}

function SkillsSection({
  skills,
  readOnly,
  onChange,
  styles,
  highlightKeywords,
}: {
  skills: string[];
  readOnly?: boolean;
  onChange?: (skills: string[]) => void;
  styles: ResumeStyles;
  highlightKeywords?: string[];
}) {
  if (!skills.length && readOnly) return null;

  if (readOnly) {
    const skillsLine = skills.join(" · ");
    return (
      <section className={styles.section}>
        <SectionHeading styles={styles}>Skills</SectionHeading>
        <p className={styles.skills}>
          {highlightKeywords?.length ? (
            <HighlightedText text={skillsLine} keywords={highlightKeywords} />
          ) : (
            skillsLine
          )}
        </p>
      </section>
    );
  }

  return (
    <section className={styles.section}>
      <SectionHeading styles={styles}>Skills</SectionHeading>
      <EditableField
        value={skills.join(" · ")}
        onChange={(v) =>
          onChange?.(
            v
              .split(/[,•|·]/)
              .map((s) => s.trim())
              .filter(Boolean)
          )
        }
        multiline
        className={styles.skills}
        placeholder="Python · React · LLMs · RAG"
      />
    </section>
  );
}

function EducationSection({
  education,
  readOnly,
  onChange,
  styles,
}: {
  education: EducationItem[];
  readOnly?: boolean;
  onChange?: (education: EducationItem[]) => void;
  styles: ResumeStyles;
}) {
  if (!education.length && readOnly) return null;

  const updateEdu = (index: number, patch: Partial<EducationItem>) => {
    onChange?.(education.map((e, i) => (i === index ? { ...e, ...patch } : e)));
  };

  return (
    <section className={styles.section}>
      <SectionHeading styles={styles}>Education</SectionHeading>
      <div className={styles.educationGap}>
        {education.map((edu, i) => (
          <div key={i} className={styles.education}>
            {readOnly ? (
              <p>
                <strong className="font-semibold text-gray-900">{edu.degree}</strong>
                {edu.institution ? (
                  <span className="text-gray-700">{` — ${edu.institution}`}</span>
                ) : null}
                {edu.year ? (
                  <span className="text-gray-500">{`, ${edu.year}`}</span>
                ) : null}
              </p>
            ) : (
              <div className="grid gap-1 sm:grid-cols-[1fr_1fr_auto]">
                <EditableField
                  value={edu.degree}
                  onChange={(v) => updateEdu(i, { degree: v })}
                  placeholder="Degree"
                />
                <EditableField
                  value={edu.institution}
                  onChange={(v) => updateEdu(i, { institution: v })}
                  placeholder="Institution"
                />
                <EditableField
                  value={edu.year}
                  onChange={(v) => updateEdu(i, { year: v })}
                  placeholder="Year"
                  className="w-16"
                />
              </div>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}

export function ResumePaper({
  data,
  editable = false,
  muted = false,
  compact = false,
  onePage = false,
  onChange,
  className,
  highlightKeywords,
}: {
  data: ResumeData;
  editable?: boolean;
  muted?: boolean;
  compact?: boolean;
  onePage?: boolean;
  onChange?: (data: ResumeData) => void;
  className?: string;
  highlightKeywords?: string[];
}) {
  const readOnly = !editable;
  const styles = getResumeStyles({ onePage, compact, editor: editable && !onePage && !compact });

  const patch = (partial: Partial<ResumeData>) => onChange?.({ ...data, ...partial });

  return (
    <div
      className={cn(
        "resume-export-page mx-auto w-full bg-white font-sans",
        onePage && "resume-page",
        styles.page,
        muted && "opacity-90",
        className
      )}
    >
      <PersonalHeader
        personal={data.personal}
        readOnly={readOnly}
        styles={styles}
        onChange={(personal) => patch({ personal })}
      />

      {(data.summary || editable) && (
        <section className={styles.section}>
          <SectionHeading styles={styles}>Professional Summary</SectionHeading>
          <EditableField
            value={data.summary}
            onChange={readOnly ? undefined : (v) => patch({ summary: v })}
            readOnly={readOnly}
            multiline
            className={styles.body}
            highlightKeywords={highlightKeywords}
            placeholder="Professional summary"
          />
        </section>
      )}

      <ExperienceSection
        experience={data.experience}
        readOnly={readOnly}
        styles={styles}
        highlightKeywords={highlightKeywords}
        onChange={(experience) => patch({ experience })}
      />

      <ProjectsSection
        projects={data.projects}
        readOnly={readOnly}
        styles={styles}
        highlightKeywords={highlightKeywords}
        onChange={(projects) => patch({ projects })}
      />

      <SkillsSection
        skills={data.skills}
        readOnly={readOnly}
        styles={styles}
        highlightKeywords={highlightKeywords}
        onChange={(skills) => patch({ skills })}
      />

      <EducationSection
        education={data.education}
        readOnly={readOnly}
        styles={styles}
        onChange={(education) => patch({ education })}
      />
    </div>
  );
}
