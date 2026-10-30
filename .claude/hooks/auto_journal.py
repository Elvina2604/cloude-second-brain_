#!/usr/bin/env python3
"""Хук Stop для Claude Code: автожурнал сессии без вызова LLM.

Читает JSON хука из stdin (transcript_path), берёт последний запрос пользователя
и последний текст ответа, маскирует типовые секреты, обрезает и дописывает
в brain/sessions/auto/ГГГГ-ММ-ДД.md. Молчит, если в проекте нет brain/brain.py.
"""
import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BRAIN = ROOT / "brain"
LIMIT = 1200
SECRETS = [
    (re.compile(r"(?i)(password|пароль|passwd|pwd|token|secret|api[_-]?key)(\s*[:=]\s*)\S+"), r"\1\2***"),
    (re.compile(r"PMAK-[A-Za-z0-9-]{10,}"), "PMAK-***"),
    (re.compile(r"gh[pousr]_[A-Za-z0-9]{10,}"), "gh*_***"),
    (re.compile(r"(?i)bearer\s+[A-Za-z0-9._\-]{10,}"), "Bearer ***"),
]


def clean(text: str) -> str:
    for pat, rep in SECRETS:
        text = pat.sub(rep, text)
    text = text.strip()
    return text if len(text) <= LIMIT else text[:LIMIT] + " …[обрезано]"


def text_of(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text")
    return ""


def main() -> int:
    if not (BRAIN / "brain.py").exists():
        return 0
    try:
        data = json.load(sys.stdin)
        lines = Path(data["transcript_path"]).read_text(encoding="utf-8").splitlines()
    except Exception:
        return 0
    last_user = last_assistant = ""
    for raw in lines:
        try:
            item = json.loads(raw)
        except json.JSONDecodeError:
            continue
        msg = item.get("message") or {}
        t = text_of(msg.get("content"))
        if not t.strip():
            continue
        if item.get("type") == "user" and not t.startswith("<"):
            last_user, last_assistant = t, ""
        elif item.get("type") == "assistant":
            last_assistant = t
    if not last_user:
        return 0
    now = dt.datetime.now()
    target = BRAIN / "sessions" / "auto" / f"{now:%Y-%m-%d}.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    head = "" if target.exists() else f"# Автожурнал {now:%Y-%m-%d}\n\nЧерновик хука Stop. Не источник истины.\n"
    with target.open("a", encoding="utf-8") as f:
        f.write(f"{head}\n## {now:%H:%M}\n**Запрос:** {clean(last_user)}\n\n**Ответ:** {clean(last_assistant)}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
