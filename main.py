#!/usr/bin/env python3
"""
main.py — CLI for the UVA Course Recommender (improved prototype).

Usage:
    python main.py                # interactive
    python main.py --demo         # run canned demo queries and exit
    python main.py --rebuild      # force-rebuild the embedding index
    python main.py --list         # print full course catalog and exit
"""

import argparse
import sys
import textwrap
from typing import Optional

from engine import CourseRecommender, StudentProfile, CourseResult
from catalog import COURSES, EXAMPLE_PROFILES

# ─────────────────────────────────────────────────────────────────────────────
# ANSI helpers
# ─────────────────────────────────────────────────────────────────────────────

_TTY = sys.stdout.isatty()

def _c(text: str, *codes: str) -> str:
    if not _TTY:
        return text
    return "".join(codes) + text + "\033[0m"

BOLD   = "\033[1m"
DIM    = "\033[2m"
ITALIC = "\033[3m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
CYAN   = "\033[36m"
RED    = "\033[31m"
BLUE   = "\033[34m"
MAGENTA = "\033[35m"
WHITE  = "\033[97m"


# ─────────────────────────────────────────────────────────────────────────────
# Banner
# ─────────────────────────────────────────────────────────────────────────────

def print_banner():
    print(_c(f"  UVA Course Recommender — {len(COURSES)} courses, {len(set(c['mnemonic'] for c in COURSES))} departments\n", BOLD))


# ─────────────────────────────────────────────────────────────────────────────
# Result display
# ─────────────────────────────────────────────────────────────────────────────

def _score_bar(score: float, width: int = 24) -> str:
    """Visual bar from score in [0,1]."""
    filled = max(1, round(score * width))
    empty  = width - filled
    bar = "█" * filled + "░" * empty
    if score >= 0.75:
        colour = GREEN
    elif score >= 0.50:
        colour = YELLOW
    else:
        colour = RED
    return _c(bar, colour)


def _stars(difficulty: int) -> str:
    filled = "★" * difficulty
    empty  = "☆" * (5 - difficulty)
    return _c(filled, YELLOW) + _c(empty, DIM)


def print_result(rank: int, r: CourseResult, verbose: bool = False) -> None:
    c = r.course

    # ── Header line ────────────────────────────────────────────────────────
    rank_str  = _c(f" {rank} ", BOLD, CYAN)
    title_str = _c(c["title"], BOLD, WHITE)
    code_str  = _c(f"{c['id']}", CYAN)
    credit_str = _c(f"{c['credits']} cr", DIM)
    print(f"\n  {rank_str}  {title_str}  {_c('·', DIM)}  {code_str}  {credit_str}")

    # ── Score bar ──────────────────────────────────────────────────────────
    bar  = _score_bar(r.final_score)
    pct  = _c(f"{r.final_score:.0%}", BOLD)
    sigs = _c(
        f"bm25:{r.bm25_score:.1f}  bi:{r.bi_score:.2f}  cross:{r.cross_score:.2f}",
        DIM
    )
    boost_tag = _c(" ★dept", MAGENTA) if r.dept_boosted else ""
    print(f"     Match  {bar}  {pct}{boost_tag}   {sigs}")

    # ── Difficulty & workload ──────────────────────────────────────────────
    diff_str = _stars(c.get("difficulty", 3))
    wl = c.get("workload_hrs_week")
    wl_str = _c(f"~{wl} hrs/wk", DIM) if wl else ""
    print(f"     Difficulty  {diff_str}   {wl_str}")

    # ── Sections ───────────────────────────────────────────────────────────
    sections = c.get("sections", [])
    for sec in sections:
        days_abbr = "/".join(d[:2] for d in sec["days"])
        instr = _c(sec.get("instructor", "TBA"), ITALIC)
        print(f"     {_c('§' + sec['section'], DIM)}  {days_abbr}  "
              f"{sec['start']}–{sec['end']}  {instr}")

    # ── Description ────────────────────────────────────────────────────────
    desc = textwrap.fill(
        c["description"], width=76,
        initial_indent="     ", subsequent_indent="     "
    )
    print(f"\n{_c(desc, DIM)}")

    # ── Tags ───────────────────────────────────────────────────────────────
    if verbose:
        tag_str = "  ".join(_c(t, BLUE) for t in c.get("tags", []))
        print(f"\n     {tag_str}")

    # ── Prereqs ────────────────────────────────────────────────────────────
    prereqs = c.get("prereqs", [])
    if prereqs:
        print(f"     {_c('Prereqs:', DIM)} {_c(', '.join(prereqs), YELLOW)}")

    # ── Student review snippet ─────────────────────────────────────────────
    review = c.get("reviews", "")
    if review:
        review_line = textwrap.fill(
            '💬  "' + review + '"',
            width=74, initial_indent="     ", subsequent_indent="        "
        )
        print(_c(review_line, ITALIC, DIM))

    # ── Constraint notes ───────────────────────────────────────────────────
    for note in r.reasons:
        print(f"     {_c('ℹ  ' + note, YELLOW)}")


