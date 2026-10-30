#!/usr/bin/env python3
"""Второй мозг для Claude: CLI по файловой базе знаний brain/.

Только стандартная библиотека Python 3.10+. Запуск:
    py -3 brain/brain.py <команда>      (Windows)
    python3 brain/brain.py <команда>    (Linux/macOS)

Команды базы знаний:
    brief                 STATE + последняя сессия + карта базы
    pack "задача"         минимальный контекст под задачу (по умолчанию ≤ 7000 символов)
    search "термин"       поиск по секциям: BM25 + префиксы + синонимы из GLOSSARY
    note "мысль"          быстро записать в inbox.md
    new-session           создать журнал sessions/ГГГГ-ММ-ДД.md по шаблону
    lint                  frontmatter, ссылки, размеры, секреты
    stats                 размеры файлов

Команды для тестирования выборок (по references/selections-test-map.md):
    checks [--section 4] [--priority P1] [--type UI] [--grep текст]
    defects [--grep текст]
    api [--grep текст]
    questions             открытые вопросы карты
"""
from __future__ import annotations

import argparse
import datetime as dt
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEST_MAP = ROOT / "references" / "selections-test-map.md"
REQUIRED_FM = ("title", "summary", "tags", "updated")
LIMITS = {"STATE.md": 60, "areas": 300, "sessions": 80}
SKIP_DIRS = {"auto"}
LOW_WEIGHT = {"GLOSSARY.md", "INDEX.md"}  # навигация: находить, но не ставить выше содержательных файлов
SECRET_PATTERNS = [
    re.compile(r"(?i)(password|пароль|passwd|pwd)\s*[:=]\s*\S+"),
    re.compile(r"(?i)(api[_-]?key|token|secret|bearer)\s*[:=]\s*[A-Za-z0-9_\-\.]{8,}"),
    re.compile(r"PMAK-[A-Za-z0-9]{20,}"),  # Postman API key
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),   # GitHub token
]
WORD = re.compile(r"[0-9A-Za-zА-Яа-яЁё_\-]+")
STOP = set("и в во не на с со по к ко о об от до из за для что как это или а но же ли бы the a an of to in for and or".split())


# ---------------------------------------------------------------- утилиты
def out(text: str = "") -> None:
    print(text)


def md_files(include_auto: bool = False):
    for p in sorted(ROOT.rglob("*.md")):
        rel = p.relative_to(ROOT)
        if not include_auto and any(part in SKIP_DIRS for part in rel.parts):
            continue
        yield p


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    fm = {}
    for line in text[3:end].strip().splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm, text[end + 4:].lstrip("\n")


def stem(word: str) -> str:
    """Грубая основа слова: первые 5 букв (хватает для русской морфологии в поиске)."""
    w = word.lower().replace("ё", "е")
    return w[:5] if len(w) > 5 else w


def tokens(text: str) -> list[str]:
    return [stem(w) for w in WORD.findall(text) if w.lower() not in STOP and len(w) > 1]


def sections(path: Path) -> list[tuple[str, str]]:
    """Делит файл на секции по заголовкам ## и ###."""
    _, body = frontmatter(read(path))
    parts, title, buf = [], path.stem, []
    for line in body.splitlines():
        if re.match(r"^#{1,3} ", line):
            if buf and "".join(buf).strip():
                parts.append((title, "\n".join(buf).strip()))
            title, buf = line.lstrip("# ").strip(), [line]
        else:
            buf.append(line)
    if buf and "".join(buf).strip():
        parts.append((title, "\n".join(buf).strip()))
    return parts


def synonyms() -> dict[str, set[str]]:
    """Синонимы из таблицы GLOSSARY.md: | Термин | Значение | Синонимы |."""
    g = ROOT / "GLOSSARY.md"
    result: dict[str, set[str]] = {}
    if not g.exists():
        return result
    for line in read(g).splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3 or cells[0] in ("Термин", "---", "") or set(cells[0]) <= {"-"}:
            continue
        group = {stem(w) for w in WORD.findall(cells[0] + " " + cells[2])}
        for s in group:
            result.setdefault(s, set()).update(group)
    return result


# ---------------------------------------------------------------- поиск
def build_index():
    docs = []
    for p in md_files():
        if "templates" in p.parts:
            continue
        for title, text in sections(p):
            docs.append((p.relative_to(ROOT).as_posix(), title, text, tokens(title + " " + text)))
    return docs


def query_terms(query: str) -> dict[str, float]:
    """Слова запроса (вес 1) и их синонимы из GLOSSARY (вес 0.4)."""
    syn = synonyms()
    q: dict[str, float] = {}
    for t in tokens(query):
        for s in syn.get(t, ()):
            q.setdefault(s, 0.4)
        q[t] = 1.0
    return q


