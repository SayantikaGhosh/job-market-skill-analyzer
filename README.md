# Job Market Skill-Demand Analyzer

An end-to-end data pipeline that collects real job postings from public ATS
APIs, extracts required skills from free-text descriptions, and analyzes
skill demand and co-occurrence for technical roles in the Indian job market.

This project was built to demonstrate the full analyst workflow — collecting
real data, cleaning it, writing real analytical SQL, and landing on a
specific, defensible insight — not just moving data from one place to
another.

---

## What this project does

1. **Collects** live job postings from company career pages via the
   Greenhouse and Lever public job board APIs.
2. **Cleans** the raw postings — normalizes two different ATS JSON formats
   into one schema, deduplicates, validates data quality.
3. **Classifies** postings into six technical role categories and extracts
   required skills from each posting using a curated skill dictionary.
4. **Analyzes** the result in PostgreSQL using window functions and CTEs to
   surface skill-demand rankings and co-occurrence patterns.
5. **Surfaces a specific finding** rather than a generic dashboard of counts
   (see [Key Findings](#key-findings)).

---

## Data sources

| Source | Role | Why |
|---|---|---|
| **Greenhouse** (public JSON API) | Full postings + descriptions | Public, unauthenticated, meant for external consumption |
| **Lever** (public JSON API) | Full postings + descriptions | Same as above |

**Evaluated and dropped: Adzuna API.** Initially considered as a secondary
source for market context (volume, title, salary) and as a possible
cross-validation source for skill extraction. Testing showed every sampled
description was truncated to exactly 500 characters, and Adzuna's public API
documentation confirmed there is no full-description parameter — the API is
structurally designed to route traffic back to the original listing rather
than serve complete records. Since full descriptions are required for skill
extraction and Greenhouse/Lever already cover that need, Adzuna was dropped
from the pipeline rather than kept for a narrower role.

**Deliberately not used:** LinkedIn, Naukri, Indeed. Both explicitly prohibit
scraping in their terms of service, LinkedIn has a track record of
litigating against scrapers, and both have anti-bot protections that make
reliable collection at scale impractical. Greenhouse/Lever's public,
unauthenticated endpoints achieve the same goal — pulling structured data
from live web sources — without that risk.

---

## Pipeline

```
Raw JSON snapshots (Greenhouse + Lever)
        │
        ▼
normalize_jobs.py       → common schema across both ATS formats
        │
        ▼
deduplicate_jobs.py     → dedupe on (source, job_id), keep newest snapshot
        │                  1,625 → 1,397 unique postings
        ▼
validate_jobs.py        → data quality checks (missing fields, invalid URLs)
        │
        ▼
classify_roles.py       → title-based rules + description-based scoring
        │                  for ambiguous titles → 64 India-based postings
        │                  classified into 6 target roles
        ▼
phase2_extract_skills.py → regex skill-dictionary matching against
        │                   title + description → 53 unique skills,
        │                   418 posting-skill relationships
        ▼
PostgreSQL (Supabase)   → postings / skills / posting_skills tables
        │
        ▼
SQL analysis            → window functions, CTEs → findings
```

Raw API responses are preserved untouched at every stage so any bug in a
later step never requires re-fetching data from source.

---

## Repository structure

```
src/
├── collection/       # Greenhouse + Lever API collectors
├── cleaning/         # normalization, deduplication
├── classification/   # role classification
├── skills/           # skill extraction
└── validation/        # data quality checks

sql/
├── schema/           # CREATE TABLE definitions
├── load/             # load classified data into PostgreSQL
└── analysis/         # window-function and CTE queries

data/                 # raw snapshots, normalized, deduplicated datasets
reports/              # validation, classification, and skill inventory reports
```

---

## Database schema

Three normalized tables — deliberately not one denormalized table, since
schema design is part of what this project demonstrates:

- **`postings`** — one row per classified posting (job_id, source, company,
  title, role, location, snapshot_date, url, description)
- **`skills`** — one row per distinct skill
- **`posting_skills`** — many-to-many join table linking postings to skills

The database loads only the **64 role-classified postings** that passed
Phase 2 skill extraction, since those are the only records with the role and
skill data the analysis requires. The full 1,397-posting deduplicated
dataset is preserved upstream as JSON — the audit trail for how the 64 were
selected, not part of the relational schema.

---

## Methodology notes and known limitations

This project prioritizes an explainable, defensible method over a
sophisticated-looking but opaque one.

- **Skill extraction is regex/keyword-based, not NLP.** A curated
  dictionary of ~60 terms is matched against posting title + description
  using word-boundary-aware regex. This is simple enough to defend every
  step of, at the cost of missing some real-world phrasing variants (e.g.
  "Software Development Engineer" doesn't match "Software Engineer" as a
  substring).
- **`Go` was removed from the skill dictionary.** It was briefly the
  third-most-frequent "skill" detected (17 matches), but manual review
  found 12 of those 17 were false positives from ordinary English usage
  ("Go-to-Market," "go-to person," "door-to-door"). Rather than building
  context-aware disambiguation, the term was dropped and this limitation is
  disclosed rather than hidden.
- **Sample size varies significantly by role**, and this shapes how the
  results should be read:

  | Role | Postings | Treat as |
  |---|---|---|
  | Software Engineer | 31 | Reliable |
  | Data Engineer | 12 | Reliable |
  | Data Analyst | 8 | Directional |
  | Backend Engineer | 8 | Directional |
  | Data Scientist | 4 | Directional |
  | Analytics Engineer | 1 | Not statistically meaningful |

  Findings for Software Engineer and Data Engineer are treated as reliable.
  Findings for the other four roles are reported for completeness but are
  explicitly not treated as representative of the broader market.

### Bugs found and fixed during development

Two upstream data bugs were found by investigating suspicious results rather
than trusting clean-looking numbers — both materially changed the dataset
and are documented here for transparency:

1. **Missing `company` field (Lever).** Unlike Greenhouse, Lever's API
   doesn't repeat the company name inside each job object (one board = one
   company). The normalizer was defaulting this to an empty string. Fixed
   by deriving company name from the raw snapshot filename and passing it
   into the normalizer explicitly.
2. **Incomplete description extraction (Lever).** Several postings with
   titles explicitly naming real skills (e.g. "Lead Data Engineer With
   Snowflake") were producing zero skill matches. Investigation showed
   Lever splits job content across `descriptionPlain` (often just a
   generic company blurb) and a separate `lists` field containing the
   actual responsibilities/requirements — the normalizer was only reading
   the former. Fixing this recovered real content: classified postings
   increased from 58 to 64, and postings with zero skill matches dropped
   from 13 to 0.

---

## Key findings

Based on the 64 classified postings (treat Software Engineer / Data
Engineer results as reliable; other roles as directional — see limitations
above):

- **SQL is the most in-demand skill overall**, appearing in **62.5%** of
  classified postings, followed by Python at **51.6%**.
- **BI-tool requirements are far less common than SQL itself**: of the 40
  postings requiring SQL, only **20% also require Tableau**, **10% also
  require Power BI**, and just **2 postings require both**. SQL is a
  near-universal baseline skill; a named BI tool is not.
- **Skill profiles differ clearly by role**: Data Engineer postings are
  strongly associated with SQL, Python, Airflow, Spark, and cloud
  platforms; Software Engineer postings show stronger signals around
  Kubernetes, React, Docker, and microservices — reflecting the different
  nature of the two roles' work.
- Cloud/infrastructure tooling (AWS, Kubernetes, Azure, Docker) forms a
  clear secondary skill tier behind core languages, appearing consistently
  across both reliable-sample roles.

---

## Tech stack

Python (`requests`, `pandas`), PostgreSQL (Supabase), SQL (window functions,
CTEs), Streamlit *(dashboard — in progress)*, Greenhouse/Lever public APIs.

---

## Project status

- ✅ Phase 1 — Data collection
- ✅ Phase 2 — Cleaning and skill extraction
- ✅ Phase 3 — Database modeling and SQL analysis
- 🚧 Phase 4 — Streamlit dashboard
- ⬜ Phase 5 — Deployment