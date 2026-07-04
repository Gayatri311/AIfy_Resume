import io
import os
import uuid

import aiofiles
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.models import Resume, ResumeDiff, Score, GapAnalysis, InterviewQuestion, Project
from app.schemas.resume import (
    ResumeAnalysisOut, UploadResponse, SectionUpdate, DocumentUpdate, EnhancedDataUpdate, ResumeData,
    ScoresOut, GapAnalysisOut, SectionDiff, SuggestedProject, ResumeSuggestionOut,
    InterviewQuestionOut, NextAction,
)
from app.services.section_sync import strip_no_change_note, NO_CHANGE_NOTE, apply_section_text
from app.services.resume_document import (
    build_full_original,
    build_full_enhanced,
    apply_document_to_resume,
)
from app.services.pipeline import SECTION_BUILDERS
from app.services.suggestion_builder import build_suggestions
from app.services.company_outreach import (
    outreach_from_stored,
    _fallback_outreach,
    sanitize_outreach_companies,
    outreach_needs_refresh,
)
from app.services.keyword_highlights import build_highlight_keywords
from app.services.suggested_store import save_suggested
from app.services.section_apply import apply_accept
from app.services.resume_cleanup import strip_invented_sections, ensure_project_coverage, ensure_ai_projects
from app.services.resume_format import normalize_resume_data
from app.services.ai_career_hook import apply_ai_career_hook
from app.services.link_preservation import preserve_links
from app.services.parser import extract_text, parse_resume_text
from app.services.resume_validator import validate_resume_text
from app.services.exceptions import ResumeValidationError
from app.tasks.resume_tasks import _process_resume_async

router = APIRouter(prefix="/resumes", tags=["resumes"])
settings = get_settings()


@router.post("/upload", response_model=UploadResponse)
async def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(400, "No file provided")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in (".pdf", ".docx"):
        raise HTTPException(400, "Only PDF and DOCX files are supported")

    content = await file.read()
    if len(content) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(400, f"File exceeds {settings.max_upload_mb}MB limit")

    os.makedirs(settings.upload_dir, exist_ok=True)
    resume_id = str(uuid.uuid4())
    file_path = os.path.join(settings.upload_dir, f"{resume_id}{ext}")

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    try:
        text = extract_text(file_path)
        parsed = parse_resume_text(text)
        validate_resume_text(text, parsed)
    except ResumeValidationError as e:
        os.remove(file_path)
        raise HTTPException(400, e.message)
    except Exception as e:
        os.remove(file_path)
        raise HTTPException(400, f"Could not read uploaded file: {e}")

    resume = Resume(
        id=resume_id,
        filename=file.filename,
        file_path=file_path,
        status="pending",
    )
    db.add(resume)
    await db.flush()

    if settings.use_celery:
        try:
            from app.tasks.resume_tasks import process_resume_task
            process_resume_task.delay(resume_id)
        except Exception:
            background_tasks.add_task(_process_resume_async, resume_id)
    else:
        background_tasks.add_task(_process_resume_async, resume_id)

    return UploadResponse(id=resume_id)


