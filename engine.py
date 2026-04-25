"""
engine.py — Three-signal hybrid retrieval engine.

WHY THE OLD APPROACH UNDERPERFORMED
═════════════════════════════════════════════════════════════════════════════
The previous version used semantic embeddings alone (bi-encoder + cross-
encoder). That fails on two important query types:

1. CATEGORICAL / DEPARTMENT QUERIES — "math courses", "CS electives"
   Semantic models treat these as "courses about mathematical topics."
   Fourteen courses in our catalog contain the word "math*" somewhere in
   their text — CS, STAT, PHYS, SYS, DS courses all qualify — so a MATH
   course has no ranking advantage over them on semantic similarity alone.

2. KEYWORD QUERIES — "NLP transformers BERT", "SQL joins"
   When a user names a specific technology or acronym, a dense embedding
   averages that signal across 768 dimensions. BM25's exact-token matching
   handles these with much higher precision.

THE FIX: THREE-SIGNAL HYBRID
═════════════════════════════════════════════════════════════════════════════

  Signal 1 — Department alias boost  (rule-based, ~0 ms)
    Explicit map from common terms ("math", "cs", "econ") to course
    mnemonics. If the query references a department, courses in that
    department receive a strong multiplicative score boost. This is the
    single most important fix for categorical queries.

  Signal 2 — BM25  (rank_bm25, ~1 ms)
    Classic sparse keyword retrieval. Good at exact term matching, acronyms,
    and named technologies. We strip domain stop-words ("course", "courses",
    "class", "take") that appear across every document and would otherwise
    inflate IDF scores for irrelevant matches.

  Signal 3 — Bi-encoder (all-mpnet-base-v2, ~80 ms)
    Dense semantic retrieval. Captures paraphrases and synonyms BM25 misses.
    "I want something with proofs" → discrete math, algorithms, real analysis.

  Signal 4 — Cross-encoder re-ranking (ms-marco-MiniLM-L-6-v2, ~200 ms)
    Joint (query, document) attention. Most accurate signal but slowest;
    applied only to top-50 candidates from Signals 2+3.

  Final score = dept_boost × (w_bm25×bm25_norm + w_bi×bi_norm + w_cross×cross_norm)
  Weights: BM25 0.30 · bi-encoder 0.20 · cross-encoder 0.50

ON THE LOW CONFIDENCE NUMBERS (20–30%)
═════════════════════════════════════════════════════════════════════════════
Those numbers ARE a sign of underperformance, not normal behaviour.

The cross-encoder (ms-marco-MiniLM-L-6-v2) was trained on MS MARCO —
pairs of web search queries and Wikipedia/web passages. It learned to score
"does this web passage answer this web query?", not "is this course relevant?"
Its logits are calibrated for that task. When we sigmoid-normalise them on a
completely different domain, the raw scale means little.

More importantly, when the RANKING is wrong (DS1002 above MATH1310 for "math
courses"), the absolute numbers don't matter — the model is making a wrong
decision, not just expressing low confidence. That's fixed by adding BM25 and
department detection, which act as strong categorical priors the cross-encoder
lacks entirely.

After this fix you should see:
  • MATH courses ranking 1–5 for "math courses"
  • Final scores in the 0.50–0.85 range for good matches
  • Specific keyword queries (e.g. "NLP transformers") scoring > 0.70
═════════════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations

import os
import pickle
import re
from dataclasses import dataclass, field
from datetime import time as dtime
from typing import Optional

import numpy as np

try:
    from rank_bm25 import BM25Okapi
    _BM25_OK = True
except ImportError:
    _BM25_OK = False

try:
    from sentence_transformers import SentenceTransformer, CrossEncoder
    _ST_OK = True
except ImportError:
    _ST_OK = False

# ─────────────────────────────────────────────────────────────────────────────
# Models & weights
# ─────────────────────────────────────────────────────────────────────────────

BI_MODEL    = "all-mpnet-base-v2"
CROSS_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
INDEX_FILE  = os.path.join(os.path.dirname(__file__), ".index_mpnet.pkl")

W_BM25  = 0.30
W_BI    = 0.20
W_CROSS = 0.50

STAGE1_CANDIDATES = 50   # fed into cross-encoder

# Multiplicative bonus applied to courses whose mnemonic matches a detected
# department in the query. 2.5 is strong enough to dominate for categorical
# queries while still allowing cross-dept results when the query is ambiguous.
DEPT_BOOST = 2.5

# ─────────────────────────────────────────────────────────────────────────────
# Department alias map
# ─────────────────────────────────────────────────────────────────────────────

# Maps lowercase query tokens / phrases → set of course mnemonics to boost.
# Multi-word phrases are checked before single tokens.
DEPT_ALIASES: dict[str, set[str]] = {
    # Mathematics
    "math":           {"MATH"},
    "maths":          {"MATH"},
    "mathematics":    {"MATH"},
    "calculus":       {"MATH"},
    "linear algebra": {"MATH"},
    "differential equations": {"MATH"},
    # Computer Science
    "cs":             {"CS"},
    "compsci":        {"CS"},
    "computer science": {"CS"},
    # Data Science
    "ds":             {"DS"},
    "data science":   {"DS"},
    # Statistics
    "stat":           {"STAT"},
    "stats":          {"STAT"},
    "statistics":     {"STAT"},
    # Physics
    "phys":           {"PHYS"},
    "physics":        {"PHYS"},
    # Chemistry
    "chem":           {"CHEM"},
    "chemistry":      {"CHEM"},
    # Biology
    "bio":            {"BIOL"},
    "biology":        {"BIOL"},
    "biol":           {"BIOL"},
    # Economics
    "econ":           {"ECON"},
    "economics":      {"ECON"},
    # Psychology
    "psych":          {"PSYC"},
    "psychology":     {"PSYC"},
    "psyc":           {"PSYC"},
    # Philosophy
    "phil":           {"PHIL"},
    "philosophy":     {"PHIL"},
    # History
    "hist":           {"HIST"},
    "history":        {"HIST"},
    # Writing / English
    "writing":        {"ENWR"},
    "english":        {"ENWR"},
    "enwr":           {"ENWR"},
    # Engineering / ECE
    "ece":            {"ECE"},
    "electrical engineering": {"ECE"},
    "computer engineering":   {"ECE", "CS"},
    # Systems
    "sys":            {"SYS"},
    "systems engineering":    {"SYS"},
    # Commerce / Business
    "comm":           {"COMM"},
    "commerce":       {"COMM"},
    "business":       {"COMM"},
    "mcintire":       {"COMM"},
    # Sociology
    "soc":            {"SOC"},
    "sociology":      {"SOC"},
    # Environmental Science
    "evsc":           {"EVSC"},
    "environmental":  {"EVSC"},
    "environment":    {"EVSC"},
    # Public Policy
    "ppl":            {"PPL"},
    "policy":         {"PPL"},
}

# Phrases to check (longest first so "computer science" beats "computer")
_DEPT_PHRASES = sorted(DEPT_ALIASES.keys(), key=len, reverse=True)

# BM25 stop-words that are meaningless in a course catalog context
_BM25_STOP = {
    "course", "courses", "class", "classes", "take", "taking",
    "want", "need", "find", "good", "great", "best", "like",
    "looking", "something", "show", "me", "give", "recommend",
    "a", "an", "the", "i", "my", "is", "in", "for", "to", "of",
    "and", "or", "that", "this", "with", "are", "at", "uva",
}


# ─────────────────────────────────────────────────────────────────────────────
# Student profile
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class StudentProfile:
    major: str = "Undeclared"
    year: int = 1
    completed: list[str] = field(default_factory=list)
    busy_times: list[dict] = field(default_factory=list)
    career_goals: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "StudentProfile":
        return cls(
            major=d.get("major", "Undeclared"),
            year=d.get("year", 1),
            completed=d.get("completed", []),
            busy_times=d.get("busy_times", []),
            career_goals=d.get("career_goals", ""),
        )


# ─────────────────────────────────────────────────────────────────────────────
# Constraint solver
# ─────────────────────────────────────────────────────────────────────────────

def _t(s: str) -> dtime:
    h, m = s.split(":")
    return dtime(int(h), int(m))

def _overlap(a0: str, a1: str, b0: str, b1: str) -> bool:
    return _t(a0) < _t(b1) and _t(b0) < _t(a1)

def check_constraints(course: dict, profile: StudentProfile) -> tuple[bool, list[str]]:
    notes: list[str] = []

    if course["id"] in profile.completed:
        return False, ["Already completed."]

    missing = [p for p in course.get("prereqs", []) if p not in profile.completed]
    if missing:
        return False, [f"Missing prereq(s): {', '.join(missing)}"]

    sections = course.get("sections", [])
    if not sections:
        return True, ["No timetabled section — verify in SIS."]

    free, blocked = [], []
    for sec in sections:
        sec_days = set(sec["days"])
        conflict = any(
            sec_days & set(b["days"]) and _overlap(sec["start"], sec["end"], b["start"], b["end"])
            for b in profile.busy_times
        )
        (blocked if conflict else free).append(sec["section"])

    if free:
        if blocked:
            notes.append(
                f"Section(s) {', '.join(blocked)} conflict — "
                f"{', '.join(free)} available."
            )
        return True, notes
    return False, ["All sections conflict with your schedule."]


# ─────────────────────────────────────────────────────────────────────────────
# Result
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class CourseResult:
    course: dict
    bi_score: float
    bm25_score: float
    cross_score: float
    final_score: float
    dept_boosted: bool
    eligible: bool
    reasons: list[str]


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _tokenize(text: str) -> list[str]:
    """Lowercase word tokens, stripped of BM25 stop-words."""
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return [t for t in tokens if t not in _BM25_STOP]


def _detect_dept_mnemonics(query: str) -> set[str]:
    """
    Return the set of mnemonics hinted at by the query.
    Uses word-boundary regex so short aliases like 'cs' don't
    fire inside longer words like 'statistics' or 'physics'.
    Multi-word phrases are checked first (longest match wins).
    """
    q_lower = query.lower()
    matched: set[str] = set()
    for phrase in _DEPT_PHRASES:
        # Build a pattern: word boundary on each end, spaces between words
        escaped = re.escape(phrase)
        pattern = r"\b" + escaped + r"\b"
        if re.search(pattern, q_lower):
            matched.update(DEPT_ALIASES[phrase])
    return matched


def _minmax(arr: np.ndarray) -> np.ndarray:
    lo, hi = arr.min(), arr.max()
    if hi - lo < 1e-9:
        return np.ones_like(arr)
    return (arr - lo) / (hi - lo)


# ─────────────────────────────────────────────────────────────────────────────
# Recommender
# ─────────────────────────────────────────────────────────────────────────────

class CourseRecommender:

    def __init__(self):
        if not _ST_OK:
            raise ImportError("Run: pip install sentence-transformers")
        if not _BM25_OK:
            raise ImportError("Run: pip install rank-bm25")

        print(f"[INFO] Loading bi-encoder   : {BI_MODEL}")
        self.bi    = SentenceTransformer(BI_MODEL)
        print(f"[INFO] Loading cross-encoder: {CROSS_MODEL}")
        self.cross = CrossEncoder(CROSS_MODEL, max_length=512)

        self.courses: list[dict] = []
        self.embeddings: Optional[np.ndarray] = None
        self.bm25: Optional[BM25Okapi] = None

    # ── Document text ──────────────────────────────────────────────────────

    def _doc_text(self, course: dict) -> str:
        """
        Document text for embedding and BM25.

        The mnemonic and full department name are repeated prominently so
        that department-referential queries ("math courses") get strong
        signal from both BM25 (token match) and the bi-encoder.
        """
        mnem = course["mnemonic"]
        dept_names = {
            "CS": "Computer Science",
            "MATH": "Mathematics",
            "STAT": "Statistics",
            "DS": "Data Science",
            "ECE": "Electrical Computer Engineering",
            "PHYS": "Physics",
            "CHEM": "Chemistry",
            "BIOL": "Biology",
            "ECON": "Economics",
            "PSYC": "Psychology",
            "PHIL": "Philosophy",
            "ENWR": "English Writing",
            "HIST": "History",
            "COMM": "Commerce Business",
            "SOC": "Sociology",
            "EVSC": "Environmental Science",
            "PPL": "Public Policy",
            "SYS": "Systems Engineering",
        }
        dept_name = dept_names.get(mnem, mnem)
        tags = " ".join(course.get("tags", []))
        prereq_str = ", ".join(course.get("prereqs", [])) or "none"
        wl = course.get("workload_hrs_week", "")
        wl_str = f"Workload approximately {wl} hours per week." if wl else ""
        reviews = course.get("reviews", "")

        # Department name repeated 3× to give BM25 and the bi-encoder a
        # strong categorical anchor without drowning out the description.
        return (
            f"{course['title']}. "
            f"{mnem} {mnem} {dept_name} {dept_name} department. "
            f"Topics: {tags}. "
            f"{course['description']} "
            f"{wl_str} "
            f"Prerequisites: {prereq_str}. "
            f"Student notes: {reviews}"
        )

    # ── Query augmentation ─────────────────────────────────────────────────

    def _augment_query(self, raw: str, profile: StudentProfile) -> str:
        year_map = {1: "first-year student", 2: "sophomore",
                    3: "junior", 4: "senior"}
        yr = year_map.get(profile.year, "student")
        parts = []
        if profile.major and profile.major != "Undeclared":
            parts.append(f"I am a {yr} studying {profile.major}.")
        else:
            parts.append(f"I am a {yr}.")
        if profile.career_goals:
            parts.append(f"Career goal: {profile.career_goals}.")
        parts.append(raw)
        return " ".join(parts)

    # ── Index ──────────────────────────────────────────────────────────────

    def build_index(self, courses: list[dict], force: bool = False) -> None:
        self.courses = courses
        ids = [c["id"] for c in courses]

        # Always rebuild BM25 in memory (it's instant)
        doc_texts = [self._doc_text(c) for c in courses]
        self.bm25 = BM25Okapi([_tokenize(t) for t in doc_texts])

        # Load or build bi-encoder index
        if not force and os.path.exists(INDEX_FILE):
            print("[INFO] Loading cached index…")
            with open(INDEX_FILE, "rb") as f:
                cached = pickle.load(f)
            if cached.get("model") == BI_MODEL and cached.get("ids") == ids:
                self.embeddings = cached["embeddings"]
                print(f"[INFO] Index ready — {len(self.courses)} courses.")
                return
            print("[INFO] Cache mismatch — rebuilding…")

        print(f"[INFO] Embedding {len(courses)} courses with {BI_MODEL}…")
        self.embeddings = self.bi.encode(
            doc_texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=True,
            batch_size=32,
        )
        with open(INDEX_FILE, "wb") as f:
            pickle.dump({"model": BI_MODEL, "ids": ids,
                         "embeddings": self.embeddings}, f)
        print("[INFO] Index saved.")

    # ── Query ──────────────────────────────────────────────────────────────

    def query(
        self,
        raw_query: str,
        profile: StudentProfile,
        top_k: int = 5,
        show_ineligible: bool = False,
    ) -> list[CourseResult]:
        if self.embeddings is None or self.bm25 is None:
            raise RuntimeError("Call build_index() first.")

        augmented = self._augment_query(raw_query, profile)

        # ── Department detection ───────────────────────────────────────────
        dept_mnemonics = _detect_dept_mnemonics(raw_query)

        # ── Signal 1: BM25 ────────────────────────────────────────────────
        bm25_raw = np.array(
            self.bm25.get_scores(_tokenize(augmented)), dtype=np.float32
        )
        bm25_norm = _minmax(bm25_raw)

        # ── Signal 2: bi-encoder ──────────────────────────────────────────
        q_vec = self.bi.encode(
            augmented, convert_to_numpy=True, normalize_embeddings=True
        )
        bi_raw: np.ndarray = self.embeddings @ q_vec
        bi_norm = _minmax(bi_raw)

        # ── Blend signals 1+2, take top candidates for cross-encoder ──────
        combined = W_BM25 * bm25_norm + W_BI * bi_norm
        top_idx = np.argsort(combined)[::-1][:STAGE1_CANDIDATES]

        # ── Signal 3: cross-encoder ───────────────────────────────────────
        pairs = [(augmented, self._doc_text(self.courses[i])) for i in top_idx]
        raw_cross = self.cross.predict(pairs, show_progress_bar=False)
        cross_norm = 1.0 / (1.0 + np.exp(-raw_cross))   # sigmoid → [0,1]

        # Normalise within candidates so blend is fair
        bi_cand   = _minmax(bi_raw[top_idx])
        bm25_cand = _minmax(bm25_raw[top_idx])
        blended   = W_BM25 * bm25_cand + W_BI * bi_cand + W_CROSS * cross_norm

        # ── Department boost ──────────────────────────────────────────────
        if dept_mnemonics:
            for rank_pos, course_idx in enumerate(top_idx):
                if self.courses[course_idx]["mnemonic"] in dept_mnemonics:
                    blended[rank_pos] *= DEPT_BOOST
            # Re-normalise so scores stay in [0,1]
            blended = _minmax(blended)

        # ── Sort and apply constraints ─────────────────────────────────────
        order = np.argsort(blended)[::-1]

        eligible_results:   list[CourseResult] = []
        ineligible_results: list[CourseResult] = []

        for rank_pos in order:
            ci      = int(top_idx[rank_pos])
            course  = self.courses[ci]
            boosted = bool(dept_mnemonics and course["mnemonic"] in dept_mnemonics)
            eligible, reasons = check_constraints(course, profile)
            result = CourseResult(
                course       = course,
                bi_score     = float(bi_raw[ci]),
                bm25_score   = float(bm25_raw[ci]),
                cross_score  = float(cross_norm[rank_pos]),
                final_score  = float(blended[rank_pos]),
                dept_boosted = boosted,
                eligible     = eligible,
                reasons      = reasons,
            )
            (eligible_results if eligible else ineligible_results).append(result)

        if show_ineligible:
            return eligible_results[:top_k] + ineligible_results[:top_k]
        return eligible_results[:top_k]
