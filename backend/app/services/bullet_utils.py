"""Normalize and split resume bullet points."""

import re

BULLET_PREFIX = re.compile(r"^[\u2022\-\*•●▪◦]\s*")
INLINE_BULLET_SPLIT = re.compile(r"\s*[\u2022•●▪]\s+")
NEWLINE_BULLET_SPLIT = re.compile(r"\n\s*[\u2022\-\*•●▪◦]\s*")


def strip_bullet_prefix(text: str) -> str:
    return BULLET_PREFIX.sub("", text.strip()).strip()


def is_bullet_line(line: str) -> bool:
    return bool(BULLET_PREFIX.match(line.strip())) or line.strip().startswith(("•", "-", "*", "●"))


def split_inline_bullets(text: str) -> list[str]:
    """Split a single line that contains multiple inline bullet markers."""
    text = text.strip()
    if not text:
        return []

    if INLINE_BULLET_SPLIT.search(text):
        parts = INLINE_BULLET_SPLIT.split(text)
        return [strip_bullet_prefix(p) for p in parts if strip_bullet_prefix(p)]

    if NEWLINE_BULLET_SPLIT.search(text):
        parts = NEWLINE_BULLET_SPLIT.split(text)
        return [strip_bullet_prefix(p) for p in parts if strip_bullet_prefix(p)]

    return [strip_bullet_prefix(text)]


def split_merged_accomplishments(text: str) -> list[str]:
    """Split a paragraph that should have been multiple resume bullets."""
    from app.services.text_cleanup import ACCOMPLISHMENT_SPLIT

    text = strip_bullet_prefix(text.strip())
    if not text:
        return []

    if len(text) < 120 and not ACCOMPLISHMENT_SPLIT.search(text):
        return [text]

    parts = [p.strip() for p in ACCOMPLISHMENT_SPLIT.split(text) if p.strip()]
    if len(parts) > 1:
        return parts

    inline = split_inline_bullets(text)
    if len(inline) > 1:
        return inline

    return [text]


CONTINUATION_FRAGMENT = re.compile(
    r"^(?:and|or|with|for|to|via|using|including|while|as|through|across|among|"
    r"within|without|such|that|which|where|when|by|from|into|between|during)\b",
    re.I,
)


def _looks_like_continuation_fragment(text: str) -> bool:
    t = text.strip()
    if not t:
        return False
    if t[0].islower():
        return True
    return bool(CONTINUATION_FRAGMENT.match(t))


def merge_continuation_fragments(bullets: list[str]) -> list[str]:
    """Rejoin bullets that were split mid-sentence (e.g. after a comma wrap)."""
    merged: list[str] = []
    for bullet in bullets:
        clean = strip_bullet_prefix((bullet or "").strip())
        if not clean:
            continue
        if merged and _looks_like_continuation_fragment(clean):
            merged[-1] = f"{merged[-1].rstrip()} {clean.lstrip()}"
        else:
            merged.append(clean)
    return merged


def normalize_bullet_list(bullets: list[str]) -> list[str]:
    """Ensure one accomplishment per bullet; split merged or inline bullets."""
    normalized: list[str] = []
    for raw in bullets:
        for part in split_inline_bullets(raw):
            clean = strip_bullet_prefix(part)
            if not clean:
                continue
            for merged in split_merged_accomplishments(clean):
                if merged and merged not in normalized:
                    normalized.append(merged)
    return merge_continuation_fragments(normalized)


def expand_raw_lines(text: str) -> list[str]:
    """Expand extracted document text into one line per logical item."""
    expanded: list[str] = []
    for raw in text.split("\n"):
        line = raw.strip()
        if not line:
            continue
        if is_bullet_line(line):
            expanded.append(line)
            continue
        if INLINE_BULLET_SPLIT.search(line) and line.count("•") + line.count("●") > 0:
            for part in split_inline_bullets(line):
                expanded.append(f"• {part}")
            continue
        expanded.append(line)
    return expanded