def print_separator():
    print("\n" + _c("  " + "─" * 74, DIM))


# ─────────────────────────────────────────────────────────────────────────────
# Catalog listing
# ─────────────────────────────────────────────────────────────────────────────

def list_courses() -> None:
    from collections import defaultdict
    by_dept: dict[str, list] = defaultdict(list)
    for c in COURSES:
        by_dept[c["mnemonic"]].append(c)

    print(_c("\n  ── Full Course Catalog ──────────────────────────────────────────\n", BOLD))
    for dept in sorted(by_dept):
        print(f"  {_c(dept, CYAN, BOLD)}")
        for c in sorted(by_dept[dept], key=lambda x: x["number"]):
            prereq_str = f"  ← {', '.join(c['prereqs'])}" if c["prereqs"] else ""
            diff = "★" * c.get("difficulty", 3)
            print(f"    {c['id']:<14}  {c['title']:<48}  {c['credits']} cr  {diff}{prereq_str}")
        print()


# ─────────────────────────────────────────────────────────────────────────────
# Profile builder
# ─────────────────────────────────────────────────────────────────────────────

def _ask(prompt: str, default: str = "") -> str:
    disp = f"{prompt} [{_c(default, YELLOW)}]: " if default else f"{prompt}: "
    val = input(_c(disp, CYAN)).strip()
    return val or default


def _ask_yn(prompt: str, default: bool = True) -> bool:
    hint = "Y/n" if default else "y/N"
    raw = input(_c(f"{prompt} [{hint}]: ", CYAN)).strip().lower()
    if not raw:
        return default
    return raw.startswith("y")


def _parse_busy_block(raw: str) -> Optional[dict]:
    """
    Parse strings like:
        "Mon/Wed/Fri 09:00-10:00"
        "T/Th 14:00-15:30"
        "mwf 8:00-9:00"
    """
    day_map = {
        "m":"Mon","mo":"Mon","mon":"Mon","monday":"Mon",
        "t":"Tue","tu":"Tue","tue":"Tue","tuesday":"Tue",
        "w":"Wed","we":"Wed","wed":"Wed","wednesday":"Wed",
        "r":"Thu","th":"Thu","thu":"Thu","thursday":"Thu",
        "f":"Fri","fr":"Fri","fri":"Fri","friday":"Fri",
        "sa":"Sat","sat":"Sat","su":"Sun","sun":"Sun",
    }
    try:
        parts = raw.strip().split()
        if len(parts) == 1:
            # might be "MWF09:00-10:00" — split on first digit
            for i, ch in enumerate(raw):
                if ch.isdigit():
                    parts = [raw[:i], raw[i:]]
                    break
        days_raw, time_raw = parts[0], parts[1]
        # normalise days string: split on / or parse compact "mwf"
        if "/" in days_raw:
            day_tokens = days_raw.split("/")
        else:
            # compact: "mwf" → ["m","w","f"]  but "mon" → ["mon"]
            # Try known abbreviations first
            d_lower = days_raw.lower()
            if d_lower in day_map:
                day_tokens = [d_lower]
            else:
                # break into single chars
                day_tokens = list(d_lower)
        days = [day_map[d.lower()] for d in day_tokens if d.lower() in day_map]
        if not days:
            return None
        start, end = time_raw.split("-")
        # zero-pad if needed
        def zpad(t):
            h, m = t.split(":") if ":" in t else (t[:-2], t[-2:])
            return f"{int(h):02d}:{m.zfill(2)}"
        return {"days": days, "start": zpad(start), "end": zpad(end)}
    except Exception:
        return None


