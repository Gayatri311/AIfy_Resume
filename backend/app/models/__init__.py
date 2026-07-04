import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    clerk_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    resumes: Mapped[list["Resume"]] = relationship(back_populates="user")


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    filename: Mapped[str] = mapped_column(String(512))
    file_path: Mapped[str] = mapped_column(String(1024))
    status: Mapped[str] = mapped_column(String(50), default="pending")
    progress: Mapped[int] = mapped_column(Integer, default=0)
    current_step: Mapped[str] = mapped_column(String(255), default="")
    original_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    enhanced_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="resumes")
    versions: Mapped[list["ResumeVersion"]] = relationship(back_populates="resume")
    sections: Mapped[list["ResumeSection"]] = relationship(back_populates="resume")
    diffs: Mapped[list["ResumeDiff"]] = relationship(back_populates="resume")
    scores: Mapped[Optional["Score"]] = relationship(back_populates="resume", uselist=False)
    gap_analysis: Mapped[Optional["GapAnalysis"]] = relationship(back_populates="resume", uselist=False)
    interview_questions: Mapped[list["InterviewQuestion"]] = relationship(back_populates="resume")
    projects: Mapped[list["Project"]] = relationship(back_populates="resume")


class ResumeVersion(Base):
    __tablename__ = "resume_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    resume_id: Mapped[str] = mapped_column(String(36), ForeignKey("resumes.id"))
    version_number: Mapped[int] = mapped_column(Integer)
    data: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    resume: Mapped["Resume"] = relationship(back_populates="versions")


class ResumeSection(Base):
    __tablename__ = "resume_sections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    resume_id: Mapped[str] = mapped_column(String(36), ForeignKey("resumes.id"))
    section_type: Mapped[str] = mapped_column(String(100))
    original_content: Mapped[str] = mapped_column(Text)
    enhanced_content: Mapped[str] = mapped_column(Text, default="")
    accepted: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    resume: Mapped["Resume"] = relationship(back_populates="sections")


class ResumeDiff(Base):
    __tablename__ = "resume_diffs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    resume_id: Mapped[str] = mapped_column(String(36), ForeignKey("resumes.id"))
    section: Mapped[str] = mapped_column(String(100))
    original: Mapped[str] = mapped_column(Text)
    enhanced: Mapped[str] = mapped_column(Text)
    changes: Mapped[list] = mapped_column(JSON, default=list)
    accepted: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    resume: Mapped["Resume"] = relationship(back_populates="diffs")


class Score(Base):
    __tablename__ = "scores"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    resume_id: Mapped[str] = mapped_column(String(36), ForeignKey("resumes.id"), unique=True)
    ai_readiness: Mapped[float] = mapped_column(Float, default=0)
    ats_score: Mapped[float] = mapped_column(Float, default=0)
    ai_terminology: Mapped[float] = mapped_column(Float, default=0)
    project_evidence: Mapped[float] = mapped_column(Float, default=0)
    technical_depth: Mapped[float] = mapped_column(Float, default=0)
    measurable_achievements: Mapped[float] = mapped_column(Float, default=0)
    band: Mapped[str] = mapped_column(String(50), default="Beginner")
    resume: Mapped["Resume"] = relationship(back_populates="scores")


class GapAnalysis(Base):
    __tablename__ = "gap_analysis"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    resume_id: Mapped[str] = mapped_column(String(36), ForeignKey("resumes.id"), unique=True)
    missing_skills: Mapped[list] = mapped_column(JSON, default=list)
    missing_projects: Mapped[list] = mapped_column(JSON, default=list)
    missing_certifications: Mapped[list] = mapped_column(JSON, default=list)
    missing_frameworks: Mapped[list] = mapped_column(JSON, default=list)
    resume: Mapped["Resume"] = relationship(back_populates="gap_analysis")


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    resume_id: Mapped[str] = mapped_column(String(36), ForeignKey("resumes.id"))
    category: Mapped[str] = mapped_column(String(50))
    question: Mapped[str] = mapped_column(Text)
    resume: Mapped["Resume"] = relationship(back_populates="interview_questions")


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    resume_id: Mapped[str] = mapped_column(String(36), ForeignKey("resumes.id"))
    title: Mapped[str] = mapped_column(String(512))
    difficulty: Mapped[str] = mapped_column(String(50))
    tech_stack: Mapped[list] = mapped_column(JSON, default=list)
    architecture: Mapped[str] = mapped_column(Text, default="")
    roadmap: Mapped[list] = mapped_column(JSON, default=list)
    business_impact: Mapped[str] = mapped_column(Text, default="")
    resume: Mapped["Resume"] = relationship(back_populates="projects")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    session_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    plan: Mapped[str] = mapped_column(String(20), default="free")
    status: Mapped[str] = mapped_column(String(30), default="inactive")
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    current_period_end: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