def focus_text(text: str, query: str, limit: int = 1500) -> str:
    """Длинный раздел: заголовок, шапка таблицы и только строки со словами запроса."""
    if len(text) <= limit:
        return text
    q = set(tokens(query))
    lines = text.splitlines()
    keep = [lines[0]]
    for i, line in enumerate(lines[1:], 1):
        is_header = line.startswith("|") and i + 1 < len(lines) and set(lines[i + 1].replace("|", "").strip()) <= {"-", ":", " "} and lines[i + 1].strip()
        if is_header or set(tokens(line)) & q:
            keep.append(line)
            if is_header:
                keep.append(lines[i + 1])
    return "\n".join(keep)


def search_docs(query: str, limit: int = 8):
    docs = build_index()
    if not docs:
        return []
    q = query_terms(query)
    n = len(docs)
    avg = sum(len(d[3]) for d in docs) / n
    df = {t: sum(1 for d in docs if t in d[3]) for t in q}
    scored = []
    for path, title, text, toks in docs:
        score = 0.0
        tl = len(toks) or 1
        title_toks = set(tokens(title))
        for t in q:
            f = toks.count(t)
            if not f:
                continue
            idf = math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5))
            score += q[t] * idf * f * 2.2 / (f + 1.2 * (0.25 + 0.75 * tl / avg))
            if t in title_toks:
                score += 1.5 * q[t]
        if path in LOW_WEIGHT:
            score *= 0.3
        elif path.startswith("areas/"):
            score *= 1.3  # отобранные знания важнее справочника
        if score > 0:
            scored.append((score, path, title, text))
    scored.sort(key=lambda x: -x[0])
    return scored[:limit]


# ---------------------------------------------------------------- команды базы
def cmd_brief(_args) -> int:
    state = ROOT / "STATE.md"
    if state.exists():
        out(frontmatter(read(state))[1])
    sess = sorted((ROOT / "sessions").glob("????-??-??.md"))
    if sess:
        out(f"\n=== Последняя сессия: {sess[-1].relative_to(ROOT).as_posix()} ===")
        out(frontmatter(read(sess[-1]))[1][:2500])
    out("\n=== Карта базы ===")
    for p in md_files():
        if "templates" in p.parts or p.parent.name == "sessions":
            continue
        fm, _ = frontmatter(read(p))
        out(f"- {p.relative_to(ROOT).as_posix()} — {fm.get('summary', '')}")
    return 0


def cmd_search(args) -> int:
    hits = search_docs(args.query, args.limit)
    if not hits:
        out("Ничего не найдено. Запишите знание: areas/, DECISIONS.md или inbox.md (команда note).")
        return 1
    for score, path, title, text in hits:
        first = next((l for l in text.splitlines()[1:] if l.strip()), "")[:160]
        out(f"{score:5.1f}  {path} § {title}\n       {first}")
    return 0


def cmd_pack(args) -> int:
    budget = args.budget
    parts = []
    state = ROOT / "STATE.md"
    if state.exists():
        body = frontmatter(read(state))[1]
        focus = body.split("## Открытые", 1)[0]
        parts.append(f"=== STATE.md (фокус) ===\n{focus.strip()}")
    used = sum(len(p) for p in parts)
    files = set()
    for score, path, title, text in search_docs(args.task, 12):
        if len(files | {path}) > args.max_files:
            continue
        chunk = f"\n=== {path} § {title} ===\n{focus_text(text, args.task)}"
        if used + len(chunk) > budget:
            chunk = chunk[: max(0, budget - used)]
            if len(chunk) < 200:
                break
        parts.append(chunk)
        files.add(path)
        used += len(chunk)
        if used >= budget:
            break
    out("\n".join(parts))
    out(f"\n--- {used} симв., файлов: {len(files)}. Дальше — search или чтение нужного раздела.")
    return 0


def cmd_note(args) -> int:
    inbox = ROOT / "inbox.md"
    stamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    with inbox.open("a", encoding="utf-8") as f:
        f.write(f"\n- {stamp} {args.text}")
    out(f"Записано в {inbox.relative_to(ROOT).as_posix()}")
    return 0


def cmd_new_session(_args) -> int:
    today = dt.date.today().isoformat()
    target = ROOT / "sessions" / f"{today}.md"
    if target.exists():
        out(f"Уже есть: sessions/{today}.md")
        return 0
    tpl = read(ROOT / "templates" / "session.md")
    _, body = frontmatter(tpl)
    text = (f"---\ntitle: {today}\nsummary: Журнал сессии {today}.\ntags: [session]\n"
            f"updated: {today}\n---\n\n" + body.replace("YYYY-MM-DD", today))
    target.write_text(text, encoding="utf-8")
    out(f"Создано: sessions/{today}.md")
    return 0