def build_profile_interactively() -> StudentProfile:
    print(_c("\n  ── Student Profile Setup ─────────────────────────────────────────\n", BOLD))

    major = _ask("  Major", "Computer Science")
    year_str = _ask("  Year (1=Freshman … 4=Senior)", "2")
    year = int(year_str) if year_str.isdigit() else 2

    print(_c("\n  Courses already completed — enter IDs separated by commas.", DIM))
    print(_c("  Example: CS1110, MATH1310, ENWR1510", DIM))
    raw_completed = _ask("  Completed", "")
    completed = [x.strip().upper() for x in raw_completed.split(",") if x.strip()]

    # Validate against catalog
    valid_ids = {c["id"] for c in COURSES}
    unknown = [x for x in completed if x not in valid_ids]
    if unknown:
        print(_c(f"  ⚠  Unrecognised IDs (ignored): {', '.join(unknown)}", YELLOW))
        completed = [x for x in completed if x in valid_ids]

    career_goals = _ask("\n  Career goals / interests (optional)", "")

    print(_c("\n  Busy time blocks — times when you are NOT available for class.", DIM))
    print(_c("  Format: Mon/Wed/Fri 09:00-10:00   or   T/Th 14:00-15:30", DIM))
    busy_times: list[dict] = []
    while True:
        raw = input(_c("  Add block (Enter to skip/finish): ", CYAN)).strip()
        if not raw:
            break
        block = _parse_busy_block(raw)
        if block:
            busy_times.append(block)
            days_str = "/".join(block["days"])
            print(f"    {_c('✓', GREEN)} {days_str}  {block['start']}–{block['end']}")
        else:
            print(_c("    ✗  Couldn't parse — try: Mon/Wed 09:00-10:00", RED))

    profile = StudentProfile(major=major, year=year, completed=completed,
                             busy_times=busy_times, career_goals=career_goals)
    print(_c("\n  Profile saved.\n", GREEN))
    return profile


# ─────────────────────────────────────────────────────────────────────────────
# Search loop
# ─────────────────────────────────────────────────────────────────────────────

HELP = """
  Commands
  ────────────────────────────────────────────────────────────────────
  <query>        Natural-language search for courses
  top <n>        Change number of results shown (default 5)
  verbose        Toggle verbose tag display
  profile        Rebuild your student profile
  list           Show full course catalog
  help           Show this message
  quit / exit    Exit

  Query tips
  ────────────────────────────────────────────────────────────────────
  • Topic-driven:   "I want to learn machine learning and use PyTorch"
  • Career-driven:  "classes that help me get a job in cybersecurity"
  • Honest:         "something not too hard that fulfills a requirement"
  • Specific:       "NLP course covering transformers and BERT"
  • Mixed:          "stats-heavy course that also involves programming"

  Your major and completed courses are automatically factored in.
"""


def search_loop(rec: CourseRecommender, profile: StudentProfile) -> None:
    top_k = 5
    verbose = False

    print(_c("\n  Type a description of what you're looking for.", BOLD))
    print(_c("  Type 'help' for commands.\n", DIM))

    while True:
        try:
            raw = input(_c("  🔍  ", BOLD, CYAN)).strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Goodbye!")
            sys.exit(0)

        if not raw:
            continue

        lower = raw.lower()

        if lower in ("quit", "exit", "q"):
            print("  Goodbye!")
            sys.exit(0)
        elif lower == "help":
            print(_c(HELP, DIM))
        elif lower == "list":
            list_courses()
        elif lower == "verbose":
            verbose = not verbose
            print(_c(f"  Verbose mode {'on' if verbose else 'off'}.", DIM))
        elif lower.startswith("top "):
            try:
                top_k = int(lower.split()[1])
                print(_c(f"  Showing top {top_k} results.", DIM))
            except (IndexError, ValueError):
                print(_c("  Usage: top <number>", RED))
        elif lower == "profile":
            profile = build_profile_interactively()
        else:
            # ── Run the two-stage retrieval ────────────────────────────────
            print(_c("\n  Retrieving…\n", DIM))
            results = rec.query(raw, profile, top_k=top_k)

            if not results:
                print(_c(
                    "  No eligible courses found matching that query.\n"
                    "  Try broadening the description, or type 'profile' to update\n"
                    "  your completed courses / schedule constraints.", YELLOW))
                continue

            label = f"Top {len(results)} results" if len(results) > 1 else "Best result"
            print(_c(f"\n  {label} for: \"{raw}\"\n", BOLD))

            for i, r in enumerate(results, 1):
                print_result(i, r, verbose=verbose)
            print_separator()
            print()


