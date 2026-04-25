# AI Course Recommender

Run the GUI:

```bash
cd gui
python app.py
```

CLI options:

```bash
python main.py              # interactive mode
python main.py --demo       # run demo queries
python main.py --list       # print the full course catalog
python main.py --rebuild    # force-rebuild the embedding index
```

## AI Use

- `BM25` handles exact keyword matching on the catalog text.
- `all-mpnet-base-v2` bi-encoder embeds every course once, then embeds the user query at runtime for semantic retrieval.
- `cross-encoder/ms-marco-MiniLM-L-6-v2` re-ranks the top retrieval candidates with a query-course pair score.
- A rule-based department alias boost increases scores when the query clearly names a subject area like `CS`, `math`, or `econ`.
- A bi-encoder similarity check flags near-duplicate courses so the scheduler avoids putting highly similar classes in the same schedule.
- The planned FLAN/T5-style constraint parser is commented out, so the current codebase does not use an LLM for schedule preference parsing.

## General Functionality

- Course data is loaded from the SQLite catalog, including descriptions, prerequisites, sections, meeting times, and instructors.
- The user provides completed courses, major, year, target credits, and a natural-language course-interest query.
- The query is augmented with profile context, then scored against the catalog with BM25 + bi-encoder retrieval, followed by cross-encoder re-ranking.
- Retrieved courses are filtered for eligibility: already-completed courses are removed, prerequisites are checked, and sections that conflict with the student's busy times are rejected.
- The top recommendation set is checked for course-to-course semantic similarity, and overly similar pairs are marked as incompatible.
- The scheduler tries course combinations near the target credit load, removes combos with time conflicts or similar-course clashes, and picks one valid section per course.
- Final schedules are scored by summed recommendation strength, then adjusted by year-level mismatch penalties and any scheduling penalties that may be configured.
- The app returns the top ranked schedules, each with course, section, time, instructor, credits, and match score.
