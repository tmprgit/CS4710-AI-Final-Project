"""
engine.py — Two-stage semantic retrieval engine.

ARCHITECTURE
════════════════════════════════════════════════════════════════════════════════

Stage 1 — Bi-encoder retrieval   (all-mpnet-base-v2, ~420 MB)
  Each course is encoded into a dense vector once and cached.  At query time
  the user's (augmented) query is encoded in ~80 ms, and cosine similarity
  is computed against every course vector with a single matrix multiply.
  This gives us the top-50 candidates very quickly.

  Why mpnet over MiniLM-L6?
    • MiniLM-L6 scores ~63 on MTEB semantic similarity benchmarks.
    • all-mpnet-base-v2 scores ~69 — a significant jump.
    • Both run comfortably on CPU / Apple M1 Silicon.
    • mpnet uses a full 768-dim representation vs MiniLM's 384-dim.

Stage 2 — Cross-encoder re-ranking   (cross-encoder/ms-marco-MiniLM-L-6-v2, ~80 MB)
  A cross-encoder reads the *concatenation* of (query, course_text) together,
  attending to both jointly.  This is far more accurate than the independent
  bi-encoder embeddings because it can model fine-grained interactions between
  query words and document words.
  The trade-off: it must run once per candidate pair, so we only apply it to
  the top-50 from Stage 1.  Final scores are a blend of the two.

Query augmentation
  The student's major, year, and career goals (if stated) are appended to the
  raw query before encoding.  This steers the embedding toward domain-relevant
  courses without requiring users to mention their major every time.

Document text construction
  Each course is represented as a single rich string:
      "<title>. <mnemonic><number>. <tags>. <description>. Student notes: <reviews>."
  Including the student-review snippet surfaces colloquial language (e.g.
  "interview prep", "real-world projects") that may match user queries more
  naturally than formal catalogue prose.

Score normalization
  Cross-encoder logits are passed through sigmoid → [0,1].
  Final score = 0.35 * cosine_sim + 0.65 * sigmoid(cross_score).
  The cross-encoder gets higher weight because it's more accurate; the
  bi-encoder score provides a useful tiebreaker among close candidates.

════════════════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations

import os
import pickle
from dataclasses import dataclass, field
from datetime import time as dtime
from typing import Optional

import numpy as np

try:
    from sentence_transformers import SentenceTransformer, CrossEncoder
    _ST_OK = True
except ImportError:
    _ST_OK = False

# ─────────────────────────────────────────────────────────────────────────────
# Models
# ─────────────────────────────────────────────────────────────────────────────

BI_ENCODER_MODEL   = "all-mpnet-base-v2"          # ~420 MB, 768-dim
CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"  # ~80 MB

INDEX_FILE = os.path.join(os.path.dirname(__file__), ".index_mpnet.pkl")

# Blend weights (must sum to 1.0)
BI_WEIGHT    = 0.30
CROSS_WEIGHT = 0.70

# Retrieve this many candidates from Stage 1 before re-ranking
STAGE1_CANDIDATES = 60


# ─────────────────────────────────────────────────────────────────────────────
# Student profile
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class StudentProfile:
    major: str = "Undeclared"
    year: int = 1
    completed: list[str] = field(default_factory=list)
    busy_times: list[dict] = field(default_factory=list)
    career_goals: str = ""   # optional free text, e.g. "work in AI industry"

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


def _overlap(a0, a1, b0, b1) -> bool:
    return _t(a0) < _t(b1) and _t(b0) < _t(a1)


def check_constraints(course: dict, profile: StudentProfile) -> tuple[bool, list[str]]:
    """
    Returns (eligible, notes).
    Ineligible reasons: already completed, missing prereqs, all sections conflict.
    Notes that don't block eligibility: partial section conflicts.
    """
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
            notes.append(f"Section(s) {', '.join(blocked)} conflict — {', '.join(free)} available.")
        return True, notes
    else:
        return False, ["All sections conflict with your schedule."]


# ─────────────────────────────────────────────────────────────────────────────
# Result type
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class CourseResult:
    course: dict
    bi_score: float       # cosine similarity from Stage 1
    cross_score: float    # normalized cross-encoder score from Stage 2
    final_score: float    # blended final score
    eligible: bool
    reasons: list[str]


# ─────────────────────────────────────────────────────────────────────────────
# Recommender
# ─────────────────────────────────────────────────────────────────────────────

class CourseRecommender:

    def __init__(self):
        if not _ST_OK:
            raise ImportError("Run: pip install sentence-transformers")
        print(f"[INFO] Loading bi-encoder  : {BI_ENCODER_MODEL}")
        self.bi = SentenceTransformer(BI_ENCODER_MODEL)
        print(f"[INFO] Loading cross-encoder: {CROSS_ENCODER_MODEL}")
        self.cross = CrossEncoder(CROSS_ENCODER_MODEL, max_length=512)
        self.courses: list[dict] = []
        self.embeddings: Optional[np.ndarray] = None

    # ── Document text ──────────────────────────────────────────────────────

    def _doc_text(self, course: dict) -> str:
        """
        Rich string representation of a course for embedding.
        Includes title, code, tags, description, and student review snippets.
        The repetition of the title and the inclusion of informal review
        language materially improves recall for colloquial queries.
        """
        tags = " ".join(course.get("tags", []))
        reviews = course.get("reviews", "")
        prereq_names = ", ".join(course.get("prereqs", [])) or "none"
        workload = course.get("workload_hrs_week", "")
        workload_str = f"Workload: approximately {workload} hours per week. " if workload else ""
        return (
            f"{course['title']}. "
            f"{course['mnemonic']} {course['number']}. "
            f"Topics and keywords: {tags}. "
            f"{course['description']} "
            f"{workload_str}"
            f"Prerequisites: {prereq_names}. "
            f"Student notes: {reviews}"
        )

    # ── Query augmentation ─────────────────────────────────────────────────

    def _augment_query(self, raw_query: str, profile: StudentProfile) -> str:
        """
        Prepend profile context so the embedding steers toward courses that
        fit the student's background, even when not explicitly mentioned.
        """
        year_map = {1: "first-year student", 2: "sophomore", 3: "junior", 4: "senior"}
        year_str = year_map.get(profile.year, "student")

        parts: list[str] = []
        if profile.major and profile.major != "Undeclared":
            parts.append(f"I am a {year_str} studying {profile.major}.")
        else:
            parts.append(f"I am a {year_str}.")
        if profile.career_goals:
            parts.append(f"My career goal is {profile.career_goals}.")
        parts.append(raw_query)
        return " ".join(parts)

    # ── Index management ───────────────────────────────────────────────────

    def build_index(self, courses: list[dict], force: bool = False) -> None:
        self.courses = courses
        ids = [c["id"] for c in courses]

        if not force and os.path.exists(INDEX_FILE):
            print("[INFO] Loading cached index…")
            with open(INDEX_FILE, "rb") as f:
                cached = pickle.load(f)
            if cached.get("model") == BI_ENCODER_MODEL and cached.get("ids") == ids:
                self.embeddings = cached["embeddings"]
                print(f"[INFO] Index ready — {len(self.courses)} courses.")
                return
            print("[INFO] Cache mismatch — rebuilding…")

        print(f"[INFO] Embedding {len(courses)} courses with {BI_ENCODER_MODEL}…")
        texts = [self._doc_text(c) for c in courses]
        self.embeddings = self.bi.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,   # unit vectors: dot product == cosine
            show_progress_bar=True,
            batch_size=32,
        )
        with open(INDEX_FILE, "wb") as f:
            pickle.dump({"model": BI_ENCODER_MODEL, "ids": ids,
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
        if self.embeddings is None:
            raise RuntimeError("Call build_index() first.")

        augmented = self._augment_query(raw_query, profile)

        # ── Stage 1: bi-encoder retrieval ─────────────────────────────────
        q_vec = self.bi.encode(augmented, convert_to_numpy=True,
                               normalize_embeddings=True)
        bi_scores: np.ndarray = self.embeddings @ q_vec  # (N,)
        top_idx = np.argsort(bi_scores)[::-1][:STAGE1_CANDIDATES]

        # ── Stage 2: cross-encoder re-ranking ─────────────────────────────
        candidates = [(augmented, self._doc_text(self.courses[i])) for i in top_idx]
        raw_cross = self.cross.predict(candidates, show_progress_bar=False)

        # sigmoid to map logits → [0, 1]
        cross_norm = 1.0 / (1.0 + np.exp(-raw_cross))

        # Blended score
        bi_candidate = bi_scores[top_idx]
        # Normalise bi scores to [0,1] within candidates so blend is fair
        bi_min, bi_max = bi_candidate.min(), bi_candidate.max()
        bi_norm = (bi_candidate - bi_min) / (bi_max - bi_min + 1e-9)
        blended = BI_WEIGHT * bi_norm + CROSS_WEIGHT * cross_norm

        # Sort candidates by blended score
        order = np.argsort(blended)[::-1]

        eligible_results: list[CourseResult] = []
        ineligible_results: list[CourseResult] = []

        for rank_i in order:
            course_i = int(top_idx[rank_i])
            course = self.courses[course_i]
            eligible, reasons = check_constraints(course, profile)
            result = CourseResult(
                course=course,
                bi_score=float(bi_scores[course_i]),
                cross_score=float(cross_norm[rank_i]),
                final_score=float(blended[rank_i]),
                eligible=eligible,
                reasons=reasons,
            )
            (eligible_results if eligible else ineligible_results).append(result)

        if show_ineligible:
            return eligible_results[:top_k] + ineligible_results[:top_k]
        return eligible_results[:top_k]
