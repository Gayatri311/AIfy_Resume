import asyncio
import logging
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.celery_app import celery_app
from app.core.database import async_session
from app.models import Resume, ResumeDiff, Score, GapAnalysis, InterviewQuestion, Project
from app.services.pipeline import run_pipeline, PROCESSING_STEPS
from app.services.parser import extract_text, parse_resume_text
from app.services.resume_validator import validate_resume_text
from app.services.exceptions import ResumeValidationError

logger = logging.getLogger(__name__)


def _run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _process_resume_async(resume_id: str):
    async with async_session() as db:
        result = await db.execute(select(Resume).where(Resume.id == resume_id))
        resume = result.scalar_one_or_none()
        if not resume:
            return

        resume.status = "processing"
        resume.progress = 10
        resume.current_step = PROCESSING_STEPS[0]
        await db.commit()

        try:
            text = extract_text(resume.file_path)
            original = parse_resume_text(text)
            validate_resume_text(text, original)

            resume.progress = 20
            resume.current_step = PROCESSING_STEPS[1]
            await db.commit()

            # Run heavy sync pipeline off the event loop so status polls stay responsive.
            logger.info("Starting pipeline for resume %s", resume_id)
            pipeline_result = await asyncio.to_thread(run_pipeline, resume.file_path)
            logger.info("Pipeline finished for resume %s", resume_id)

            resume.original_data = pipeline_result["original"]
            resume.enhanced_data = pipeline_result["enhanced"]
            from app.services.suggested_store import save_suggested
            save_suggested(resume_id, pipeline_result["enhanced"])
            resume.progress = 100
            resume.current_step = "Complete"
            resume.status = "completed"

            for diff_data in pipeline_result["diffs"]:
                db.add(ResumeDiff(
                    resume_id=resume_id,
                    section=diff_data["section"],
                    original=diff_data["original"],
                    enhanced=diff_data["enhanced"],
                    changes=diff_data.get("changes", []),
                ))

            if pipeline_result.get("suggestions"):
                db.add(ResumeDiff(
                    resume_id=resume_id,
                    section="suggestions",
                    original="",
                    enhanced="",
                    changes=pipeline_result["suggestions"],
                ))

            if pipeline_result.get("outreach"):
                db.add(ResumeDiff(
                    resume_id=resume_id,
                    section="outreach",
                    original="",
                    enhanced="",
                    changes=[pipeline_result["outreach"]],
                ))

            scores_data = pipeline_result["scores"]
            db.add(Score(
                resume_id=resume_id,
                ai_readiness=scores_data["ai_readiness"],
                ats_score=scores_data["ats_score"],
                ai_terminology=scores_data["ai_terminology"],
                project_evidence=scores_data["project_evidence"],
                technical_depth=scores_data["technical_depth"],
                measurable_achievements=scores_data["measurable_achievements"],
                band=scores_data["band"],
            ))

            gaps = pipeline_result["gap_analysis"]
            db.add(GapAnalysis(
                resume_id=resume_id,
                missing_skills=gaps["missing_skills"],
                missing_projects=gaps["missing_projects"],
                missing_certifications=gaps["missing_certifications"],
                missing_frameworks=gaps.get("missing_frameworks", []),
            ))

            for q in pipeline_result["interview_questions"]:
                db.add(InterviewQuestion(
                    resume_id=resume_id,
                    category=q["category"],
                    question=q["question"],
                ))

            for p in pipeline_result["suggested_projects"]:
                db.add(Project(
                    resume_id=resume_id,
                    title=p["title"],
                    difficulty=p["difficulty"],
                    tech_stack=p["tech_stack"],
                    architecture=p["architecture"],
                    roadmap=p["roadmap"],
                    business_impact=p["business_impact"],
                ))

            await db.commit()

        except ResumeValidationError as e:
            resume.status = "failed"
            resume.current_step = e.message
            resume.progress = 0
            await db.commit()
        except Exception as e:
            logger.exception("Resume processing failed for %s", resume_id)
            resume.status = "failed"
            resume.current_step = str(e)
            resume.progress = 0
            await db.commit()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def process_resume_task(self, resume_id: str):
    try:
        _run_async(_process_resume_async(resume_id))
    except Exception as exc:
        raise self.retry(exc=exc)
