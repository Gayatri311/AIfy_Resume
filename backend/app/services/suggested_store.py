import json
import os
from typing import Optional
from app.core.config import get_settings

settings = get_settings()


def _path(resume_id: str) -> str:
    os.makedirs(settings.upload_dir, exist_ok=True)
    return os.path.join(settings.upload_dir, f"{resume_id}_suggested.json")


def save_suggested(resume_id: str, data: dict) -> None:
    with open(_path(resume_id), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_suggested(resume_id: str) -> Optional[dict]:
    path = _path(resume_id)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)