# ─────────────────────────────────────────────────────────────────────────────
# Demo mode
# ─────────────────────────────────────────────────────────────────────────────

DEMO_RUNS = [
    (
        "Alex — CS Junior",
        EXAMPLE_PROFILES[0],
        [
            "I want to learn about NLP, transformers, and large language models",
            "a hard theory course, I enjoy proofs and abstract math",
            "build a full web application and ship it — team project preferred",
        ],
    ),
    (
        "Jordan — DS Sophomore",
        EXAMPLE_PROFILES[1],
        [
            "practical machine learning on real datasets, Python preferred",
            "something combining data science with environmental or climate topics",
        ],
    ),
    (
        "Sam — Undeclared Freshman",
        EXAMPLE_PROFILES[2],
        [
            "intro to coding, never programmed before",
            "understand the ethics of AI and technology, no tech background needed",
        ],
    ),
    (
        "Riley — Pre-med Sophomore",
        EXAMPLE_PROFILES[3],
        [
            "computational approaches to biology and genomics",
            "quantitative research methods with statistics",
        ],
    ),
]


def run_demo(rec: CourseRecommender) -> None:
    print(_c("\n  ══ DEMO MODE ══════════════════════════════════════════════════════\n", BOLD, CYAN))

    for student_name, prof_dict, queries in DEMO_RUNS:
        profile = StudentProfile.from_dict(prof_dict)
        print(_c(f"  ── {student_name} ──────────────────────────────────────────", BOLD))
        print(f"     Major: {profile.major}  |  Year: {profile.year}")
        print(f"     Completed: {', '.join(profile.completed[:6])}{'…' if len(profile.completed) > 6 else ''}")
        print()

        for query in queries:
            print(_c(f"  Query: \"{query}\"", BOLD, WHITE))
            results = rec.query(query, profile, top_k=3)
            for i, r in enumerate(results, 1):
                print_result(i, r)
            print_separator()
            print()


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="UVA Course Recommender — semantic search prototype",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--demo",    action="store_true", help="Run demo queries and exit.")
    parser.add_argument("--rebuild", action="store_true", help="Force rebuild embedding index.")
    parser.add_argument("--list",    action="store_true", help="Print catalog and exit.")
    args = parser.parse_args()

    print_banner()

    if args.list:
        list_courses()
        return

    rec = CourseRecommender()
    rec.build_index(COURSES, force=args.rebuild)

    if args.demo:
        run_demo(rec)
        return

    # ── Interactive: pick or build a profile ──────────────────────────────
    print(_c("  Choose a starting profile:\n", BOLD))
    for i, p in enumerate(EXAMPLE_PROFILES, 1):
        comp_preview = ", ".join(p["completed"][:4]) + ("…" if len(p["completed"]) > 4 else "")
        print(f"    [{i}] {_c(p['name'], CYAN)}  —  {p['major']}, Year {p['year']}")
        if comp_preview:
            print(f"        Completed: {_c(comp_preview, DIM)}")
    print(f"    [{len(EXAMPLE_PROFILES)+1}] {_c('Build my own profile', YELLOW)}")
    print()

    choice = input(_c(f"  Choice [1–{len(EXAMPLE_PROFILES)+1}]: ", CYAN)).strip()
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(EXAMPLE_PROFILES):
            profile = StudentProfile.from_dict(EXAMPLE_PROFILES[idx])
            print(_c(f"\n  Loaded: {EXAMPLE_PROFILES[idx]['name']}\n", GREEN))
        else:
            profile = build_profile_interactively()
    except (ValueError, IndexError):
        profile = build_profile_interactively()

    search_loop(rec, profile)


if __name__ == "__main__":
    main()
