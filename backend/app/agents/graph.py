"""LangGraph workflow for resume processing pipeline.

When OPENAI_API_KEY or ANTHROPIC_API_KEY is configured, agents can be
upgraded to use LLM-powered nodes. The default pipeline uses deterministic
rule-based agents for reliability and authenticity validation.
"""

from typing import TypedDict
from app.schemas.resume import ResumeData


class PipelineState(TypedDict):
    file_path: str
    original: dict
    enhanced: dict
    ats_result: dict
    scores: dict
    gaps: dict
    projects: list
    questions: list
    diffs: list
    changes: list
    step: str
    progress: int


def build_resume_graph():
    """Build LangGraph workflow — extensible for LLM nodes."""
    try:
        from langgraph.graph import StateGraph, END

        from app.services.pipeline import run_pipeline

        def parse_node(state: PipelineState) -> PipelineState:
            result = run_pipeline(state["file_path"])
            return {
                **state,
                **result,
                "step": "complete",
                "progress": 100,
            }

        graph = StateGraph(PipelineState)
        graph.add_node("process", parse_node)
        graph.set_entry_point("process")
        graph.add_edge("process", END)
        return graph.compile()
    except ImportError:
        return None


resume_graph = build_resume_graph()
