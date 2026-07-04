export type AuthenticityLevel = "SAFE" | "STRETCH" | "UNVERIFIABLE";
export type InterviewRisk = "LOW" | "MEDIUM" | "HIGH";
export type ReadinessBand = "Beginner" | "Emerging" | "AI Aware" | "AI Ready";

export interface PersonalDetails {
  name: string;
  title: string;
  email?: string;
  phone?: string;
  location?: string;
  linkedin?: string;
  website?: string;
  github?: string;
}

export interface ExperienceItem {
  company: string;
  title: string;
  start_date: string;
  end_date: string;
  bullets: string[];
}

export interface ProjectItem {
  title: string;
  description: string;
  tech_stack?: string[];
  status?: string;
  url?: string;
}

export interface EducationItem {
  institution: string;
  degree: string;
  year: string;
}

export interface ResumeData {
  personal: PersonalDetails;
  summary: string;
  experience: ExperienceItem[];
  projects: ProjectItem[];
  education: EducationItem[];
  skills: string[];
  certifications?: string[];
  awards?: string[];
}

export interface ChangeExplanation {
  why: string;
  confidence: number;
  authenticity: AuthenticityLevel;
  interview_risk: InterviewRisk;
}

export interface SectionDiff {
  section: string;
  original: string;
  enhanced: string;
  changes: ChangeExplanation[];
  accepted?: boolean;
  no_change_required?: boolean;
}

export interface GapAnalysis {
  missing_skills: string[];
  missing_projects: string[];
  missing_certifications: string[];
  missing_frameworks?: string[];
}

export interface Scores {
  ai_readiness: number;
  ats_score: number;
  ai_terminology: number;
  project_evidence: number;
  technical_depth: number;
  measurable_achievements: number;
  band: ReadinessBand;
}

export interface SuggestedProject {
  title: string;
  difficulty: string;
  tech_stack: string[];
  architecture: string;
  roadmap: string[];
  business_impact: string;
}

export interface InterviewQuestion {
  id: string;
  category: "Behavioral" | "Technical" | "AI" | "Scenario-based";
  question: string;
}

export interface NextAction {
  title: string;
  description: string;
  type: "project" | "certification" | "learning";
}

export interface ResumeSuggestion {
  section: string;
  title: string;
  suggestion: string;
  why: string;
}

export interface PotentialCompany {
  name: string;
  role: string;
  why_hiring: string;
  fit_reason: string;
  careers_hint: string;
  job_url?: string;
  linkedin_url?: string;
  match_score?: number;
  search_keywords?: string;
}

export interface ColdEmail {
  subject: string;
  body: string;
}

export interface ResumeAnalysis {
  id: string;
  status: "pending" | "processing" | "completed" | "failed";
  progress: number;
  current_step: string;
  original: ResumeData;
  enhanced: ResumeData;
  full_original?: string;
  full_enhanced?: string;
  diffs: SectionDiff[];
  scores: Scores;
  gap_analysis: GapAnalysis;
  suggested_projects: SuggestedProject[];
  interview_questions: InterviewQuestion[];
  next_actions: NextAction[];
  suggestions?: ResumeSuggestion[];
  potential_companies?: PotentialCompany[];
  cold_email?: ColdEmail;
  outreach_tip?: string;
  highlight_keywords?: string[];
  ats_issues?: string[];
  missing_keywords?: string[];
  confidence_strengths?: { label: string; level: string }[];
  experience_gaps?: { label: string; level: string }[];
  original_filename?: string;
  original_file_type?: "pdf" | "docx";
}