def _build_analysis_out(resume: Resume) -> ResumeAnalysisOut:
    original = ResumeData(**(resume.original_data or {}))
    enhanced = ResumeData(**(resume.enhanced_data or original.model_dump()))
    enhanced = strip_invented_sections(original, enhanced)
    enhanced = ensure_project_coverage(original, enhanced)
    enhanced = ensure_ai_projects(enhanced)
    enhanced = apply_ai_career_hook(original, enhanced)
    enhanced = preserve_links(original, enhanced)
    original = normalize_resume_data(original)
    enhanced = normalize_resume_data(enhanced)

    suggestion_entries = [
        d for d in (resume.diffs or []) if d.section == "suggestions"
    ]
    outreach_entries = [
        d for d in (resume.diffs or []) if d.section == "outreach"
    ]
    diffs = [
        SectionDiff(
            section=d.section,
            original=d.original,
            enhanced=d.enhanced,
            changes=d.changes or [],
            accepted=d.accepted,
            no_change_required=NO_CHANGE_NOTE in (d.enhanced or ""),
        )
        for d in (resume.diffs or [])
        if d.section not in ("suggestions", "outreach")
    ]

    scores = ScoresOut()
    if resume.scores:
        scores = ScoresOut(
            ai_readiness=resume.scores.ai_readiness,
            ats_score=resume.scores.ats_score,
            ai_terminology=resume.scores.ai_terminology,
            project_evidence=resume.scores.project_evidence,
            technical_depth=resume.scores.technical_depth,
            measurable_achievements=resume.scores.measurable_achievements,
            band=resume.scores.band,
        )

    gaps = GapAnalysisOut()
    if resume.gap_analysis:
        gaps = GapAnalysisOut(
            missing_skills=resume.gap_analysis.missing_skills or [],
            missing_projects=resume.gap_analysis.missing_projects or [],
            missing_certifications=resume.gap_analysis.missing_certifications or [],
            missing_frameworks=resume.gap_analysis.missing_frameworks or [],
        )

    projects = [
        SuggestedProject(
            title=p.title,
            difficulty=p.difficulty,
            tech_stack=p.tech_stack or [],
            architecture=p.architecture or "",
            roadmap=p.roadmap or [],
            business_impact=p.business_impact or "",
        )
        for p in (resume.projects or [])
    ]

    questions = [
        InterviewQuestionOut(id=q.id, category=q.category, question=q.question)
        for q in (resume.interview_questions or [])
    ]

    next_actions = [
        NextAction(
            title="Build an AI Documentation Assistant using RAG",
            description="Create a hands-on project to prove your AI workflow claims.",
            type="project",
        ),
        NextAction(
            title="Complete Prompt Engineering certification",
            description="Strengthen credibility for LLM-related resume claims.",
            type="certification",
        ),
        NextAction(
            title="Learn LangChain basics",
            description="Foundation for building AI agents and RAG pipelines.",
            type="learning",
        ),
    ]

    llm_suggestions = suggestion_entries[0].changes if suggestion_entries else []
    suggestions = build_suggestions(original, enhanced, gaps, projects, llm_suggestions)

    outreach = outreach_from_stored(outreach_entries[0].changes if outreach_entries else None)
    if not outreach:
        outreach = _fallback_outreach(enhanced)
    elif outreach.companies and outreach_needs_refresh(outreach.companies):
        outreach = _fallback_outreach(enhanced)

    companies = sanitize_outreach_companies(outreach.companies, enhanced)

    highlight_keywords = build_highlight_keywords(
        enhanced,
        resume.gap_analysis.missing_skills if resume.gap_analysis else [],
    )

    return ResumeAnalysisOut(
        id=resume.id,
        status=resume.status,
        progress=resume.progress,
        current_step=resume.current_step,
        original=original,
        enhanced=enhanced,
        full_original=build_full_original(original.personal, diffs),
        full_enhanced=build_full_enhanced(enhanced.personal, diffs),
        diffs=diffs,
        scores=scores,
        gap_analysis=gaps,
        suggested_projects=projects,
        interview_questions=questions,
        next_actions=next_actions,
        suggestions=suggestions,
        potential_companies=companies,
        cold_email=outreach.cold_email,
        outreach_tip=outreach.outreach_tip,
        highlight_keywords=highlight_keywords,
        original_filename=resume.filename or "",
        original_file_type="pdf" if (resume.file_path or "").lower().endswith(".pdf") else "docx",
        confidence_strengths=[
            {"label": "AI-assisted documentation", "level": "STRONG"},
            {"label": "Prompt Engineering", "level": "STRONG"},
            {"label": "Predictive Ops", "level": "GOOD"},
        ],
        experience_gaps=[
            {"label": "AI Agent Frameworks", "level": "MISSING"},
            {"label": "Workflow Automation", "level": "WEAK"},
            {"label": "Model Fine-tuning", "level": "GAP"},
        ],
    )