def cmd_lint(_args) -> int:
    errors, warns = [], []
    for p in md_files(include_auto=False):
        rel = p.relative_to(ROOT).as_posix()
        text = read(p)
        fm, body = frontmatter(text)
        if "references" not in p.parts:
            miss = [k for k in REQUIRED_FM if k not in fm]
            if miss:
                errors.append(f"{rel}: нет полей frontmatter {', '.join(miss)}")
        for m in re.finditer(r"\]\(([^)#\s]+\.md)(#[^)]*)?\)", body):
            if not (p.parent / m.group(1)).resolve().exists():
                errors.append(f"{rel}: битая ссылка {m.group(1)}")
        lines = len(body.splitlines())
        limit = LIMITS.get(p.name) or next((v for k, v in LIMITS.items() if k in p.parts), None)
        if limit and lines > limit:
            warns.append(f"{rel}: {lines} строк (лимит ~{limit}) — разбить")
        for pat in SECRET_PATTERNS:
            if pat.search(body):
                errors.append(f"{rel}: похоже на секрет ({pat.pattern[:30]}…) — удалить")
    for w in warns:
        out(f"WARN  {w}")
    for e in errors:
        out(f"ERROR {e}")
    out(f"lint: ошибок {len(errors)}, предупреждений {len(warns)}")
    return 1 if errors else 0


def cmd_stats(_args) -> int:
    total = 0
    for p in md_files(include_auto=True):
        n = len(read(p))
        total += n
        out(f"{n:7d}  {p.relative_to(ROOT).as_posix()}")
    out(f"{total:7d}  всего")
    return 0


# ---------------------------------------------------------------- карта тестирования
def table_rows():
    """Строки таблиц карты: (раздел, ячейки, заголовки)."""
    if not TEST_MAP.exists():
        out(f"Нет файла {TEST_MAP.relative_to(ROOT)}")
        return
    section, header = "", []
    for line in read(TEST_MAP).splitlines():
        if line.startswith("#"):
            section = line.lstrip("# ").strip()
            header = []
            continue
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if all(set(c) <= {"-", ":", " "} for c in cells):
            continue
        if not header:
            header = cells
            continue
        yield section, cells, header


def match(cells, grep):
    return not grep or grep.lower() in " ".join(cells).lower()


def cmd_checks(args) -> int:
    n = 0
    for section, cells, header in table_rows():
        num = cells[0]
        if not re.match(r"^\d+(\.\d+)*$", num):
            continue
        if args.section and not (num == args.section or num.startswith(args.section + ".")):
            continue
        if args.priority and args.priority.upper() not in [c.upper() for c in cells]:
            continue
        if args.type and not any(args.type.upper() in c.upper() for c in cells[-1:]):
            continue
        if not match(cells, args.grep):
            continue
        out(f"{num:8} {' | '.join(cells[1:])}")
        n += 1
    out(f"--- проверок: {n}")
    return 0


def cmd_defects(args) -> int:
    n = 0
    for section, cells, header in table_rows():
        if re.match(r"^Д-\d+$", cells[0]) and match(cells, args.grep):
            out(f"{cells[0]:5} {cells[1]}\n      где: {cells[2]}\n      ожидалось: {cells[3]} [{cells[-1]}]")
            n += 1
    out(f"--- подозрений на дефекты: {n}")
    return 0


def cmd_api(args) -> int:
    n = 0
    for section, cells, header in table_rows():
        if section.startswith("13.4") and match(cells, args.grep):
            out(f"{cells[0]}.{cells[1]} — {cells[2]}\n      проверить: {cells[3]} [{cells[4]}]")
            n += 1
    out(f"--- публичных методов: {n}")
    return 0


def cmd_questions(_args) -> int:
    text = read(TEST_MAP)
    part = text.split("Открытые вопросы", 1)[-1]
    for line in part.splitlines():
        if re.match(r"^\s*[-*] \[ \]", line):
            out(line.strip())
    return 0


# ---------------------------------------------------------------- main
def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(prog="brain.py", description="Второй мозг: CLI базы знаний brain/")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("brief").set_defaults(fn=cmd_brief)
    p = sub.add_parser("pack"); p.add_argument("task"); p.add_argument("--budget", type=int, default=7000)
    p.add_argument("--max-files", type=int, default=4); p.set_defaults(fn=cmd_pack)
    p = sub.add_parser("search"); p.add_argument("query"); p.add_argument("--limit", type=int, default=8)
    p.set_defaults(fn=cmd_search)
    p = sub.add_parser("note"); p.add_argument("text"); p.set_defaults(fn=cmd_note)
    sub.add_parser("new-session").set_defaults(fn=cmd_new_session)
    sub.add_parser("lint").set_defaults(fn=cmd_lint)
    sub.add_parser("stats").set_defaults(fn=cmd_stats)
    p = sub.add_parser("checks"); p.add_argument("--section"); p.add_argument("--priority")
    p.add_argument("--type"); p.add_argument("--grep"); p.set_defaults(fn=cmd_checks)
    p = sub.add_parser("defects"); p.add_argument("--grep"); p.set_defaults(fn=cmd_defects)
    p = sub.add_parser("api"); p.add_argument("--grep"); p.set_defaults(fn=cmd_api)
    sub.add_parser("questions").set_defaults(fn=cmd_questions)
    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
