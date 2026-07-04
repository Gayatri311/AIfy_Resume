def validate_authenticity(original_bullet: str, enhanced_bullet: str) -> str:
    if original_bullet.strip().rstrip(".") == enhanced_bullet.strip().rstrip("."):
        return "SAFE"

    from app.agents.resume_quality import is_vague_bullet

    unverifiable_terms = [
        "fine-tuned model", "trained a model", "published paper",
        "phd", "patent", "from scratch neural",
    ]
    if any(t in enhanced_bullet.lower() for t in unverifiable_terms):
        return "UNVERIFIABLE"

    # Thin or duty-list bullets — allow substantial modernization
    if is_vague_bullet(original_bullet):
        return "SAFE"

    orig_words = {w.lower() for w in original_bullet.split() if len(w) > 3}
    enh_words = enhanced_bullet.lower()
    overlap = sum(1 for w in orig_words if w in enh_words)
    if overlap >= max(1, len(orig_words) // 3):
        return "SAFE"

    return "STRETCH"


def filter_enhancements(original, enhanced, changes: list) -> tuple:
    from copy import deepcopy

    filtered = deepcopy(enhanced)
    valid_changes = []

    for exp_orig, exp_enh in zip(original.experience, filtered.experience):
        new_bullets = []
        for orig_b, enh_b in zip(exp_orig.bullets, exp_enh.bullets):
            auth = validate_authenticity(orig_b, enh_b)
            if auth == "UNVERIFIABLE":
                new_bullets.append(orig_b)
            else:
                new_bullets.append(enh_b)
        exp_enh.bullets = new_bullets

    for change in changes:
        if change.get("authenticity") != "UNVERIFIABLE":
            valid_changes.append(change)

    return filtered, valid_changes