@router.get("/{resume_id}", response_model=ResumeAnalysisOut)
async def get_resume(
    resume_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Resume)
        .where(Resume.id == resume_id)
        .options(
            selectinload(Resume.diffs),
            selectinload(Resume.scores),
            selectinload(Resume.gap_analysis),
            selectinload(Resume.interview_questions),
            selectinload(Resume.projects),
        )
    )
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(404, "Resume not found")
    return _build_analysis_out(resume)


@router.get("/{resume_id}/file")
async def get_original_file(
    resume_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Serve the uploaded resume file for inline PDF viewing."""
    result = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume = result.scalar_one_or_none()
    if not resume or not resume.file_path or not os.path.isfile(resume.file_path):
        raise HTTPException(404, "Original file not found")

    ext = os.path.splitext(resume.file_path)[1].lower()
    media_types = {
        ".pdf": "application/pdf",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }
    media_type = media_types.get(ext, "application/octet-stream")
    filename = resume.filename or f"resume{ext}"

    return FileResponse(
        resume.file_path,
        media_type=media_type,
        filename=filename,
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


@router.patch("/{resume_id}/sections/{section}", response_model=ResumeAnalysisOut)
async def update_section(
    resume_id: str,
    section: str,
    body: SectionUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Resume)
        .where(Resume.id == resume_id)
        .options(
            selectinload(Resume.diffs),
            selectinload(Resume.scores),
            selectinload(Resume.gap_analysis),
            selectinload(Resume.interview_questions),
            selectinload(Resume.projects),
        )
    )
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(404, "Resume not found")

    clean_enhanced = strip_no_change_note(body.enhanced)

    for diff in resume.diffs:
        if diff.section == section and body.accepted is not None:
            diff.accepted = body.accepted

    original = ResumeData(**(resume.original_data or {}))
    accepted = ResumeData(**(resume.enhanced_data or original.model_dump()))
    builder = SECTION_BUILDERS.get(section)

    if body.accepted is False:
        updated = apply_accept(accepted, original, original, section, False)
        for diff in resume.diffs:
            if diff.section == section:
                diff.enhanced = diff.original
    else:
        updated = apply_section_text(accepted, section, clean_enhanced)
        if builder:
            for diff in resume.diffs:
                if diff.section == section:
                    diff.enhanced = clean_enhanced or builder(updated)

    resume.enhanced_data = updated.model_dump()

    await db.flush()
    await db.commit()
    return _build_analysis_out(resume)


@router.patch("/{resume_id}/enhanced", response_model=ResumeAnalysisOut)
async def update_enhanced_data(
    resume_id: str,
    body: EnhancedDataUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Resume)
        .where(Resume.id == resume_id)
        .options(
            selectinload(Resume.diffs),
            selectinload(Resume.scores),
            selectinload(Resume.gap_analysis),
            selectinload(Resume.interview_questions),
            selectinload(Resume.projects),
        )
    )
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(404, "Resume not found")

    original = ResumeData(**(resume.original_data or {}))
    payload = strip_invented_sections(original, body.enhanced)
    resume.enhanced_data = payload.model_dump()

    for diff in resume.diffs or []:
        if diff.section == "suggestions":
            continue
        builder = SECTION_BUILDERS.get(diff.section)
        if builder:
            diff.enhanced = builder(payload)
            diff.accepted = True

    await db.flush()
    await db.commit()
    return _build_analysis_out(resume)


@router.patch("/{resume_id}/document", response_model=ResumeAnalysisOut)
async def update_document(
    resume_id: str,
    body: DocumentUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Resume)
        .where(Resume.id == resume_id)
        .options(
            selectinload(Resume.diffs),
            selectinload(Resume.scores),
            selectinload(Resume.gap_analysis),
            selectinload(Resume.interview_questions),
            selectinload(Resume.projects),
        )
    )
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(404, "Resume not found")

    base = ResumeData(**(resume.enhanced_data or resume.original_data or {}))
    try:
        updated, section_blocks = apply_document_to_resume(base, resume.diffs or [], body.enhanced)
    except ValueError as e:
        raise HTTPException(400, str(e))

    resume.enhanced_data = updated.model_dump()

    for diff in resume.diffs or []:
        if diff.section in section_blocks:
            diff.enhanced = section_blocks[diff.section]
            diff.accepted = True

    await db.flush()
    await db.commit()
    return _build_analysis_out(resume)


@router.post("/{resume_id}/sections/{section}/regenerate", response_model=ResumeAnalysisOut)
async def regenerate_section(
    resume_id: str,
    section: str,
    db: AsyncSession = Depends(get_db),
):
    from app.services.pipeline import run_pipeline

    result = await db.execute(
        select(Resume)
        .where(Resume.id == resume_id)
        .options(selectinload(Resume.diffs))
    )
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(404, "Resume not found")

    pipeline_result = run_pipeline(resume.file_path)
    save_suggested(resume_id, pipeline_result["enhanced"])

    for diff in resume.diffs:
        for new_diff in pipeline_result["diffs"]:
            if diff.section == new_diff["section"]:
                if diff.section == section:
                    diff.enhanced = new_diff["enhanced"]
                    diff.changes = new_diff.get("changes", [])
                    diff.accepted = None

    await db.flush()

    result = await db.execute(
        select(Resume)
        .where(Resume.id == resume_id)
        .options(
            selectinload(Resume.diffs),
            selectinload(Resume.scores),
            selectinload(Resume.gap_analysis),
            selectinload(Resume.interview_questions),
            selectinload(Resume.projects),
        )
    )
    resume = result.scalar_one()
    await db.commit()
    return _build_analysis_out(resume)


@router.get("/{resume_id}/export")
async def export_resume(
    resume_id: str,
    format: str = "pdf",
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume = result.scalar_one_or_none()
    if not resume or not resume.enhanced_data:
        raise HTTPException(404, "Resume not found")

    data = ResumeData(**resume.enhanced_data)
    original = ResumeData(**(resume.original_data or {}))
    data = strip_invented_sections(original, data)

    if format == "pdf":
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from app.services.bullet_utils import normalize_bullet_list

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        y = height - 50

        c.setFont("Helvetica-Bold", 18)
        c.drawString(50, y, data.personal.name)
        y -= 20
        c.setFont("Helvetica", 12)
        c.drawString(50, y, data.personal.title)
        y -= 30

        if data.summary:
            c.setFont("Helvetica-Bold", 10)
            c.drawString(50, y, "SUMMARY")
            y -= 15
            c.setFont("Helvetica", 9)
            for line in _wrap_text(data.summary, 90):
                c.drawString(50, y, line)
                y -= 12

        for exp in data.experience:
            y -= 10
            c.setFont("Helvetica-Bold", 10)
            c.drawString(50, y, f"{exp.company} — {exp.start_date} to {exp.end_date}")
            y -= 12
            if exp.title:
                c.setFont("Helvetica", 9)
                c.drawString(50, y, exp.title)
                y -= 12
            for bullet in normalize_bullet_list(exp.bullets):
                for line in _wrap_text(f"• {bullet}", 85):
                    c.setFont("Helvetica", 9)
                    c.drawString(55, y, line)
                    y -= 12
                    if y < 50:
                        c.showPage()
                        y = height - 50

        c.save()
        buffer.seek(0)
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=alfy-resume.pdf"},
        )

    raise HTTPException(400, "Unsupported format")


def _wrap_text(text: str, width: int) -> list[str]:
    words = text.split()
    lines = []
    current = ""
    for word in words:
        if len(current) + len(word) + 1 <= width:
            current += (" " if current else "") + word
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines
