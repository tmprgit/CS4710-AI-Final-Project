from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from itertools import combinations, product

from engine import _overlap


MAX_SCHEDULE_CANDIDATES = 12


@dataclass
class TimeBlock:
    days: list[str]
    start: str
    end: str

@dataclass
class PenaltyBlock(TimeBlock):
    weight: float = 0.3

@dataclass
class ScheduleConstraints:
    blocked: list[TimeBlock] = field(default_factory=list)
    penalties: list[PenaltyBlock] = field(default_factory=list)

@dataclass
class ScheduledCourse:
    course: dict
    section: dict
    recommendation_score: float

@dataclass
class Schedule:
    courses: list[ScheduledCourse]
    relevance_score: float
    penalty: float

    @property
    def total_score(self):
        return self.relevance_score - self.penalty


def _meetings_conflict(m_a, m_b):
    if not (set(m_a.get("days", [])) & set(m_b.get("days", []))):
        return False
    s_a, e_a, s_b, e_b = m_a.get("start"), m_a.get("end"), m_b.get("start"), m_b.get("end")
    return bool(s_a and e_a and s_b and e_b and _overlap(s_a, e_a, s_b, e_b))

def _sections_conflict(sec_a, sec_b):
    return any(_meetings_conflict(a, b)
        for a in sec_a.get("meetings", [])
        for b in sec_b.get("meetings", [])
    )


def _section_overlap(section, blocks):
    return sum(
        getattr(block, "weight", 1)
        for block in blocks
        if any(
            _meetings_conflict(
                meeting,
                {"days": block.days, "start": block.start, "end": block.end},
            )
            for meeting in section.get("meetings", [])
        )
    )


def parse_constraints(text, flan_tokenizer=None, flan_model=None):
    # TODO: Implement rule-based or fine-tuned constraint parsing
    # Currently LLM-based approach is unreliable for structured JSON output
    if not text.strip():
        return ScheduleConstraints()

    # if flan_model is None or flan_tokenizer is None:
    #     from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    #     print("[INFO] Loading t5-small for constraint parsing...")
    #     flan_tokenizer = AutoTokenizer.from_pretrained("t5-small")
    #     flan_model = AutoModelForSeq2SeqLM.from_pretrained("t5-small")
    #
    # print("[INFO] Parsing scheduling constraints with flan-t5-base...")
    # prompt = (
    #     'Convert these scheduling preferences into JSON with fields "blocked" (hard blocks) '
    #     'and "penalties" (soft preferences). Each entry has "days" (list from: Mon Tue Wed Thu Fri Sat Sun), '
    #     '"start" (HH:MM), "end" (HH:MM). Penalties also have "weight" 0.1-1.0. '
    #     '"No class before X" means block 00:00 to X. "No class after X" means block X to 23:59. '
    #     f'"Preferably no X" means a penalty. Output only valid JSON. Preferences: {text}'
    # )
    #
    # inputs = flan_tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
    # outputs = flan_model.generate(**inputs, max_new_tokens=256)
    # raw = flan_tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
    # match = re.search(r"\{.*\}", raw, re.DOTALL)
    # data = json.loads(match.group() if match else raw)
    # return ScheduleConstraints(
    #     blocked=[TimeBlock(**b) for b in data.get("blocked", [])],
    #     penalties=[PenaltyBlock(**p) for p in data.get("penalties", [])],
    # )

    return ScheduleConstraints()


def find_similar_course_pairs(courses, bi_encoder, threshold=0.92):
    if len(courses) < 2:
        return []
    texts = [f"{c['title']}. {c['description'][:300]}" for c in courses]
    emb = bi_encoder.encode(texts, convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=False)
    sim = emb @ emb.T
    return [
        (courses[i]["id"], courses[j]["id"])
        for i in range(len(courses))
        for j in range(i + 1, len(courses))
        if sim[i, j] >= threshold
    ]


def _find_section_assignment(combo):
    for assignment in product(*[secs for _, _, secs in combo]):
        if not any(_sections_conflict(a, b) for a, b in combinations(assignment, 2)):
            return list(assignment)
    return None


def _year_penalty(course, student_year):
    level = course.get("number", 0) // 1000
    return (2 ** abs(level - student_year) - 1) * 0.2 if level else 0

def _adjusted_score(r, student_year):
    return (r.final_score - _year_penalty(r.course, student_year) - (0.5 if "independent study" in r.course["title"].lower() else 0))


def _course_credits(course):
    c = course.get("credits", 0)
    if isinstance(c, str) and "-" in c:
        return int(c.split("-")[0])
    return int(c or 0)


def build_schedules(results, constraints=None, similar_pairs=None, student_year=2,
                    target_credits=15, top_n=5):
    constraints = constraints or ScheduleConstraints()
    similar_pairs = similar_pairs or []
    candidates = [
        (r, _adjusted_score(r, student_year), secs)
        for r in results
        if (secs := [
            s for s in r.course.get("sections", [])
            if not _section_overlap(s, constraints.blocked)
        ])
    ]
    candidates.sort(key=lambda item: item[1], reverse=True)
    candidates = candidates[:MAX_SCHEDULE_CANDIDATES]

    similar_set = {frozenset(p) for p in similar_pairs}
    min_credits, max_credits = target_credits - 1, target_credits + 1
    schedules = []

    for k in range(target_credits // 4, target_credits // 3 + 2):
        for combo in combinations(candidates, k):
            credits = sum(_course_credits(r.course) for r, _, _ in combo)
            if not (min_credits <= credits <= max_credits):
                continue
            ids = {r.course["id"] for r, _, _ in combo}
            if any(frozenset(pair) in similar_set for pair in combinations(ids, 2)):
                continue
            assignment = _find_section_assignment(combo)
            if assignment is None:
                continue
            relevance = sum(score for _, score, _ in combo)
            penalty = sum(_section_overlap(section, constraints.penalties) for section in assignment)
            schedules.append(Schedule(
                courses=[ScheduledCourse(r.course, s, score) for (r, score, _), s in zip(combo, assignment)],
                relevance_score=relevance,
                penalty=penalty,
            ))

    return sorted(schedules, key=lambda s: s.total_score, reverse=True)[:top_n]
