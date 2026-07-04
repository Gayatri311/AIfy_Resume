"use client";

const FAQS = [
  {
    q: "Will Alfy fabricate experience on my resume?",
    a: "No. Alfy improves clarity and impact using your real work. Every change is explained with authenticity tags (SAFE / STRETCH) so you know what to stand behind in interviews.",
  },
  {
    q: "How is this different from ChatGPT for resumes?",
    a: "Alfy parses your actual resume file, scores ATS readiness, shows a section-by-section diff you can accept or reject, and generates interview questions from your enhanced version.",
  },
  {
    q: "What file formats are supported?",
    a: "PDF and DOCX. Upload your resume and Alfy will parse it, suggest improvements, and let you export a clean PDF when you're done reviewing.",
  },
  {
    q: "Can I edit the suggestions before accepting?",
    a: "Yes. Review each section side-by-side, accept or reject changes, or edit the suggested text manually before it goes into your final resume.",
  },
  {
    q: "What sections does Alfy enhance?",
    a: "Summary, experience, projects, skills, and education — with clear before/after diffs for each section.",
  },
];

export function FaqSection() {
  return (
    <section id="faq" className="border-t border-border bg-muted/30 py-20">
      <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
        <h2 className="text-center text-3xl font-bold">Frequently asked questions</h2>
        <div className="mt-10 space-y-4">
          {FAQS.map((faq) => (
            <details
              key={faq.q}
              className="group rounded-xl border border-border bg-card px-5 py-4"
            >
              <summary className="cursor-pointer list-none font-medium marker:content-none [&::-webkit-details-marker]:hidden">
                {faq.q}
              </summary>
              <p className="mt-3 text-sm leading-relaxed text-muted-foreground">{faq.a}</p>
            </details>
          ))}
        </div>
      </div>
    </section>
  );
}
