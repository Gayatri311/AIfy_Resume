/** Typography & spacing tokens for ATS-friendly resume layout (preview, editor, PDF). */

type StyleOptions = {
  onePage?: boolean;
  compact?: boolean;
  /** Slightly larger type for on-screen editing (review / full screen). */
  editor?: boolean;
};

export function getResumeStyles({
  onePage = false,
  compact = false,
  editor = false,
}: StyleOptions = {}) {
  if (onePage) {
    return {
      page: "w-[816px] max-w-[816px] px-[34px] py-[22px] text-[10.5px] leading-[1.45] text-gray-900 antialiased",
      header: "border-b border-gray-300 pb-3 mb-1",
      name: "text-[22px] font-bold leading-tight tracking-tight text-gray-900",
      headline: "mt-1 block text-[10px] font-semibold uppercase tracking-[0.12em] text-gray-600",
      contact: "mt-2 flex flex-wrap items-center gap-x-2 gap-y-1 text-[9.5px] text-gray-600",
      contactSep: "text-gray-300 select-none",
      contactInput: "min-w-[5rem] bg-transparent text-[9.5px] text-gray-600",
      section: "mt-4 first:mt-0",
      sectionHeading:
        "mb-2 border-b-2 border-gray-800 pb-0.5 text-[9.5px] font-bold uppercase tracking-[0.14em] text-gray-900",
      body: "text-[10.5px] leading-[1.45] text-gray-800",
      jobBlock: "border-b border-gray-100 pb-2.5 last:border-b-0 last:pb-0",
      jobHeader: "flex flex-wrap items-baseline justify-between gap-x-3 gap-y-0.5",
      company: "text-[10.5px] font-semibold text-gray-900",
      dates: "shrink-0 text-[9.5px] tabular-nums text-gray-500",
      jobTitle: "mt-0.5 block text-[10px] font-medium text-gray-700",
      bulletList: "mt-1 space-y-0.5",
      bulletItem: "flex items-start gap-1.5",
      bulletMarker: "mt-[0.35em] shrink-0 text-[10px] leading-none text-gray-700",
      bulletText: "flex-1 text-[10.5px] leading-[1.45] text-gray-800",
      projectBlock: "border-b border-gray-100 pb-2 last:border-b-0 last:pb-0",
      projectTitle: "text-[10.5px] font-semibold text-gray-900",
      projectBody: "mt-0.5 text-[10.5px] leading-[1.45] text-gray-800",
      projectUrl: "mt-0.5 text-[9.5px] text-gray-600",
      skills: "text-[10.5px] leading-[1.45] text-gray-800",
      education: "text-[10.5px] text-gray-800",
      auxiliary: "text-[9.5px] text-gray-500",
      entryGap: "space-y-2.5",
      projectGap: "space-y-2",
      educationGap: "space-y-1",
    };
  }

  if (compact) {
    return {
      page: "max-w-[580px] px-6 py-5 text-[13px] leading-[1.5] text-gray-900 antialiased",
      header: "border-b border-gray-300 pb-4 mb-2",
      name: "text-[24px] font-bold leading-tight tracking-tight text-gray-900",
      headline: "mt-1 block text-xs font-semibold uppercase tracking-[0.1em] text-gray-600",
      contact: "mt-2.5 flex flex-wrap items-center gap-x-2.5 gap-y-1 text-xs text-gray-600",
      contactSep: "text-gray-300 select-none",
      contactInput: "min-w-[5rem] bg-transparent text-xs text-gray-600",
      section: "mt-5 first:mt-0",
      sectionHeading:
        "mb-2.5 border-b-2 border-gray-800 pb-1 text-[11px] font-bold uppercase tracking-[0.14em] text-gray-900",
      body: "text-[13px] leading-[1.55] text-gray-800",
      jobBlock: "border-b border-gray-100 pb-4 last:border-b-0 last:pb-0",
      jobHeader: "flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1",
      company: "text-[13px] font-semibold text-gray-900",
      dates: "shrink-0 text-xs tabular-nums text-gray-500",
      jobTitle: "mt-0.5 block text-[13px] font-medium text-gray-700",
      bulletList: "mt-1.5 space-y-1",
      bulletItem: "flex items-start gap-2",
      bulletMarker: "mt-[0.45em] shrink-0 text-[13px] leading-none text-gray-700",
      bulletText: "flex-1 text-[13px] leading-[1.55] text-gray-800",
      projectBlock: "border-b border-gray-100 pb-3 last:border-b-0 last:pb-0",
      projectTitle: "text-[13px] font-semibold text-gray-900",
      projectBody: "mt-1 text-[13px] leading-[1.55] text-gray-800",
      projectUrl: "mt-1 text-xs text-gray-600",
      skills: "text-[13px] leading-[1.55] text-gray-800",
      education: "text-[13px] text-gray-800",
      auxiliary: "text-xs text-gray-500",
      entryGap: "space-y-4",
      projectGap: "space-y-3",
      educationGap: "space-y-2",
    };
  }

  const preview = {
    page: "w-[816px] max-w-full px-[34px] py-10 text-[11px] leading-[1.5] text-gray-900 antialiased",
    header: "border-b border-gray-300 pb-4 mb-2",
    name: "text-[26px] font-bold leading-tight tracking-tight text-gray-900",
    headline: "mt-1.5 block text-[11px] font-semibold uppercase tracking-[0.12em] text-gray-600",
    contact: "mt-3 flex flex-wrap items-center gap-x-3 gap-y-1 text-[10.5px] text-gray-600",
    contactSep: "text-gray-300 select-none",
    contactInput: "min-w-[6rem] bg-transparent text-[10.5px] text-gray-600",
    section: "mt-6 first:mt-0",
    sectionHeading:
      "mb-3 border-b-2 border-gray-800 pb-1 text-[11px] font-bold uppercase tracking-[0.15em] text-gray-900",
    body: "text-[11px] leading-[1.55] text-gray-800",
    jobBlock: "border-b border-gray-100 pb-4 last:border-b-0 last:pb-0",
    jobHeader: "flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1",
    company: "text-[11px] font-semibold text-gray-900",
    dates: "shrink-0 text-[10.5px] tabular-nums text-gray-500",
    jobTitle: "mt-0.5 block text-[11px] font-medium text-gray-700",
    bulletList: "mt-2 space-y-1",
    bulletItem: "flex items-start gap-2",
    bulletMarker: "mt-[0.4em] shrink-0 text-[11px] leading-none text-gray-700",
    bulletText: "flex-1 text-[11px] leading-[1.55] text-gray-800",
    projectBlock: "border-b border-gray-100 pb-3.5 last:border-b-0 last:pb-0",
    projectTitle: "text-[11px] font-semibold text-gray-900",
    projectBody: "mt-1 text-[11px] leading-[1.55] text-gray-800",
    projectUrl: "mt-1 text-[10.5px] text-gray-600",
    skills: "text-[11px] leading-[1.55] text-gray-800",
    education: "text-[11px] text-gray-800",
    auxiliary: "text-[10.5px] text-gray-500",
    entryGap: "space-y-4",
    projectGap: "space-y-3.5",
    educationGap: "space-y-2",
  };

  if (!editor) {
    return preview;
  }

  return {
    ...preview,
    page: "w-[816px] max-w-full px-[34px] py-10 text-[12px] leading-[1.55] text-gray-900 antialiased",
    name: "text-[28px] font-bold leading-tight tracking-tight text-gray-900",
    headline: "mt-1.5 block text-[12px] font-semibold uppercase tracking-[0.12em] text-gray-600",
    contact: "mt-3 flex flex-wrap items-center gap-x-3 gap-y-1 text-[11.5px] text-gray-600",
    contactInput: "min-w-[6rem] bg-transparent text-[11.5px] text-gray-600",
    sectionHeading:
      "mb-3 border-b-2 border-gray-800 pb-1 text-[12px] font-bold uppercase tracking-[0.15em] text-gray-900",
    body: "text-[12px] leading-[1.55] text-gray-800",
    company: "text-[12px] font-semibold text-gray-900",
    dates: "shrink-0 text-[11px] tabular-nums text-gray-500",
    jobTitle: "mt-0.5 block text-[12px] font-medium text-gray-700",
    bulletMarker: "mt-[0.4em] shrink-0 text-[12px] leading-none text-gray-700",
    bulletText: "flex-1 text-[12px] leading-[1.55] text-gray-800",
    projectTitle: "text-[12px] font-semibold text-gray-900",
    projectBody: "mt-1 text-[12px] leading-[1.55] text-gray-800",
    projectUrl: "mt-1 text-[11px] text-gray-600",
    skills: "text-[12px] leading-[1.55] text-gray-800",
    education: "text-[12px] text-gray-800",
    auxiliary: "text-[11px] text-gray-500",
  };
}

export const EDITABLE_FIELD =
  "w-full rounded-sm border border-transparent bg-transparent px-0.5 py-0.5 -mx-0.5 transition-colors hover:border-gray-200 focus:border-gray-300 focus:outline-none";
