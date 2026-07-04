from pydantic import BaseModel, Field
from typing import Optional


class PersonalDetails(BaseModel):
    name: str = ""
    title: str = ""
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    website: Optional[str] = None
    github: Optional[str] = None


class ExperienceItem(BaseModel):
    company: str
    title: str
    start_date: str
    end_date: str
    bullets: list[str] = Field(default_factory=list)


class ProjectItem(BaseModel):
    title: str
    description: str
    tech_stack: list[str] = Field(default_factory=list)
    status: Optional[str] = None
    url: Optional[str] = None


class EducationItem(BaseModel):
    institution: str
    degree: str
    year: str


class ResumeData(BaseModel):
    personal: PersonalDetails = Field(default_factory=PersonalDetails)
    summary: str = ""
    experience: list[ExperienceItem] = Field(default_factory=list)
    projects: list[ProjectItem] = Field(default_factory=list)
    education: list[EducationItem] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    awards: list[str] = Field(default_factory=list)


class ChangeExplanation(BaseModel):
    why: str
    confidence: float
    authenticity: str  # SAFE | STRETCH | UNVERIFIABLE
    interview_risk: str  # LOW | MEDIUM | HIGH


class SectionDiff(BaseModel):
    section: str
    original: str
    enhanced: str
    changes: list[ChangeExplanation] = Field(default_factory=list)
    accepted: Optional[bool] = None
    no_change_required: bool = False


class GapAnalysisOut(BaseModel):
    missing_skills: list[str] = Field(default_factory=list)
    missing_projects: list[str] = Field(default_factory=list)
    missing_certifications: list[str] = Field(default_factory=list)
    missing_frameworks: list[str] = Field(default_factory=list)


class ScoresOut(BaseModel):
    ai_readiness: float = 0
    ats_score: float = 0
    ai_terminology: float = 0
    project_evidence: float = 0
    technical_depth: float = 0
    measurable_achievements: float = 0
    band: str = "Beginner"


class SuggestedProject(BaseModel):
    title: str
    difficulty: str
    tech_stack: list[str]
    architecture: str
    roadmap: list[str]
    business_impact: str


class InterviewQuestionOut(BaseModel):
    id: str
    category: str
    question: str


class NextAction(BaseModel):
    title: str
    description: str
    type: str


class ResumeSuggestionOut(BaseModel):
    section: str
    title: str
    suggestion: str
    why: str


class PotentialCompanyOut(BaseModel):
    name: str
    role: str
    why_hiring: str
    fit_reason: str
    careers_hint: str = ""
    job_url: str = ""
    linkedin_url: str = ""
    match_score: int = 0
    search_keywords: str = ""


class ColdEmailOut(BaseModel):
    subject: str
    body: str


class OutreachOut(BaseModel):
    companies: list[PotentialCompanyOut] = Field(default_factory=list)
    cold_email: ColdEmailOut = Field(default_factory=lambda: ColdEmailOut(subject="", body=""))
    outreach_tip: str = ""


class DocumentUpdate(BaseModel):
    enhanced: str


class ResumeAnalysisOut(BaseModel):
    id: str
    status: str
    progress: int
    current_step: str
    original: ResumeData
    enhanced: ResumeData
    full_original: str = ""
    full_enhanced: str = ""
    diffs: list[SectionDiff]
    scores: ScoresOut
    gap_analysis: GapAnalysisOut
    suggested_projects: list[SuggestedProject]
    interview_questions: list[InterviewQuestionOut]
    next_actions: list[NextAction]
    suggestions: list[ResumeSuggestionOut] = Field(default_factory=list)
    potential_companies: list[PotentialCompanyOut] = Field(default_factory=list)
    cold_email: Optional[ColdEmailOut] = None
    outreach_tip: str = ""
    highlight_keywords: list[str] = Field(default_factory=list)
    ats_issues: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    confidence_strengths: list[dict] = Field(default_factory=list)
    experience_gaps: list[dict] = Field(default_factory=list)
    original_filename: str = ""
    original_file_type: str = "pdf"


class SectionUpdate(BaseModel):
    enhanced: str
    accepted: Optional[bool] = None


class EnhancedDataUpdate(BaseModel):
    enhanced: ResumeData


class UploadResponse(BaseModel):
    id: str
