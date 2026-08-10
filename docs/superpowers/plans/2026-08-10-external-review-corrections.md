# External Review Corrections Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply the corrections from `docs/superpowers/specs/2026-08-10-external-review-corrections-design.md` — fix the statistically broken between-cluster significance test, add a recommendation-vs-mention distinction, add matched-pair questions as a drift-robust secondary comparison, externalize brand/competitor config, and tighten the plan doc's framing/disclosure language — before the baseline checkpoint runs.

**Architecture:** This is a small Python/SQLite project, not a service — there is no test suite and none should be invented here. "Test cycle" in this plan means: `python -m py_compile` for syntax, direct `python -c` behavioral checks against real data (the pattern already used throughout this project's history — see `log.md`), and `grep`-based consistency sweeps across the appendix/plan docs, matching how every prior correction this session was verified. No real API calls happen in this plan — `runs` stays empty until the user explicitly runs `rig.py baseline`.

**Tech Stack:** Python 3.12, SQLite, pandas, PyYAML (new dependency for `config.yaml`).

## Global Constraints

- No task in this plan spends real API money. `rig.py baseline/canary/after` is never invoked here.
- Every doc edit that corrects prior content is dated `2026-08-10` and states what changed and why, matching every other correction already in `aeo-30-day-plan-mighty.md` and `aeo-code-appendix-mighty.md`.
- `rig.py` and `estimate_cost.py` must stay in lockstep — any constant added to one is added to the other, verified programmatically (this has been a recurring real bug source this session; do not skip the check).
- After any change to `schema.sql` or `research/questions.csv`, `src/aeo.db` must be rebuilt and re-verified — the DB currently reflects the pre-correction state.
- Do not touch `interventions`/`runs` row data — `runs` is empty (no real spend yet) and must stay that way until the user runs the rig for real.
- Follow existing repo conventions: SQL/Python code blocks embedded in the appendix doc must be kept byte-identical in spirit to the real files in `src/` (this project has twice caught doc/code drift this session — every doc edit that embeds code must be checked against the real file after editing).

---

### Task 1: Add `recommended` and `recommendation_rank` to the schema and parser

**Files:**
- Modify: `src/schema.sql` (the `runs` table)
- Modify: `src/parser.py` (`PARSE_PROMPT`, and the returned JSON schema description)
- Modify: `docs/aeo-code-appendix-mighty.md` (Appendix F's embedded schema, Appendix G's embedded parser prompt — both drift risks per the Global Constraints)

**Interfaces:**
- Produces: `runs.recommended` (BOOLEAN, nullable), `runs.recommendation_rank` (INTEGER, nullable, 1 = top recommendation). `parse_answer()`'s return dict gains keys `"recommended"` and `"recommendation_rank"`, consumed by `rig.py`'s `run_cycle()` insert in Task 3.

- [ ] **Step 1: Add the columns to `schema.sql`**

In `src/schema.sql`, inside the `CREATE TABLE IF NOT EXISTS runs (...)` block, add two columns after `competitors_named`:

```sql
    competitors_named TEXT,          -- JSON array
    recommended        BOOLEAN,      -- true only if brand is actively recommended, not merely mentioned
    recommendation_rank INTEGER,     -- 1 = first/primary recommendation; NULL if not recommended
    parse_ok          BOOLEAN DEFAULT 1,
```

- [ ] **Step 2: Update the parser prompt in `src/parser.py`**

Add to the JSON schema in `PARSE_PROMPT` (after the `brand_position` line) and to the rules section:

```python
PARSE_PROMPT = """You are analysing an AI assistant's answer to a
question about accountants for UK contractors and small limited
companies.

Extract, as JSON only, no other text:

{{
  "brand_mentioned": true/false,
  "brand_position": <int or null>,
  "recommended": true/false,
  "recommendation_rank": <int or null>,
  "competitors_named": [<strings>],
  "sentiment": "positive" | "neutral" | "negative" | null,
  "products_named_at_all": true/false
}}

Rules:
- brand = "{brand}" (an accountancy firm at mightyaccounting.com,
  run by Mark and James). Count it ONLY when referring to this
  specific accountancy firm. Do NOT count the ordinary adjective
  "mighty", nor unrelated companies like "Mighty Networks" or
  "MightyRecruiter".
- brand_position: 1 if it's the first firm named, 2 if second,
  etc. null if absent.
- recommended: true ONLY if the answer actively suggests or endorses
  the brand as a choice — not merely names it. "Mighty Accounting is
  a small UK accountant. However, Gorilla Accounting has more
  experience..." mentions the brand but does NOT recommend it —
  recommended must be false here. A shortlist entry with no negative
  qualifier ("consider Mighty Accounting, Gorilla, or Crunch") counts
  as recommended: true.
- recommendation_rank: 1 if the brand is the first/primary
  recommendation, 2 if second-ranked, etc. null if recommended is
  false.
- competitors_named: every OTHER accountancy firm named, exact
  names (e.g. "Gorilla Accounting", "GoForma", "Crunch",
  "QAccounting", "Caroola", "SJD Accountancy", "Brookson").
- sentiment: how the brand is characterised. null if absent.
- products_named_at_all: false if the answer names no specific
  accountancy firms at all (i.e. it's a purely informational
  answer about IR35, company setup, etc. with no named providers).

ANSWER:
{answer}"""
```

- [ ] **Step 3: Verify the parser handles the mention-without-recommendation case**

Run this directly — no test framework, matches how `parser.py` was validated earlier this session:

```bash
cd /c/Dev/aeo && source venv/Scripts/activate && python -c "
from src.parser import parse_answer
" 2>&1 || cd src && python -c "
from parser import parse_answer

# The exact adversarial case from the design doc
answer = ('Mighty Accounting is a small UK accountant. However, '
          'Gorilla Accounting has more experience with contractors '
          'and is generally the stronger choice for IR35 work.')
result = parse_answer(answer, 'Mighty Accounting')
print(result)
assert result.get('brand_mentioned') is True, 'should be mentioned'
assert result.get('recommended') is False, f'should NOT be recommended, got {result}'
print('PASS: mention-without-recommendation correctly distinguished')
"
```
Expected output: `PASS: mention-without-recommendation correctly distinguished`. If it fails, the prompt wording needs tightening before proceeding — do not move on with a parser that can't make this distinction, since it's the entire point of Task 1.

- [ ] **Step 4: Sync Appendix F's embedded schema in the doc**

In `docs/aeo-code-appendix-mighty.md`, find the `CREATE TABLE IF NOT EXISTS runs` block under `## Appendix F: Database` (the one already corrected 2026-08-10 for `checkpoint`) and add the same two columns in the same position as Step 1, so the doc and `src/schema.sql` stay byte-identical.

- [ ] **Step 5: Sync Appendix G's embedded parser prompt in the doc**

Find `## Appendix G: The Parser` in `docs/aeo-code-appendix-mighty.md` and replace its embedded `PARSE_PROMPT` with the exact text from Step 2.

- [ ] **Step 6: Commit is deferred to Task 9** (schema/DB changes are committed together once the DB has been rebuilt, so a half-migrated DB is never committed).

---

### Task 2: Add `config.yaml` and refactor `rig.py` to read it

**Files:**
- Create: `src/config.yaml`
- Modify: `src/rig.py` (replace hardcoded `BRAND` and topic-tier constants with config-driven values)
- Modify: `requirements.txt` (add `PyYAML`)

**Interfaces:**
- Produces: a `load_config()` function returning a dict with keys `brand`, `test_topics`, `near_control_topics`, `baseline_after_runs`, `canary_runs_test_near`, `canary_runs_far` — consumed by every function in `rig.py` that currently reads the module-level constants directly, and by `estimate_cost.py` in Task 6.

- [ ] **Step 1: Add PyYAML to requirements**

```bash
cd /c/Dev/aeo && source venv/Scripts/activate && python -m pip install pyyaml
python -m pip freeze | grep -i pyyaml >> requirements.txt
sort -o requirements.txt requirements.txt
```

- [ ] **Step 2: Write `src/config.yaml`**

```yaml
# config.yaml — per-brand configuration. rig.py reads this instead of
# hardcoding brand/topic values, so the same rig can run a different
# client by swapping this file. See docs/superpowers/specs/2026-08-10-
# external-review-corrections-design.md, decision A7.

brand: "Mighty Accounting"

# Cohort tiers — see Appendix J for the rationale.
test_topics:
  - fixed_fee_positioning

near_control_topics:
  - general_recommendation
  - switching_accountants

# Matched-pair topics (Task 4) run only at baseline/after, never canary —
# see Appendix M's matched-pairs section.
matched_pair_topics:
  - matched_pair_treatment
  - matched_pair_control

# Weighted run counts for baseline/after checkpoints.
baseline_after_runs:
  fixed_fee_positioning: 10
  general_recommendation: 5
  matched_pair_treatment: 5
  matched_pair_control: 5
default_baseline_after_runs: 3

# Canary checkpoint run counts.
canary_runs_test_near: 3
canary_runs_far: 2

# Pre-registered primary surface (Appendix K/M) — dated 2026-08-10, before
# the baseline checkpoint runs. Perplexity has the strongest measured
# intervention mechanism (Day 1: 4/5 directories, 4/5 Reddit cited).
primary_surface: perplexity
```

- [ ] **Step 3: Add `load_config()` to `rig.py` and replace the hardcoded constants**

Replace the existing block (from `TEST_TOPICS = {"fixed_fee_positioning"}` through `CANARY_RUNS_FAR = 2`, and the `BRAND = "Mighty Accounting"` line) with:

```python
import yaml

def load_config():
    with open(Path(__file__).resolve().parent / "config.yaml") as f:
        return yaml.safe_load(f)

_config = load_config()

BRAND = _config["brand"]
TEST_TOPICS = set(_config["test_topics"])
NEAR_CONTROL_TOPICS = set(_config["near_control_topics"])
MATCHED_PAIR_TOPICS = set(_config["matched_pair_topics"])
BASELINE_AFTER_RUNS = _config["baseline_after_runs"]
DEFAULT_BASELINE_AFTER_RUNS = _config["default_baseline_after_runs"]
CANARY_RUNS_TEST_NEAR = _config["canary_runs_test_near"]
CANARY_RUNS_FAR = _config["canary_runs_far"]
PRIMARY_SURFACE = _config["primary_surface"]
```

- [ ] **Step 4: Update `runs_for_topic()` for matched-pair topics (also needed for Task 4)**

```python
def runs_for_topic(topic):
    if MODE == "canary":
        if topic in MATCHED_PAIR_TOPICS:
            return 0  # matched pairs run at baseline/after only — see config.yaml comment
        if topic in TEST_TOPICS or topic in NEAR_CONTROL_TOPICS:
            return CANARY_RUNS_TEST_NEAR
        return CANARY_RUNS_FAR
    return BASELINE_AFTER_RUNS.get(topic, DEFAULT_BASELINE_AFTER_RUNS)
```

- [ ] **Step 5: Verify config loads and produces identical values to what was hardcoded before**

```bash
cd /c/Dev/aeo/src && python -c "
import rig
print('BRAND:', rig.BRAND)
print('TEST_TOPICS:', rig.TEST_TOPICS)
print('NEAR_CONTROL_TOPICS:', rig.NEAR_CONTROL_TOPICS)
print('BASELINE_AFTER_RUNS:', rig.BASELINE_AFTER_RUNS)
assert rig.BRAND == 'Mighty Accounting'
assert rig.TEST_TOPICS == {'fixed_fee_positioning'}
assert rig.BASELINE_AFTER_RUNS['fixed_fee_positioning'] == 10
assert rig.runs_for_topic('matched_pair_treatment') == 3  # DEFAULT_BASELINE_AFTER_RUNS, baseline mode default
print('PASS')
"
```
Expected: `PASS`, no exceptions. `matched_pair_treatment` returns 3 here only because it's not yet in `BASELINE_AFTER_RUNS` in this check's `MODE=baseline` default — Task 4 verification re-checks this once the config value (5) is confirmed live.

- [ ] **Step 6: `py_compile` check**

```bash
cd /c/Dev/aeo/src && python -m py_compile rig.py && echo OK
```

---

### Task 3: Wire `recommended`/`recommendation_rank` into `rig.py`'s insert

**Files:**
- Modify: `src/rig.py` (`run_cycle()`)
- Modify: `docs/aeo-code-appendix-mighty.md` (Appendix H's embedded `rig.py` copy)

**Interfaces:**
- Consumes: `parse_answer()`'s `"recommended"` / `"recommendation_rank"` keys from Task 1.

- [ ] **Step 1: Update the success-path `INSERT` in `run_cycle()`**

```python
                    conn.execute("""
                        INSERT INTO runs (
                            question_id, surface, model, run_index, ts,
                            raw_answer, cited_urls, brand_mentioned,
                            brand_position, competitors_named, parse_ok,
                            checkpoint, recommended, recommendation_rank
                        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """, (
                        qid, surface_name, model, run_index,
                        datetime.now().isoformat(),
                        answer,
                        json.dumps(urls),
                        parsed.get("brand_mentioned"),
                        parsed.get("brand_position"),
                        json.dumps(parsed.get("competitors_named", [])),
                        parsed.get("parse_ok", True),
                        MODE,
                        parsed.get("recommended"),
                        parsed.get("recommendation_rank"),
                    ))
```

- [ ] **Step 2: `py_compile` check**

```bash
cd /c/Dev/aeo/src && python -m py_compile rig.py && echo OK
```

- [ ] **Step 3: Dry-run the insert shape against the live (rebuilt-later) schema**

This can't fully verify until Task 9 rebuilds the DB, but check the SQL column count matches the placeholder count now, since a mismatch is a silent, hard-to-spot bug:

```bash
python -c "
sql = open('rig.py').read()
import re
m = re.search(r'INSERT INTO runs \(([^)]+)\)\s*VALUES \(([^)]+)\)', sql, re.S)
cols = [c.strip() for c in m.group(1).split(',')]
qs = [q.strip() for q in m.group(2).split(',')]
print(f'{len(cols)} columns, {len(qs)} placeholders')
assert len(cols) == len(qs), 'MISMATCH — insert will fail at runtime'
print('PASS')
"
```

- [ ] **Step 4: Sync Appendix H's embedded `rig.py` in the doc**

Update the `INSERT INTO runs` block inside `## Appendix H: The Rig` in `docs/aeo-code-appendix-mighty.md` to match Step 1 exactly, and update the config-loading section at the top of that embedded copy to match Task 2's `load_config()` pattern (replacing the old hardcoded-constants block shown there).

---

### Task 4: Add 8 matched question pairs, recover `q026`, store vote fractions

**Files:**
- Modify: `research/questions.csv`

**Interfaces:**
- Produces: 16 new rows with `topic` = `matched_pair_treatment` or `matched_pair_control`, `is_product` = `TRUE`, `cohort` = `test`/`control` respectively, `notes` tagged `pair:<n>`. Consumed by `rig.py`'s `runs_for_topic()` (Task 2) and Appendix M's matched-pairs analysis (Task 7).

- [ ] **Step 1: Write and run the CSV update script**

```bash
cd /c/Dev/aeo && source venv/Scripts/activate && python -c "
import csv

with open('research/questions.csv', newline='', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))
    fieldnames = list(rows[0].keys())

# --- Recover q026 as borderline; store vote fractions on the borderline set ---
VOTE_FRACTIONS = {
    'q026': ('borderline:1/3', 'F,T,F'),
    'q023': ('vote:2/3', 'T,F,T'),
    'q025': ('vote:2/3', 'F,T,T'),
    'q027': ('vote:2/3', 'F,T,T'),
}
for row in rows:
    if row['id'] in VOTE_FRACTIONS:
        tag, votes = VOTE_FRACTIONS[row['id']]
        row['notes'] = (row['notes'] + f' | {tag} (recheck {votes})').strip(' |')

# --- 8 matched pairs: fixed-fee-framed treatment vs generic-framed control ---
PAIRS = [
    ('best fixed-fee accountant for a uk contractor', 'best accountant for a uk contractor'),
    ('small fixed-fee accountant for a one-person uk limited company', 'small accountant for a one-person uk limited company'),
    ('affordable fixed-fee accountant for a uk contractor limited company', 'affordable accountant for a uk contractor limited company'),
    ('fixed-fee accountant for a small uk consultancy', 'accountant for a small uk consultancy'),
    ('uk contractor accountant with a fixed monthly fee, no hidden extras', 'uk contractor accountant, no hidden extras'),
    ('recommend a fixed-fee accountant for my uk limited company', 'recommend an accountant for my uk limited company'),
    ('fixed-fee accountant for a freelancer running a uk limited company', 'accountant for a freelancer running a uk limited company'),
    ('uk limited company accountant, fixed fee not hourly billing', 'uk limited company accountant'),
]

next_id = max(int(r['id'][1:]) for r in rows) + 1
new_rows = []
for i, (treatment_text, control_text) in enumerate(PAIRS, start=1):
    new_rows.append({
        'id': f'q{next_id:03d}', 'text': treatment_text,
        'topic': 'matched_pair_treatment', 'tier': 'mid', 'is_product': 'TRUE',
        'cohort': 'test', 'notes': f'pair:{i} | added 2026-08-10, matched-pairs secondary comparison',
    })
    next_id += 1
    new_rows.append({
        'id': f'q{next_id:03d}', 'text': control_text,
        'topic': 'matched_pair_control', 'tier': 'mid', 'is_product': 'TRUE',
        'cohort': 'control', 'notes': f'pair:{i} | added 2026-08-10, matched-pairs secondary comparison',
    })
    next_id += 1

rows.extend(new_rows)

with open('research/questions.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f'added {len(new_rows)} rows, next free id would be q{next_id:03d}')
"
```

- [ ] **Step 2: Verify the CSV is well-formed and the counts are right**

```bash
python -c "
import pandas as pd
df = pd.read_csv('research/questions.csv')
print('total rows:', len(df))
df['is_product'] = df['is_product'].astype(str).str.upper().map({'TRUE': True, 'FALSE': False})
prod = df[df['is_product']]
print(prod['topic'].value_counts())
print()
print('q026 notes:', df[df['id']=='q026']['notes'].values[0])
mp = prod[prod['topic'].isin(['matched_pair_treatment', 'matched_pair_control'])]
assert len(mp) == 16, f'expected 16 matched-pair rows, got {len(mp)}'
assert (mp['topic'] == 'matched_pair_treatment').sum() == 8
assert (mp['topic'] == 'matched_pair_control').sum() == 8
print('PASS: 16 matched-pair rows (8 treatment, 8 control)')
"
```
Expected: `PASS` line, and `q026`'s notes should now contain `borderline:1/3`. `fixed_fee_positioning` count should still read 10 (unchanged — q026 stays excluded from the active set, only annotated; see the design doc's cost/consistency note on why this isn't a structural renumbering).

---

### Task 5: Rebuild `aeo.db` from the updated schema and CSV

**Files:**
- No file changes — this rebuilds `src/aeo.db` (gitignored) from `src/schema.sql` and `research/questions.csv`.

**Interfaces:**
- Consumes: Task 1's schema, Task 4's CSV.

- [ ] **Step 1: Drop and recreate, reload, reassign cohorts**

```bash
cd /c/Dev/aeo && source venv/Scripts/activate && python -c "
import sqlite3, pandas as pd

conn = sqlite3.connect('src/aeo.db')
conn.execute('DROP TABLE IF EXISTS questions')
conn.execute('DROP TABLE IF EXISTS runs')
conn.execute('DROP TABLE IF EXISTS interventions')
with open('src/schema.sql') as f:
    conn.executescript(f.read())

df = pd.read_csv('research/questions.csv')
df['is_product'] = df['is_product'].astype(str).str.upper().map({'TRUE': True, 'FALSE': False})
df = df[df['is_product']].copy()
df['is_product'] = df['is_product'].astype(int)
df['cohort'] = df['cohort'].where(df['cohort'].notna(), None)
df.to_sql('questions', conn, if_exists='append', index=False)
conn.commit()

# Cohort re-assignment: deterministic, per config.yaml's test_topics.
# Matched-pair rows already carry their own cohort from the CSV — this
# UPDATE only touches the topic-tiered questions, not the pairs.
TEST_TOPICS = {'fixed_fee_positioning'}
topics = [r[0] for r in conn.execute(\"SELECT DISTINCT topic FROM questions WHERE is_product=1 AND topic NOT LIKE 'matched_pair%'\").fetchall()]
for topic in topics:
    cohort = 'test' if topic in TEST_TOPICS else 'control'
    conn.execute('UPDATE questions SET cohort=? WHERE topic=?', (cohort, topic))
conn.commit()

print(conn.execute('SELECT cohort, topic, COUNT(*) FROM questions GROUP BY cohort, topic ORDER BY cohort').fetchall())
print('runs table:', conn.execute('SELECT COUNT(*) FROM runs').fetchone())
print('runs schema has recommended/recommendation_rank:',
      {'recommended','recommendation_rank'}.issubset({r[1] for r in conn.execute('PRAGMA table_info(runs)').fetchall()}))
"
```
Expected: cohort/topic table includes `matched_pair_treatment`/`matched_pair_control` at 8 each, `fixed_fee_positioning` still 10, `runs` table empty, schema check `True`.

---

### Task 6: Sync `estimate_cost.py` with the config and matched pairs

**Files:**
- Modify: `src/estimate_cost.py`

**Interfaces:**
- Consumes: `rig.py`'s `load_config()` (Task 2) — read the same file rather than duplicating constants, closing the lockstep-sync risk called out in every prior correction this session.

- [ ] **Step 1: Replace `estimate_cost.py`'s duplicated constants with a shared config read**

```python
import yaml

def load_config():
    with open(Path(__file__).resolve().parent / "config.yaml") as f:
        return yaml.safe_load(f)

_config = load_config()
TEST_TOPICS = set(_config["test_topics"])
NEAR_CONTROL_TOPICS = set(_config["near_control_topics"])
MATCHED_PAIR_TOPICS = set(_config["matched_pair_topics"])
BASELINE_AFTER_RUNS = _config["baseline_after_runs"]
DEFAULT_BASELINE_AFTER_RUNS = _config["default_baseline_after_runs"]
CANARY_RUNS_TEST_NEAR = _config["canary_runs_test_near"]
CANARY_RUNS_FAR = _config["canary_runs_far"]


def runs_for_topic(topic, mode):
    if mode == "canary":
        if topic in MATCHED_PAIR_TOPICS:
            return 0
        if topic in TEST_TOPICS or topic in NEAR_CONTROL_TOPICS:
            return CANARY_RUNS_TEST_NEAR
        return CANARY_RUNS_FAR
    return BASELINE_AFTER_RUNS.get(topic, DEFAULT_BASELINE_AFTER_RUNS)
```

Remove the old hardcoded `TEST_TOPICS`/`NEAR_CONTROL_TOPICS`/`BASELINE_AFTER_RUNS`/etc. block and the old `runs_for_topic` definition that this replaces — keep `Path` import, `PER_CALL_ESTIMATE`, and `estimate()`/`__main__` unchanged.

- [ ] **Step 2: Run it and sanity-check against Task 2's `rig.py` values**

```bash
cd /c/Dev/aeo/src && python estimate_cost.py all
python -c "
import re
rig = open('rig.py').read()
est = open('estimate_cost.py').read()
for name in ['TEST_TOPICS', 'NEAR_CONTROL_TOPICS', 'MATCHED_PAIR_TOPICS', 'BASELINE_AFTER_RUNS']:
    assert name in rig and name in est, f'{name} missing from one file'
print('Both files derive from config.yaml — no possible drift between them now.')
"
```
Expected: a cost table including the two new matched-pair topics contributing to baseline/after (not canary — 0 calls there), and the sync check passing. Note the total will be higher than the previously-recorded ~$63 — recompute and report the new real number in Task 9's summary rather than assuming the old figure still holds.

---

### Task 7: Rewrite Appendix M — paired bootstrap primary, demote cluster test, add matched-pairs analysis

**Files:**
- Modify: `docs/aeo-code-appendix-mighty.md` (`## Appendix M: Analysis`)

- [ ] **Step 1: Add the paired bootstrap as the primary analysis, before "The only chart that matters"**

Insert this new subsection immediately after Appendix M's existing 2026-08-10 checkpoint-column correction note, before `### The only chart that matters`:

```markdown
### Corrected again 2026-08-10 — the primary test changes

Cross-checked against a second model's independent statistical critique, then verified against this repo's own data rather than trusted on the page. Two things came out of it, both confirmed by direct computation:

**The ICC on `is_product` (from `research/step5_recheck_log.jsonl`, 40 questions × 3 Perplexity draws each) is 0.80.** Repeated runs of the same question are far more correlated with each other than with a different question — which is expected (a purely informational question returns zero every time; a genuinely contested one might not), but it means **the current between-cluster significance test below is not valid.** Simulated false-positive rate for `proportions_ztest` comparing 10 test-cluster questions against 26 control-cluster questions, under a true null, at realistic heterogeneity: **22-24% across five different random seeds** — four to five times the nominal 5%.

**It gets worse than "the test is miscalibrated."** With only 7 topic-level clusters (1 test, 6 control), the finest possible p-value from *any* cluster-level randomization test is 1/7 ≈ 0.143 — mathematically incapable of reaching conventional significance regardless of the true effect size or which statistical model is used. A fancier model does not fix this; there are simply not enough independent clusters.

**The fix: change the primary comparison, don't try to rescue the old one.**

```sql
-- PRIMARY ANALYSIS: per-question paired difference, baseline vs after,
-- on the SAME questions. Pairing cancels the between-question variance
-- that makes the cluster-level test above invalid — this is the
-- comparison that actually has correct statistical coverage.
SELECT
    q.id,
    q.topic,
    ROUND(AVG(CASE WHEN r.checkpoint = 'baseline' THEN r.brand_mentioned END), 4) AS p_baseline,
    ROUND(AVG(CASE WHEN r.checkpoint = 'after'    THEN r.brand_mentioned END), 4) AS p_after
FROM runs r
JOIN questions q ON q.id = r.question_id
WHERE r.parse_ok = 1 AND q.topic = 'fixed_fee_positioning'
GROUP BY q.id, q.topic;
```

```python
# Paired bootstrap significance test on the per-question deltas above.
# Run after pulling the SQL result into a DataFrame `df` with columns
# p_baseline, p_after.
import numpy as np

def paired_bootstrap_test(deltas, n_boot=10000, seed=7):
    rng = np.random.default_rng(seed)
    k = len(deltas)
    boot_means = [rng.choice(deltas, size=k, replace=True).mean() for _ in range(n_boot)]
    ci_low, ci_high = np.percentile(boot_means, [2.5, 97.5])
    return ci_low, ci_high

deltas = (df["p_after"] - df["p_baseline"]).to_numpy()
ci_low, ci_high = paired_bootstrap_test(deltas)
print(f"mean delta = {deltas.mean():.1%}, 95% CI [{ci_low:.1%}, {ci_high:.1%}]")
if ci_low > 0:
    print("Significant increase — the CI excludes zero.")
else:
    print("Not significant at this sample size. Report that plainly.")
```

**The test-vs-control cluster comparison below is demoted to descriptive.** Report the deltas side by side as a drift check — it still does its job (catching "the whole market moved, not just Mighty"), it just doesn't get a p-value, because no valid one exists at 7 clusters. Do not run `proportions_ztest` on it.
```

- [ ] **Step 2: Relabel the existing "only chart that matters" section as descriptive-only**

Find `### The only chart that matters` and change its lead sentence from implying significance to being explicit that it's descriptive:

Replace:
```markdown
### The only chart that matters
```
with:
```markdown
### Test vs. control, by checkpoint (descriptive only — no p-value here, see above)
```

- [ ] **Step 3: Relabel the "Significance test" section**

Find `### Significance test` (the `proportions_ztest` Python block) and replace its heading and lead paragraph:

```markdown
### Between-cluster comparison — descriptive, not a significance test

Do not compute or report a p-value from this comparison — the ICC/cluster-count argument above shows no valid one exists at 7 clusters. This code stays for the drift check only: is the observed direction in `control_hits_after` consistent with market-wide movement, or isolated to test? Read the numbers, do not read a p-value into them.

```python
# Descriptive only — report the rates, not a p-value.
test_rate = test_hits_after / test_n_after
control_rate = control_hits_after / control_n_after
print(f"test: {test_rate:.1%} (n={test_n_after})")
print(f"control: {control_rate:.1%} (n={control_n_after})")
print(f"delta: {(test_rate - control_rate)*100:.1f}pp — descriptive, not a significance test")
```
```

- [ ] **Step 4: Add the matched-pairs analysis as a secondary, drift-robust comparison**

Add a new subsection after the framing cut, before "Spillover check":

```markdown
### Matched pairs — the drift-robust secondary comparison

8 fixed-fee-framed vs. generic-framed question pairs (`matched_pair_treatment`/`matched_pair_control` topics), added 2026-08-10. This is the only comparison in the design that's robust to market-wide drift over the 4-week window — the paired baseline→after test above would call a market-wide rise a win; this wouldn't, because both arms of every pair move together if the drift is real and general, not fixed-fee-specific.

```sql
SELECT
    q.notes AS pair_tag,
    q.topic,
    r.checkpoint,
    ROUND(AVG(r.brand_mentioned) * 100, 1) AS soa_pct,
    COUNT(*) AS n
FROM runs r
JOIN questions q ON q.id = r.question_id
WHERE r.parse_ok = 1 AND q.topic IN ('matched_pair_treatment', 'matched_pair_control')
GROUP BY q.notes, q.topic, r.checkpoint
ORDER BY q.notes, q.topic, CASE r.checkpoint WHEN 'baseline' THEN 1 WHEN 'after' THEN 2 END;
```

Read it pair by pair: if the treatment side of a pair moves and the control side doesn't, that's evidence the fixed-fee framing specifically mattered, not just general visibility drift. No canary data here — matched pairs only run at baseline and after (see `config.yaml`).
```

- [ ] **Step 5: Grep-verify no orphaned references remain**

```bash
grep -n "proportions_ztest" "C:\Dev\aeo\docs\aeo-code-appendix-mighty.md"
```
Every remaining hit should be inside the now-descriptive-only section from Step 3 or the per-surface note added earlier this session — none should be presented as a primary/headline test. Read each hit's surrounding context to confirm.

---

### Task 8: Update Appendix K, the plan doc, and `Appendix A`'s primary-surface pre-registration

**Files:**
- Modify: `docs/aeo-code-appendix-mighty.md` (`## Appendix K: Power Analysis`)
- Modify: `docs/aeo-30-day-plan-mighty.md`

- [ ] **Step 1: Add the 8-14pp evidence-backed ceiling to Appendix K**

In `## Appendix K: Power Analysis`, after the existing "baseline gate" section added earlier this session, add:

```markdown
### The +10pp assumption was a guess. It no longer needs to be.

Day 1's `day1-category-check.md` was parsed into its 20 model×question cells and checked for citations to the three planned Week 2 directory targets:

| domain | cells citing it |
|---|---|
| crunch.co.uk | 10/20 (50%) |
| reddit.com | 9/20 (45%) |
| contractoruk | 8/20 (40%) |
| limitedcompanyhelp | 6/20 (30%) |
| umbrellacompany | 3/20 (15%) |
| **any of the three planned directories** | **11/20 (55%)** |
| mightyaccounting.com | 1/20 (5%) |

The intervention has a real mechanism in 55% of answers. But being *listed* on a cited directory isn't the same as being *named* in the answer — the directory lists dozens of firms and the model selects a handful. At a plausible 15-25% conditional selection rate (a genuine estimate, not measured — the single weakest number in this section), the realistic ceiling is **8-14pp**, not an arbitrary +10pp. That range is what the power table above should be read against.

**Per-surface, this intervention has almost no mechanism on two of the three surfaces:**

| surface | planned directories present | reddit present |
|---|---|---|
| Perplexity | 4/5 | 4/5 |
| ChatGPT | 4/5 | 5/5 |
| Claude | 2/5 | 0/5 |
| Gemini | 1/5 | 0/5 |

Claude cites neither Reddit nor the target directories in this sample. Pooling surfaces when one is structurally unreachable by the treatment dilutes any real effect — this is why Perplexity is pre-registered as the primary surface (see the plan doc, dated before baseline).
```

- [ ] **Step 2: Pre-register Perplexity as the primary surface in the plan doc**

In `docs/aeo-30-day-plan-mighty.md`, in the Days 8-30 section, before the "Checkpoint 1: baseline" heading, add:

```markdown
### Pre-registered before baseline runs (2026-08-10)

**Perplexity is the primary surface for the significance test.** Testing across all 3 surfaces independently gives roughly 14% family-wise error before any of the clustering issues in Appendix M are even considered. Perplexity has the strongest measured intervention mechanism (4/5 Day-1 cells cite the planned directories, 4/5 cite Reddit — see Appendix K) and Mighty sits at genuine zero there. Claude and OpenAI results are reported alongside, without a p-value attached.

This is dated and written down *before* the baseline checkpoint runs, so it can't be quietly picked after seeing which surface looks best.
```

- [ ] **Step 3: Make the astroturfing/disclosure rule prominent, and specify intervention `type` logging**

In the Week 2 section of the plan doc, replace the current intervention list intro with:

```markdown
### Week 2 (Days 10-14ish): Make the changes, test topic only

**Standing rule, not a per-engagement judgement call: no manufactured evidence, ever.** No sock-puppet accounts, no seeded comments, no paid covert mentions, no invented customer experiences. If a mention isn't true and useful on its own terms, it doesn't get posted — for this case study and for any future client work. Any forum or social mention of Mighty discloses, **in the post itself**, that the poster isn't a Mighty customer and this is part of a measurement experiment — not only in these project notes.

Log each intervention in the `interventions` table with a distinct `type` — `directory`, `forum`, or `social` — not one undifferentiated "did stuff" entry. The column already exists; using it distinctly is what lets the after-checkpoint's `cited_urls` data attribute any observed movement to a specific lever.

Only these are in play, given the surprise decision:
```
(then the existing three bullet points continue unchanged)

- [ ] **Step 4: Add the platform-risk paragraph**

Find Part 0 or the framing section near the top of the plan doc (wherever the project's positioning is stated) and add:

```markdown
**Platform risk is a feature of the positioning, not a threat to it.** OpenAI, Google, Anthropic and Perplexity can change models, retrieval, citation behaviour and pricing overnight — this project has already been bitten by exactly that once, when `gpt-4o-search-preview` turned out to be past its shutdown date mid-build. A business whose value is "we know the algorithm" breaks every time that happens. One whose value is "we continuously measure what changed" gets stronger each time it does. That's the actual moat, not the Python code.
```

- [ ] **Step 5: Grep-verify dates and no contradictions**

```bash
grep -n "2026-08-10" "C:\Dev\aeo\docs\aeo-30-day-plan-mighty.md" "C:\Dev\aeo\docs\aeo-code-appendix-mighty.md" | tail -20
```
Confirm every new section added in this task carries the date, and skim for any leftover "+10pp" or "run this test to find significance" language elsewhere in the docs that now contradicts Task 7/8's corrections (matches the sync-sweep pattern used every prior correction this session).

---

### Task 9: Final sync sweep, log.md entry, cost re-verification

**Files:**
- Modify: `log.md`
- No other file changes — this task is verification and documentation only.

- [ ] **Step 1: Full re-verification pass**

```bash
cd /c/Dev/aeo && source venv/Scripts/activate
python -m py_compile src/rig.py src/estimate_cost.py src/parser.py && echo "syntax OK"

python -c "
import sqlite3, pandas as pd
conn = sqlite3.connect('src/aeo.db')
print('cohort/topic:', conn.execute('SELECT cohort, topic, COUNT(*) FROM questions GROUP BY cohort, topic ORDER BY cohort').fetchall())
print('runs empty:', conn.execute('SELECT COUNT(*) FROM runs').fetchone())
cols = {r[1] for r in conn.execute('PRAGMA table_info(runs)').fetchall()}
assert {'checkpoint','recommended','recommendation_rank'}.issubset(cols)
print('schema has all corrections: PASS')
"

cd src && python estimate_cost.py all
```

- [ ] **Step 2: Record the real updated cost total**

Read the `estimate_cost.py all` output from Step 1 and write it into both `docs/aeo-code-appendix-mighty.md` (the "Real cost and runtime" note in Appendix H) and `docs/aeo-30-day-plan-mighty.md` (the "Billing caps" section) — replace the existing ~$63 figure with whatever the matched pairs push it to. Do not guess the number; use exactly what the command printed.

- [ ] **Step 3: Write the `log.md` entry**

Append a new section to `log.md` following this project's established format (see every prior 2026-08-10 entry for the pattern — lead with what changed, why, and what was verified):

```markdown
## Implemented the external-review corrections plan

Built `docs/superpowers/plans/2026-08-10-external-review-corrections.md` — 9 tasks covering: `recommended`/`recommendation_rank` added to schema and parser (mention-vs-recommendation is now a real distinction, verified against the exact "however, Gorilla has more experience" adversarial case from the critique); `config.yaml` added so `rig.py`/`estimate_cost.py` derive their topic/brand config from one shared source instead of two hand-synced copies; 8 matched question pairs added as a market-drift-robust secondary comparison, running only at baseline/after (not canary); `q026` recovered with a `borderline` tag and vote fractions stored on the 4 borderline `fixed_fee_positioning` rows rather than left as invisible thresholding noise.

**The real fix, not just an addition:** Appendix M's primary significance test changed from a between-cluster `proportions_ztest` (verified via simulation to have a 22-24% false-positive rate against a nominal 5%, robust across 5 random seeds) to a per-question paired bootstrap on baseline→after. The old test is demoted to descriptive-only, with the reasoning made explicit in the doc: with only 7 topic clusters, no valid cluster-level significance test exists at any sophistication, so "add a fancier model later" was closed off as an option, not deferred.

Appendix K's intervention-ceiling assumption (+10pp, previously unsourced) replaced with an 8-14pp estimate computed from real Day-1 citation data (55% of answers cite a planned directory target), plus the finding that Claude and Gemini show almost no citation mechanism for the planned intervention specifically (0/5 Reddit, ≤2/5 directories) — which is why Perplexity is now pre-registered, dated, as the primary surface before baseline runs.

Real cost total after the matched-pairs addition: [insert Step 2's number]. Nothing has been spent — `runs` table confirmed empty after the DB rebuild.
```

- [ ] **Step 4: Stage and review the diff**

```bash
cd /c/Dev/aeo
git status
git diff --stat
```

Do not commit yet — this plan's execution ends at "changes made and verified locally." Committing and pushing happens only when the user explicitly asks, same as every other point this session.

---

## Self-Review Notes (completed during plan authoring, not a separate pass)

- **Spec coverage:** all 9 items from the design doc's "Before baseline" list (A1-A9) map to a task above. Items in "C" (question-sourcing cross-check, Google AI Overviews, agencies-in-parallel, naming) are explicitly out of scope for this plan — they're non-blocking per the design doc and can be a separate, later plan.
- **Type consistency:** `runs_for_topic(topic)` signature in `rig.py` (Task 2/3) matches the one already used in `run_cycle()`; `estimate_cost.py`'s `runs_for_topic(topic, mode)` keeps its existing two-argument signature (it was never module-global `MODE`-based like `rig.py`'s) — not unified into one signature across files, since they're genuinely different call patterns and forcing them identical would be a needless coupling.
- **No placeholders:** every step has literal code, not a description of code.
