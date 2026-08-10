# AEO Code Appendix — Mighty Accounting

Companion to [aeo-30-day-plan-mighty.md](aeo-30-day-plan-mighty.md). Everything here is identical in structure to the general version — the rig doesn't care what brand it's tracking — but every example, config value, and illustrative query below is now specific to Mighty and UK contractor accountancy, so you can hand this straight to Claude Code without translating anything yourself.

**Assumed:** you know SQL well. You've not really used Python or APIs. Everything below assumes that and explains accordingly.

**How to use this with Claude Code:** don't type this out. Paste an appendix section into Claude Code and say "build this, explain each file as you go." You're the PM. This doc is the spec.

---

## Contents

- [Appendix A: Setting Up the Box](#appendix-a-setting-up-the-box)
- [Appendix B: API Setup](#appendix-b-api-setup)
- [Appendix C: Question Expansion](#appendix-c-question-expansion)
- [Appendix D: questions.csv](#appendix-d-questionscsv)
- [Appendix E: Python Primer](#appendix-e-python-primer)
- [Appendix F: Database](#appendix-f-database)
- [Appendix G: The Parser](#appendix-g-the-parser)
- [Appendix H: The Rig](#appendix-h-the-rig)
- [Appendix I: The Queries](#appendix-i-the-queries)
- [Appendix J: Cohort Assignment](#appendix-j-cohort-assignment)
- [Appendix K: Power Analysis](#appendix-k-power-analysis)
- [Appendix L: robots.txt Check](#appendix-l-robotstxt-check)
- [Appendix M: Analysis](#appendix-m-analysis)

---

## Appendix A: Setting Up the Box

*Referenced from: Part 2 — Where This Runs*

Nothing here changes for Mighty — this is pure infrastructure. Included for completeness.

### Phase 1: Local (Days 1-5) — do this first

```bash
mkdir aeo-rig && cd aeo-rig
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install requests python-dotenv anthropic openai pandas
pip freeze > requirements.txt
```

**What just happened, in SQL terms:** `venv` is like creating a separate database for this project. `pip install` is loading the libraries you'll query against. `requirements.txt` is the DDL — the recipe to rebuild it identically elsewhere.

### Phase 2: The Hetzner box (before Day 15)

**Step 1 — Create the server.**
1. Sign up at hetzner.com/cloud
2. New Project → Add Server
3. Location: **Falkenstein** or **Helsinki**
4. Image: **Ubuntu 24.04**
5. Type: **CX22** (2 vCPU, 4GB RAM, 40GB NVMe) — €4.50/month
6. SSH key: add yours
7. Create

**If you don't have an SSH key:**
```bash
ssh-keygen -t ed25519 -C "your@email.com"
cat ~/.ssh/id_ed25519.pub
# Copy that output into Hetzner's SSH key box
```

**Step 2 — First login and basic hardening.**
```bash
ssh root@YOUR_SERVER_IP
apt update && apt upgrade -y
adduser tess
usermod -aG sudo tess
rsync --archive --chown=tess:tess ~/.ssh /home/tess
ufw allow OpenSSH
ufw enable
exit
ssh tess@YOUR_SERVER_IP
```

**Step 3 — Python on the box.**
```bash
sudo apt install python3-pip python3-venv git -y
```

**Step 4 — VS Code Remote-SSH.**
1. Install the **Remote - SSH** extension in VS Code
2. Cmd/Ctrl+Shift+P → "Remote-SSH: Connect to Host"
3. Enter `tess@YOUR_SERVER_IP`

**Step 5 — Get your code there.**
```bash
git clone https://github.com/yourusername/aeo-rig.git
cd aeo-rig
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Step 6 — Checkpoint runs, not a nightly scheduler.**

Corrected 2026-08-10: a nightly `0 3 * * *` cron entry running the full weighted cycle every night for 30 nights was never reconciled against the stated month's budget — real measured cost is ~$18-19 per full cycle, so 30 nights is $500+. Nothing in the analysis needs daily granularity; it needs three deliberate checkpoints. **Do not add a recurring cron entry.** Instead, run manually (or via a one-off `at` job) at each checkpoint:

```bash
python estimate_cost.py baseline   # dry-run check first, every time
python rig.py baseline             # once, after Day 5 validation passes

# ... Day 8-9 cohort assignment, Week 2 interventions, wait a few days ...

python estimate_cost.py canary
python rig.py canary               # once, partway through the wait period

# ... finish the wait period (1-2 weeks total) ...

python estimate_cost.py after
python rig.py after                # once, in Week 3
```

If the Hetzner box is still wanted for reliability (so a checkpoint run isn't lost to a closed laptop lid), that's fine — just don't wire a recurring cron entry back in. SSHing in and running each command by hand, or a single `at`-scheduled job per checkpoint, both work.

**Step 7 — Verify a checkpoint actually ran.**
```bash
sqlite3 ~/aeo-rig/aeo.db "SELECT checkpoint, COUNT(*), DATE(ts) FROM runs GROUP BY checkpoint, DATE(ts);"
```

### Backups

```bash
# after each checkpoint run, snapshot manually — no recurring cron needed for 3 total runs
cp /home/tess/aeo-rig/aeo.db /home/tess/backups/aeo-$(date +\%Y\%m\%d)-$(cat /tmp/last_checkpoint).db
```

```bash
# pull a copy down periodically
scp tess@YOUR_SERVER_IP:~/aeo-rig/aeo.db ./aeo-backup.db
```

---

## Appendix B: API Setup

*Referenced from: Part 2 — The API cost maths*

Three accounts, same as any brand.

| Provider | Where | Notes |
|---|---|---|
| Perplexity | perplexity.ai/settings/api | Your workhorse. Add ~$5 credit. |
| Anthropic | console.anthropic.com | Claude as surface + the parser |
| OpenAI | platform.openai.com | ChatGPT as surface |

**Brave dropped, parked for later.** The original design used Brave Search as a fourth, independent "retrieval set" surface. Two things changed that: Brave killed its no-card free tier in Feb 2026 (now metered, card required, no spend cap), and — separately from cost — Claude's own `web_search` tool is strongly believed to already run on Brave's index under the hood, making a standalone Brave call largely redundant with the Claude surface anyway. Instead, the rig now extracts citations directly from Perplexity, Claude, and OpenAI's own responses (see Appendix H) — higher-fidelity data, since it's exactly what each platform used for that specific answer, at no extra cost. **Revisit Brave (or Serper, a cheap Google-backed alternative) later only if a few weeks of real data show genuine gaps** — e.g. runs where Mighty isn't mentioned and none of the three platforms' own citations explain why.

**Gemini: planned, but deliberately not part of this initial build.** Part 0 and Day 1's manual check both promise coverage "across four AI platforms," and Day 1 already found Mighty at 0% on Gemini specifically by hand — that's real baseline data currently unused by the automated rig. Dropping it silently would mean carrying a checkable, easily-embarrassing gap into any pitch ("show me the Gemini numbers"). It should be added — Gemini's Search grounding API (`google-genai` SDK, `Tool(google_search=GoogleSearch())`) follows the same `question → (answer, urls)` shape already used for the other three, and is comfortably inside budget (5,000 free grounded calls/month, then $14/1k; some spillover into the paid tier is possible since a single prompt can trigger multiple internal search queries, but realistic worst case is still only ~£10-30 for the month).

**Sequencing matters, though.** The single biggest execution risk flagged for this project is silent unattended failure — a rig that breaks at 3am with nobody noticing, corrupting the before/after comparison the whole experiment depends on. Adding a fourth SDK's citation/annotation shape while the first three are still being validated as reliable stacks integration risk at exactly the point where debugging capability (first Python project) is lowest. **Build and stabilize the 3-surface rig first — through Day 5's 30-sample parser validation — before adding Gemini as a fast-follow, once that foundation is proven solid and before the real before/after comparison run.** When Gemini is added, give it its own mini validation pass (10-15 sample answers is enough) rather than assuming it inherits the Day 5 check that ran without it.

### SET BILLING CAPS. NOW. BEFORE ANY CODE.

Corrected 2026-08-10, revised again same day after the power analysis pushed `fixed_fee_positioning`'s N from 5 to 10 (see Appendix K): £15 was set before real per-call costs were measured. Web search results dominate token count on both Claude and OpenAI — real measured cost is ~$0.035-0.05/call (Claude, with `max_uses=1`) and ~$0.065-0.10/call (OpenAI, with `search_context_size="low"`, high variance). Current `estimate_cost.py all` total across the three checkpoints: **Perplexity ~$4.83, Claude ~$24.15, OpenAI ~$33.81, grand total ~$63.** **Set Anthropic to £25-30 and OpenAI to £30-35** — OpenAI's total sits close enough to a £25 cap that a single unlucky high-variance run could trip it mid-checkpoint. Perplexity stays cheap; £5-10 is plenty. Run `python estimate_cost.py <mode>` before every real checkpoint regardless of the cap — that's the actual insurance, the cap is just the backstop for a loop bug.

### `.env` and `.gitignore`

```
PERPLEXITY_API_KEY=pplx-xxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxxxx
```

```
.env
venv/
*.db
__pycache__/
logs/
```

**The `.gitignore` is not optional.** Without it you commit your keys to GitHub, bots find them within minutes, and you wake up to someone else's bill.

### Smoke test

```python
# test_apis.py
import os, requests
from dotenv import load_dotenv

load_dotenv()

def test_perplexity():
    r = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers={"Authorization": f"Bearer {os.getenv('PERPLEXITY_API_KEY')}"},
        json={
            "model": "sonar",
            "messages": [{"role": "user", "content": "What is 2+2?"}],
        },
        timeout=30,
    )
    print("Perplexity:", r.status_code)
    print(r.json()["choices"][0]["message"]["content"][:200])

if __name__ == "__main__":
    test_perplexity()
```

Run this on Day 3 before writing anything else.

---

## Appendix C: Question Expansion

*Referenced from: Day 2 — Question research*

Paste into Claude, one seed at a time. **Example, using a real Mighty-relevant seed:**

```
I'm researching how real people phrase questions when they're
looking for an accountant for their UK limited company, as a
contractor or freelancer.

Seed question: "best accountant for a small limited company that
won't feel like a big impersonal firm"

Generate 20 different ways a real person might ask this to an AI
assistant. Vary:
- formality (some typed quickly, frustrated with a current
  accountant, lowercase, informal)
- specificity (some vague, some very specific about IR35 status,
  turnover, or whether they're a first-time company director)
- framing (some ask for a recommendation, some describe a problem
  with their current accountant, some ask "is X any good")
- length (some 5 words, some a full paragraph explaining their
  situation)

Do NOT make them all polished. Real people type things like "sick
of my accountant never replying to emails, anyone recommend
someone actually good for a one person ltd co".

Output as a plain list, one per line, no numbering, no commentary.
```

### Why phrasings matter this much

You're not measuring "does Mighty rank for keyword X." You're measuring **P(Mighty appears | someone asks about this intent, however they phrase it)**.

That's a distribution over phrasings. This matters even more for accountancy than for a consumer app, because the emotional register varies hugely — someone typing "IR35 compliant accountant for contractors" is in research mode; someone typing "my accountant hasn't replied in three weeks, need someone new urgently" is in switching mode, and the AI likely retrieves different pages for each even though both are "looking for an accountant."

### Other seed questions worth running through this same expansion

Pull these from your own Day 2 Step 1 brain dump, but if you want starting seeds beyond the one above:

- "accountant for IT contractor IR35 inside vs outside"
- "how much should I pay for a limited company accountant"
- "fixed fee accountant no hidden costs contractor"
- "switching accountants mid tax year limited company"
- "accountant that actually understands one person consultancies"

### Sanity check your own list

Once you have ~60, read them cold and ask: *would I have typed this while genuinely frustrated with my own accounting admin, or while first setting up Tess Turner Ltd?* Anything that reads like marketing copy, cut it.

---

## Appendix D: questions.csv

*Referenced from: Day 2 — Question research*

### Schema

| Column | Type | Notes |
|---|---|---|
| `id` | text | `q001`, `q002`… stable, never reuse |
| `text` | text | The question, exactly as asked |
| `topic` | text | Cluster slug: `ir35_compliance`, `fixed_fee_positioning` |
| `tier` | text | `head` / `mid` / `long` |
| `is_product` | bool | Did named firms appear when tested? |
| `cohort` | text | `test` / `control` — filled Day 8-9 (no holdout tier — see Appendix J) |
| `notes` | text | Anything useful |

### Example rows, using Mighty's actual competitor set and clusters

```csv
id,text,topic,tier,is_product,cohort,notes
q001,best accountant for uk limited company contractor,general_recommendation,head,TRUE,,Caroola+GoForma named
q002,fixed fee accountant no big agency feel small company,fixed_fee_positioning,mid,TRUE,,Mighty's home turf - check closely
q003,how do i register a limited company,new_company_setup,long,FALSE,,NO FIRMS NAMED - delete
q004,switching accountants mid tax year limited company uk,switching_accountants,mid,TRUE,,check which firms recommended for switchers
q005,what is ir35,ir35_compliance,head,FALSE,,informational - delete
q006,accountant for it contractor inside ir35,ir35_compliance,mid,TRUE,,Caroola/SJD dominant historically here
```

Note `q003` and `q005`. Both are perfectly reasonable questions a contractor would ask. Both are worth **zero** — no named firms in the answer, ever. Delete them.

### Loading it

```python
import pandas as pd

questions = pd.read_csv("questions.csv")
questions = questions[questions.is_product == True]  # the filter
print(f"{len(questions)} product questions across {questions.topic.nunique()} topics")
```

### Step 5, scripted (`step5_product_filter.py`)

Added after a manual spot-check (web search, not Perplexity, so treat as
directional) surfaced two things worth fixing before running this for
real:

1. `new_company_setup`-style "do I need an accountant" questions mostly
   return pure informational content, no named firms — matches the
   plan's own worked example (`q003` in the sample rows above). Expect
   this cluster to lose the most rows.
2. `freelancer_agency` phrasings without an explicit UK/limited-company
   anchor pulled entirely US-based CPA firms in the spot-check. All 5
   rows in that cluster were rewritten to include "uk" and "limited
   company" — every other cluster naturally anchors via "IR35",
   "limited company", or "contractor", but authored phrasings need it
   added explicitly.

This script runs the real filter via the Perplexity API once Appendix
B's smoke test passes, using an LLM call (not regex — same reasoning
as Appendix G) to judge whether a specific firm got named. It only
touches rows where `is_product` is blank or `BORDERLINE`, so manually
spot-checked rows are left alone, and it saves after every row so a
crash mid-run doesn't lose progress.

```python
# step5_product_filter.py
import os, csv, time, random
import requests
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

CSV_PATH = "questions.csv"
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

FILTER_PROMPT = """You are checking whether an AI assistant's answer
names any SPECIFIC accountancy firm or accounting company (a proper
noun business name — e.g. "Crunch", "Gorilla Accounting", "Mighty
Accounting"), as opposed to giving purely generic/informational advice
with no named providers.

Rules:
- Software platforms (Xero, FreeAgent, Pandle, QuickBooks) do NOT
  count as accountancy firms on their own.
- Generic advice ("hire a qualified accountant", "look for someone
  ACCA-certified") with no actual named business does NOT count.
- A directory or comparison site listing named firms DOES count.
- If in doubt, answer TRUE only if you could point to an actual firm
  name in the text.

Answer with exactly one word: TRUE or FALSE.

ANSWER TO CHECK:
{answer}"""


def ask_perplexity(question):
    r = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers={"Authorization": f"Bearer {os.getenv('PERPLEXITY_API_KEY')}"},
        json={
            "model": "sonar",
            "messages": [{"role": "user", "content": question}],
        },
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def is_product_question(answer_text):
    msg = anthropic_client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=10,
        messages=[{
            "role": "user",
            "content": FILTER_PROMPT.format(answer=answer_text),
        }],
    )
    raw = msg.content[0].text.strip().upper()
    return "TRUE" in raw


def run_filter():
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    fieldnames = list(rows[0].keys())
    to_check = [r for r in rows if not r["is_product"] or r["is_product"] == "BORDERLINE"]

    print(f"{len(rows)} total questions, {len(to_check)} need checking")

    for i, row in enumerate(to_check, 1):
        try:
            answer = ask_perplexity(row["text"])
            result = is_product_question(answer)
            row["is_product"] = "TRUE" if result else "FALSE"
            note = f"scripted Step 5 check, {time.strftime('%Y-%m-%d')}"
            row["notes"] = (row["notes"] + " | " + note).strip(" |") if row["notes"] else note
            print(f"[{i}/{len(to_check)}] {row['id']}: {row['is_product']} — {row['text'][:60]}")
        except Exception as e:
            print(f"[{i}/{len(to_check)}] {row['id']}: ERROR — {e}")
            row["is_product"] = ""

        # save after every row so a crash doesn't lose progress
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        time.sleep(random.uniform(0.5, 1.5))

    kept = sum(1 for r in rows if r["is_product"] == "TRUE")
    deleted = sum(1 for r in rows if r["is_product"] == "FALSE")
    print(f"\nDone. {kept} product questions kept, {deleted} flagged for deletion.")
    print("Review the FALSE rows before deleting — spot-check a handful first.")


if __name__ == "__main__":
    run_filter()
```

Drop this in your `aeo-rig` folder alongside `questions.csv` and run
`python step5_product_filter.py` once your Perplexity key is live.

---

## Appendix E: Python Primer

*Referenced from: Days 3-5 — Build the rig*

Unchanged — no brand-specific content here. For someone fluent in SQL:

| SQL concept | Python equivalent |
|---|---|
| A table | A `list` of `dict`s, or a pandas DataFrame |
| A row | A `dict`: `{"id": "q001", "text": "..."}` |
| `WHERE x = 1` | `[r for r in rows if r["x"] == 1]` |
| `SELECT col` | `[r["col"] for r in rows]` |
| A stored procedure | A `def` function |
| `NULL` | `None` |
| A cursor loop | `for row in rows:` |

### The six things you need

**1. Variables** — no declaration, no types.
```python
brand = "Mighty Accounting"
n_runs = 5
```

**2. Dicts** — a row.
```python
row = {"question_id": "q001", "surface": "perplexity", "hit": True}
print(row["surface"])
```

**3. Lists** — a result set.
```python
surfaces = ["perplexity", "claude", "openai"]
for s in surfaces:
    print(s)
```

**4. Functions** — a stored proc.
```python
def ask(question, surface):
    # do the thing
    return answer
```

**5. f-strings** — string concatenation that doesn't hurt.
```python
print(f"Ran {n_runs} times for {brand}")
```

**6. try/except** — error handling.
```python
try:
    answer = ask(q, "perplexity")
except Exception as e:
    print(f"Failed: {e}")
    answer = None
```

### Indentation is syntax

Python has no `BEGIN`/`END` or braces. Indentation *is* the block structure. Four spaces. Be consistent or nothing runs.

---

## Appendix F: Database

*Referenced from: The database — one table*

Schema is entirely brand-agnostic — same table for Mighty as for anything else.

### Full schema

Corrected 2026-08-10: `cohort` no longer includes `'holdout'` (dropped — see Appendix J) and `runs` gained a `checkpoint` column (see Appendix H).

```sql
-- schema.sql

CREATE TABLE IF NOT EXISTS questions (
    id          TEXT PRIMARY KEY,
    text        TEXT NOT NULL,
    topic       TEXT NOT NULL,
    tier        TEXT CHECK (tier IN ('head','mid','long')),
    is_product  BOOLEAN NOT NULL,
    cohort      TEXT CHECK (cohort IN ('test','control')),
    notes       TEXT
);

CREATE TABLE IF NOT EXISTS runs (
    run_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id       TEXT NOT NULL REFERENCES questions(id),
    surface           TEXT NOT NULL,
    model             TEXT NOT NULL,
    run_index         INTEGER NOT NULL,
    ts                TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    raw_answer        TEXT NOT NULL,
    cited_urls        TEXT,          -- JSON array
    brand_mentioned   BOOLEAN,
    brand_position    INTEGER,       -- 1 = named first; NULL if absent
    competitors_named TEXT,          -- JSON array
    recommended         BOOLEAN,     -- true only if brand is actively recommended, not merely mentioned
    recommendation_rank INTEGER,     -- 1 = first/primary recommendation; NULL if not recommended
    parse_ok          BOOLEAN DEFAULT 1,
    error             TEXT,
    checkpoint        TEXT CHECK (checkpoint IN ('baseline','canary','after'))
);

-- Log every intervention. This is your experiment audit trail.
CREATE TABLE IF NOT EXISTS interventions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ts          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    topic       TEXT NOT NULL,
    cohort      TEXT NOT NULL,
    type        TEXT,   -- new_page | content_enhancement | citation
    description TEXT,
    url         TEXT
);

CREATE INDEX IF NOT EXISTS idx_runs_question ON runs(question_id);
CREATE INDEX IF NOT EXISTS idx_runs_ts       ON runs(ts);
CREATE INDEX IF NOT EXISTS idx_runs_surface  ON runs(surface);
```

### Setup

```bash
sqlite3 aeo.db < schema.sql
sqlite3 aeo.db ".tables"
```

### Loading questions

```python
import sqlite3, pandas as pd

conn = sqlite3.connect("aeo.db")
df = pd.read_csv("questions.csv")
df = df[df.is_product == True]
df.to_sql("questions", conn, if_exists="replace", index=False)
conn.commit()
```

---

## Appendix G: The Parser

*Referenced from: Design decision 3 — Parse with an LLM*

### Why not just search for the word

```python
brand_mentioned = "Mighty" in answer   # DO NOT DO THIS
```

Breaks on:
- "a **mighty** fine service" → false positive (it's the adjective, not the firm)
- "**Mighty** Networks" (a different, unrelated company) → false positive
- "MightyRecruiter", "Mighty Well" and similar unrelated brands → false positive
- "the small fixed-fee firm run by Mark and James" (description without the name) → false negative
- "Mighty Accounting" vs "Mighty" vs "mightyaccounting.com" → inconsistent

And it can't tell you *position*, *sentiment*, or *which competitors were named*.

### The LLM parser

```python
import json, os
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

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


def parse_answer(answer_text, brand="Mighty Accounting"):
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",   # cheap; this is easy work
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": PARSE_PROMPT.format(brand=brand, answer=answer_text),
        }],
    )
    raw = msg.content[0].text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"parse_ok": False, "raw": raw}
```

### Validate the parser before trusting it

Do this on Day 5, non-negotiable — and for Mighty specifically, deliberately include a few answers you'd expect to be tricky: any that mention "Mighty Networks" or use "mighty" as a plain adjective, so you can confirm the parser isn't false-positiving on those.

```python
sample = conn.execute(
    "SELECT run_id, raw_answer FROM runs ORDER BY RANDOM() LIMIT 30"
).fetchall()

for run_id, answer in sample:
    result = parse_answer(answer)
    print(f"\n--- {run_id} ---")
    print(answer[:300])
    print(f"PARSER SAYS: {result}")
    input("Correct? (note disagreements) ")
```

---

## Appendix H: The Rig

*Referenced from: Days 3-5 — Build the rig*

Built for real 2026-08-10, not just pasted from this appendix — see `src/rig.py` for the current file, and log.md for the full history of what changed and why. The version originally drafted here had three real bugs (a stale/dead OpenAI model past its shutdown date, a Claude response-parsing path that crashed on any search error, a missing import) and one unreconciled design flaw (nightly cron cost vs. the stated month's budget, off by ~25x). All fixed. Current shape:

```python
# rig.py
import os, sys, json, time, sqlite3, random
from datetime import datetime
from pathlib import Path
import requests
import yaml
from dotenv import load_dotenv
from anthropic import Anthropic
from openai import OpenAI

from parser import parse_answer

load_dotenv()

DB = Path(__file__).resolve().parent / "aeo.db"

MODE = sys.argv[1] if len(sys.argv) > 1 else "baseline"
assert MODE in ("baseline", "canary", "after"), "usage: python rig.py [baseline|canary|after]"

CLAUDE_MODEL  = "claude-sonnet-5"
OPENAI_MODEL  = "gpt-5.6-terra"

anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
openai_client    = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Loaded from config.yaml (added 2026-08-10) so the rig is reusable for a
# different brand/client by swapping one file instead of editing code.
# See Appendix J for the cohort/tier rationale.
def load_config():
    with open(Path(__file__).resolve().parent / "config.yaml") as f:
        return yaml.safe_load(f)

_config = load_config()

BRAND               = _config["brand"]
TEST_TOPICS         = set(_config["test_topics"])
NEAR_CONTROL_TOPICS = set(_config["near_control_topics"])
MATCHED_PAIR_TOPICS = set(_config["matched_pair_topics"])
BASELINE_AFTER_RUNS = _config["baseline_after_runs"]
DEFAULT_BASELINE_AFTER_RUNS = _config["default_baseline_after_runs"]
CANARY_RUNS_TEST_NEAR = _config["canary_runs_test_near"]
CANARY_RUNS_FAR       = _config["canary_runs_far"]
PRIMARY_SURFACE       = _config["primary_surface"]


def runs_for_topic(topic):
    if MODE == "canary":
        if topic in MATCHED_PAIR_TOPICS:
            return 0  # matched pairs run at baseline/after only — see config.yaml
        if topic in TEST_TOPICS or topic in NEAR_CONTROL_TOPICS:
            return CANARY_RUNS_TEST_NEAR
        return CANARY_RUNS_FAR
    return BASELINE_AFTER_RUNS.get(topic, DEFAULT_BASELINE_AFTER_RUNS)


# ---------- SURFACES ----------

def ask_perplexity(question):
    r = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers={"Authorization": f"Bearer {os.getenv('PERPLEXITY_API_KEY')}"},
        json={
            "model": "sonar",
            "messages": [{"role": "user", "content": question}],
            "temperature": 1.0,
        },
        timeout=60,
    )
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"], data.get("citations", [])


def ask_claude(question):
    # web_search_tool_result.content is a LIST on success, a SINGLE error
    # object on failure — never assume it's iterable. max_uses=1 caps
    # re-searching (real measured cost: ~$0.08-0.10/call unset, ~$0.035-0.05
    # capped). Bounded pause_turn resumption per Anthropic's documented fix.
    messages = [{"role": "user", "content": question}]
    text = ""
    urls = []

    for _ in range(3):
        msg = anthropic_client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1024,
            tools=[{
                "type": "web_search_20250305",
                "name": "web_search",
                "max_uses": 1,
            }],
            messages=messages,
        )

        for block in msg.content:
            if block.type == "text":
                text += block.text
                for citation in getattr(block, "citations", None) or []:
                    url = getattr(citation, "url", None)
                    if url:
                        urls.append(url)
            elif block.type == "web_search_tool_result":
                content = getattr(block, "content", None)
                if isinstance(content, list):
                    for result in content:
                        url = getattr(result, "url", None)
                        if url:
                            urls.append(url)

        if msg.stop_reason != "pause_turn":
            break
        messages = [
            {"role": "user", "content": question},
            {"role": "assistant", "content": msg.content},
        ]

    return text, list(dict.fromkeys(urls))


def ask_openai(question):
    # Responses API, not chat.completions + gpt-4o-search-preview (dead,
    # shutdown 2026-07-23). search_context_size="low" is a real cost lever
    # per OpenAI's docs but high-variance in practice — treat as a mild
    # average saving, not a guarantee.
    resp = openai_client.responses.create(
        model=OPENAI_MODEL,
        tools=[{"type": "web_search", "search_context_size": "low"}],
        input=question,
    )
    urls = []
    for item in getattr(resp, "output", None) or []:
        if getattr(item, "type", None) != "message":
            continue
        for content in getattr(item, "content", None) or []:
            for annotation in getattr(content, "annotations", None) or []:
                if getattr(annotation, "type", None) == "url_citation":
                    url = getattr(annotation, "url", None)
                    if url:
                        urls.append(url)
    return resp.output_text, list(dict.fromkeys(urls))


SURFACES = {
    "perplexity": (ask_perplexity, "sonar"),
    "claude":     (ask_claude,     CLAUDE_MODEL),
    "openai":     (ask_openai,     OPENAI_MODEL),
}


# ---------- MAIN LOOP ----------

def run_cycle():
    conn = sqlite3.connect(DB)
    questions = conn.execute(
        "SELECT id, text, topic FROM questions WHERE is_product = 1"
    ).fetchall()

    total_calls = sum(runs_for_topic(topic) for _, _, topic in questions) * len(SURFACES)
    print(f"[{datetime.now()}] Starting {MODE} cycle: "
          f"{len(questions)} questions x {len(SURFACES)} surfaces, weighted -> {total_calls} calls")

    for qid, qtext, topic in questions:
        n_runs = runs_for_topic(topic)
        for surface_name, (fn, model) in SURFACES.items():
            for run_index in range(n_runs):
                try:
                    answer, urls = fn(qtext)
                    parsed = (parse_answer(answer, BRAND)
                              if answer else {"brand_mentioned": None})

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
                    conn.commit()

                except Exception as e:
                    print(f"  ERROR {qid}/{surface_name}/{run_index}: {e}")
                    conn.execute("""
                        INSERT INTO runs (
                            question_id, surface, model, run_index, ts,
                            raw_answer, parse_ok, error, checkpoint
                        ) VALUES (?,?,?,?,?,?,?,?,?)
                    """, (qid, surface_name, model, run_index,
                          datetime.now().isoformat(), "", 0, str(e), MODE))
                    conn.commit()

                time.sleep(random.uniform(0.5, 1.5))

    conn.close()
    print(f"[{datetime.now()}] {MODE} cycle complete")


if __name__ == "__main__":
    run_cycle()
```

### The design decisions, called out (unchanged rationale, still applies)

**`temperature: 1.0`.** You're measuring the world as real users experience it, including the variance. Don't suppress it.

**try/except around every call.** One blip shouldn't kill the whole checkpoint.

**`time.sleep` with jitter.** Avoids rate limits, avoids hammering in lockstep.

**Commit per row.** A crash at question 30 shouldn't lose the ones before it.

**Errors get a row, not silence.** Ambiguity between "failed" and "never ran" corrupts your denominators.

**Citations come from the platforms themselves, not a separate search call.** `ask_claude` and `ask_openai` pull the URLs each platform actually used for that specific answer (Claude via `web_search_tool_result`/`citations` blocks, OpenAI via `response.output[].content[].annotations`), the same way `ask_perplexity` already did via its `citations` field. This replaced a fourth "independent" surface (Brave) that turned out to be redundant with Claude's own retrieval anyway — see the note in Appendix B.

**`checkpoint` column, `MODE` argv, weighted + tiered run counts.** Replaces the flat `N_RUNS` and nightly cron — see the cost correction above and Appendix J for the cohort tiers.

### Real cost and runtime (measured, not estimated)

The original "~2s/call, ~30 minutes" estimate assumed plain chat calls. Web search calls are slower and far heavier on tokens than that — real measured cost per call: Perplexity ~$0.01, Claude ~$0.035-0.05 (with `max_uses=1`), OpenAI ~$0.065-0.10 (`search_context_size="low"`, high variance). Run `python estimate_cost.py <mode>` before every real checkpoint to get the current number against the actual question set — don't rely on this appendix's figures staying accurate. As of 2026-08-10 (after `fixed_fee_positioning`'s N raised to 10 per Appendix K's power check, and the 8 matched pairs added per the external-review corrections): **baseline/after ≈ $35.62 each (822 calls), canary ≈ $12.35 (285 calls, matched pairs excluded), total ≈ $83.59 across all three.** Real time per call is more like 5-15s given search latency — expect **75-226 minutes (up to ~3.8hr) for baseline/after**, less for canary.

---

## Appendix I: The Queries

*Referenced from: Defining Share of Answers*

### Share of Answers by topic × surface

```sql
SELECT
    q.topic,
    r.surface,
    COUNT(*)                                AS n_runs,
    SUM(r.brand_mentioned)                  AS n_hits,
    ROUND(AVG(r.brand_mentioned) * 100, 1)  AS soa_pct
FROM runs r
JOIN questions q ON q.id = r.question_id
WHERE r.parse_ok = 1
GROUP BY q.topic, r.surface
ORDER BY soa_pct DESC;
```

### With a confidence interval

```sql
WITH agg AS (
    SELECT
        q.topic,
        r.surface,
        COUNT(*)               AS n,
        AVG(r.brand_mentioned) AS p
    FROM runs r
    JOIN questions q ON q.id = r.question_id
    WHERE r.parse_ok = 1
    GROUP BY q.topic, r.surface
)
SELECT
    topic,
    surface,
    n,
    ROUND(p * 100, 1)                                          AS soa_pct,
    ROUND((p - 1.96 * SQRT(p * (1 - p) / n)) * 100, 1)        AS ci_low,
    ROUND((p + 1.96 * SQRT(p * (1 - p) / n)) * 100, 1)        AS ci_high
FROM agg
ORDER BY soa_pct DESC;
```

**The CI is the product.** Reporting "12% ± 8, n=40" tells Mighty whether to act on it. That distinction is your entire positioning.

### Competitor share of answers — Mighty's actual competitor set

```sql
SELECT
    competitor.value                        AS competitor_name,
    COUNT(*)                                AS times_named,
    ROUND(COUNT(*) * 100.0 /
        (SELECT COUNT(*) FROM runs WHERE parse_ok = 1), 1) AS pct_of_all_answers
FROM runs r,
     json_each(r.competitors_named) AS competitor
WHERE r.parse_ok = 1
GROUP BY competitor.value
ORDER BY times_named DESC;
```

This is the slide that sells. Based on Day 1's manual check, expect Crunch, Gorilla Accounting, Ember, Nixon Williams, GoForma, SG Accounting and Mazuma to dominate — QAccounting, despite being an originally-assumed major competitor, barely showed up (1 mention across 40 Day 1 answers) and shouldn't be assumed dominant without the rig's own data confirming it. Mighty should sit near zero on Claude/Perplexity/Gemini and thin-but-present on ChatGPT specifically. That comparison, laid out plainly, is the entire pitch.

### Citation URL frequency — your Week 2 target list

```sql
SELECT
    url.value                AS cited_url,
    COUNT(*)                 AS times_cited,
    COUNT(DISTINCT r.question_id) AS n_questions
FROM runs r,
     json_each(r.cited_urls) AS url
WHERE r.parse_ok = 1
GROUP BY url.value
ORDER BY times_cited DESC
LIMIT 50;
```

For this niche, expect this list to be dominated by directory/roundup sites — contractoruk.com, umbrellacompany.com, limitedcompanyhelp.com — rather than the accountancy firms' own domains. That's an important difference from a pure SaaS niche: your citation-optimization target in Week 2 may be less about getting Mighty to write its own comparison content and more about getting Mighty *listed* on these third-party directories, which is a different and often easier ask (submission, not content production).

### Data quality check — run every morning

```sql
SELECT
    DATE(ts)                                    AS day,
    COUNT(*)                                    AS total_runs,
    SUM(CASE WHEN parse_ok = 0 THEN 1 ELSE 0 END) AS failures,
    ROUND(SUM(CASE WHEN parse_ok = 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS failure_pct
FROM runs
GROUP BY DATE(ts)
ORDER BY day DESC;
```

---

## Appendix J: Cohort Assignment

*Referenced from: Days 8-9 — Test/control split*

**Corrected 2026-08-10 — deterministic, not randomised, and no holdout tier.** The original topic-level random shuffle (7 topics → random split → pop one into holdout) was never actually consistent with putting `fixed_fee_positioning` in test on purpose — a genuine random shuffle doesn't guarantee that. And a dedicated holdout cluster, permanently unused, wasn't worth the N it costs on a dataset this thin: the near/far control tiering below plus the direct cited-URL spillover check (Appendix M) cover what holdout was for, more precisely.

```python
import sqlite3

TEST_TOPICS = {"fixed_fee_positioning"}

conn = sqlite3.connect("aeo.db")
topics = [r[0] for r in conn.execute(
    "SELECT DISTINCT topic FROM questions WHERE is_product = 1"
).fetchall()]

for topic in topics:
    cohort = "test" if topic in TEST_TOPICS else "control"
    conn.execute("UPDATE questions SET cohort=? WHERE topic=?", (cohort, topic))

conn.commit()
print(conn.execute(
    "SELECT cohort, topic, COUNT(*) FROM questions WHERE is_product=1 GROUP BY cohort, topic"
).fetchall())
```

With Mighty's **actual surviving clusters** — `new_company_setup` had zero product questions survive Day 2 Step 5 (0/7), so it never appears in this query; the real set is 7 clusters, not 8 (general_recommendation, ir35_compliance, fixed_fee_positioning, switching_accountants, tax_efficiency, software_compatibility, freelancer_agency). `fixed_fee_positioning` — Mighty's clearest differentiator, and (after reclassifying q001 out of `general_recommendation`, since "cheapest monthly online accountants uk" is a pricing-framing question, not a generic-recommendation one) its largest cluster at 10 questions — goes in **test**, since that's both where an intervention is most likely to land and where there's enough N to detect one. Everything else is **control**, split for interpretation into near/far tiers by semantic distance from the intervention:

| Tier | Clusters | Purpose |
|---|---|---|
| Test | `fixed_fee_positioning` (10) | Where the effort is aimed — should move if anything works |
| Near control | `general_recommendation` (8), `switching_accountants` (5) | Semantically close to "best accountant" listings — may move via genuine spillover, not proof of nothing |
| Far control | `tax_efficiency` (2), `software_compatibility` (3), `ir35_compliance` (4), `freelancer_agency` (4) | Should stay flat. If these move too, that's market drift, not you |

**Weight run allocation toward the clusters that can support a claim, not evenly.** `fixed_fee_positioning` (10) and `general_recommendation` (8) can support a real confidence interval; `tax_efficiency` (2) never will, no matter how many times it's run. `rig.py`'s `BASELINE_AFTER_RUNS` gives `fixed_fee_positioning` N=10 (raised from N=5 after Appendix K's power check showed N=5 gave the planned interventions well under 50% power in realistic scenarios), `general_recommendation` N=5, and N=3 to everything else — directional-only on the thin clusters, by design, not an oversight.

---

## Appendix K: Power Analysis

*Referenced from: Day 10 — The power calculation*

**Actually run 2026-08-10, not left as "unchanged mechanics."** `statsmodels` (this script's own dependency) wasn't even in `requirements.txt` — it would have failed on import the first time anyone tried to run it. Fixed. More importantly: ran it against realistic Day-1-derived baseline assumptions instead of leaving the power question unexamined until real data existed.

### What the numbers actually said

Day 1's manual check found Mighty **absent** from the exact question type that is now the test cluster ("fixed-fee accountant, not a big impersonal firm") — so a true baseline near 0% on `fixed_fee_positioning` specifically is plausible, though the aggregate rate across all question types was higher than zero. At the original N=5 (n=50), the picture was baseline-dependent in a way that mattered: if true baseline is ~0%, even a modest result (5/50 citations after) clears significance — a true zero is easy to move away from statistically. But if baseline sits anywhere in the realistic 4-10% range, detecting a generous +10pp lift from three weak, cooperation-free interventions (a directory listing, one Instagram post, one forum mention — no site access) had only **29-56% power** — worse than a coin flip in the worse cases.

**Changed as a result: `fixed_fee_positioning`'s N went from 5 to 10** (`rig.py`'s `BASELINE_AFTER_RUNS`). That raises power for a +10pp lift to 52-85% across the same baseline range, for about +$13 total across baseline and after. Cheap, and worth it — see the real cost in Appendix B's billing section.

```python
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize

analysis = NormalIndPower()
for n_per_q in [5, 10]:
    n = n_per_q * 10  # fixed_fee_positioning question count
    for p0 in [0.02, 0.05, 0.10]:
        p1 = p0 + 0.10  # the +10pp lift a weak, cooperation-free intervention might plausibly produce
        es = proportion_effectsize(p1, p0)
        power = analysis.power(effect_size=es, nobs1=n, alpha=0.05, ratio=1.0)
        print(f"N={n_per_q}/q, baseline={p0:.0%} -> +10pp lift: power={power:.0%}")
```

### Two things caught in cross-checking this with a second model (2026-08-10) — both real, both fixed

**The "how much lift is needed" number depends on which question you're asking.** "What's the smallest after-the-fact result that would look significant?" (~12pp at baseline 4%) and "what true effect do I need for an 80% *chance* of detecting it given sampling noise?" (~18-19pp at baseline 5%) are different, both-valid statistics — the first is optimistic and only useful for interpreting a result after it happens, the second is the right one for planning N in advance, which is what this appendix is for. Use the 80%-power framing when deciding whether the design can work; don't be surprised if a post-hoc check produces a smaller-sounding number for the same data.

**Every query below pools all three surfaces into one rate — and Day 1's own evidence says that's risky.** Day 1 found Mighty present (thinly) on ChatGPT and at genuine zero on Claude, Perplexity, and Gemini — not a uniform low rate, three structurally different platforms. Pooling them into one binomial test can dilute a real, detectable single-surface effect into pooled noise, or misrepresent what "baseline" even means. Appendix I's descriptive `SoA by topic × surface` query already breaks this out; the significance/power queries below didn't, until now. Check both pooled and per-surface — don't rely on pooled alone.

### The baseline gate — check this before Week 2, not after Week 4

Don't wait until the final analysis to find out whether the design could ever have worked. **Immediately after the baseline checkpoint runs, before spending any Week 2 effort**, check the actual observed rate — pooled and per-surface:

```sql
-- Pooled (the headline number)
SELECT ROUND(AVG(brand_mentioned) * 100, 1) AS baseline_pct, COUNT(*) AS n
FROM runs r JOIN questions q ON q.id = r.question_id
WHERE q.topic = 'fixed_fee_positioning' AND r.checkpoint = 'baseline' AND r.parse_ok = 1;

-- Per surface — check this too. A real signal on one platform can hide inside a flat pooled number.
SELECT r.surface, ROUND(AVG(r.brand_mentioned) * 100, 1) AS baseline_pct, COUNT(*) AS n
FROM runs r JOIN questions q ON q.id = r.question_id
WHERE q.topic = 'fixed_fee_positioning' AND r.checkpoint = 'baseline' AND r.parse_ok = 1
GROUP BY r.surface;
```

- **At or near 0% on both views** → good news for detectability specifically — even a small real result will likely show up as significant. Proceed as planned.
- **Above ~5% pooled, or meaningfully nonzero on one surface** → the planned interventions are unlikely to move the pooled number enough to reach significance at N=10, given the power numbers above — but check whether the effort should instead be evaluated per-surface if one platform is carrying most of the baseline presence. Worth a real decision at that point, not a silent hope: accept that a null (or per-surface-only) result is the likely honest outcome and frame the writeup accordingly, push N higher still (diminishing but real returns — see the table above), or revisit the "staying fully surprise" decision from Day 8-9 since site-access interventions are a fundamentally stronger treatment than anything on the no-cooperation list.
- **Remember the actual uncertainty here is wide.** Day 1's own data on this exact question type was 2 runs × 4 platforms, all zero (n=8) — a 95% Wilson interval on that is [0%, 32%], not a tight "probably near zero." The baseline checkpoint's real n=100 will tell you something Day 1's 8 observations couldn't.

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

### Original mechanics (per-topic/cohort, run against real data once `runs` has rows)

```python
# power.py
import sqlite3
import pandas as pd
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize

conn = sqlite3.connect("aeo.db")

baseline = pd.read_sql("""
    SELECT
        q.topic,
        q.cohort,
        COUNT(*)               AS n,
        AVG(r.brand_mentioned) AS p
    FROM runs r
    JOIN questions q ON q.id = r.question_id
    WHERE r.parse_ok = 1
    GROUP BY q.topic, q.cohort
""", conn)

print(baseline)

analysis = NormalIndPower()

for _, row in baseline.iterrows():
    p0 = row["p"]
    n  = row["n"]
    if p0 in (0, 1):
        print(f"{row['topic']}: baseline at {p0:.0%} — "
              f"can't compute MDE at a boundary. Note it.")
        continue

    for p1 in [x / 100 for x in range(1, 100)]:
        if p1 <= p0:
            continue
        es = proportion_effectsize(p1, p0)
        power = analysis.power(effect_size=es, nobs1=n, alpha=0.05, ratio=1.0)
        if power >= 0.80:
            print(f"{row['topic']}: baseline {p0:.1%}, n={n} → "
                  f"can detect a move to {p1:.0%} (MDE = {p1-p0:.1%})")
            break
    else:
        print(f"{row['topic']}: baseline {p0:.1%}, n={n} → "
              f"CANNOT detect any realistic effect. Need more runs.")
```

### Reading it for Mighty specifically

Given the flagged risk about Mighty's citation footprint, pay close attention to whether the baseline for any topic comes back at exactly 0%. A true zero (not just low) makes the standard proportion test awkward at the boundary — if you see this, it's worth treating as its own finding ("Mighty has literally zero presence in this topic cluster, versus a low-but-nonzero presence elsewhere") rather than forcing a power calculation that isn't well-defined at 0%.

---

## Appendix L: robots.txt Check

*Referenced from: What's conspicuously absent — the technical layer*

Five minutes. Once. Then stop. Site list swapped for Mighty's actual competitor set.

```bash
curl -s https://mightyaccounting.com/robots.txt
```

Look for:

```
User-agent: GPTBot
Disallow: /          # ← BLOCKED. Zero chance. Fix this.

User-agent: ClaudeBot
User-agent: PerplexityBot
User-agent: Google-Extended
```

Or scripted across the whole competitor set:

```python
import requests

SITES = ["mightyaccounting.com", "gorillaaccounting.com",
         "goforma.com", "crunch.co.uk", "qaccounting.com",
         "caroola.com", "sg-accounting.co.uk", "intouchaccounting.com",
         "ember.co", "mazumamoney.co.uk"]
# sg-accounting.co.uk, intouchaccounting.com, ember.co, mazumamoney.co.uk added
# after Day 1 manual check — these outranked qaccounting.com in real AI answers
BOTS  = ["GPTBot", "ClaudeBot", "PerplexityBot", "Google-Extended", "CCBot"]

for site in SITES:
    try:
        txt = requests.get(f"https://{site}/robots.txt", timeout=10).text
        print(f"\n=== {site} ===")
        for bot in BOTS:
            if bot in txt:
                idx = txt.find(bot)
                print(f"  {bot}: FOUND → {txt[idx:idx+80].splitlines()[1:2]}")
            else:
                print(f"  {bot}: not mentioned (default = allowed)")
    except Exception as e:
        print(f"{site}: {e}")
```

Binary gate, not an optimization. Check once, move on.

---

## Appendix M: Analysis

*Referenced from: Days 22-25 — Analysis*

**Corrected 2026-08-10.** Keyed on the `checkpoint` column (`'baseline'`, `'canary'`, `'after'`) instead of a hardcoded date threshold — the date-cutoff approach was brittle (one typo and "before" answers land in "after"); the explicit column can't drift out of sync with when a checkpoint actually ran. Three checkpoints also means a real trend line, not just two snapshots — worth plotting all three, not just before/after.

**Also corrected the same day, caught cross-checking this appendix with a second model:** every query in this section pools all three surfaces into one rate. Day 1 found Mighty present (thinly) on ChatGPT and at genuine zero on Claude and Perplexity — not a uniform low rate. Pooling risks diluting a real single-surface effect into noise, or averaging together three platforms that don't actually behave the same way. **Run the per-surface version alongside the pooled one, always** — don't trust the pooled number in isolation. Appendix K's baseline gate now does this too.

### Corrected again 2026-08-10 — the primary test changes

Cross-checked against a second model's independent statistical critique, then verified against this repo's own data rather than trusted on the page. Two things came out of it, both confirmed by direct computation:

**The ICC on `is_product` (from `research/step5_recheck_log.jsonl`, 40 questions × 3 Perplexity draws each) is 0.80.** Repeated runs of the same question are far more correlated with each other than with a different question — which is expected (a purely informational question returns zero every time; a genuinely contested one might not), but it means **the between-cluster significance test below is not valid.** Simulated false-positive rate for `proportions_ztest` comparing 10 test-cluster questions against 26 control-cluster questions, under a true null, at realistic heterogeneity: **22-24% across five different random seeds** — four to five times the nominal 5%, not a fluke of one simulation run.

**It gets worse than "the test is miscalibrated."** With only 7 topic-level clusters (1 test, 6 control), the finest possible p-value from *any* cluster-level randomization test is 1/7 ≈ 0.143 — mathematically incapable of reaching conventional significance regardless of the true effect size or which statistical model is used. A more sophisticated model does not fix this; there are simply not enough independent clusters for any valid frequentist test at the cluster level.

**The fix: change the primary comparison, don't try to rescue the old one.**

```sql
-- PRIMARY ANALYSIS: per-question paired difference, baseline vs after,
-- on the SAME questions. Pairing cancels the between-question variance
-- that makes the cluster-level test below invalid — this is the
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

### Test vs. control, by checkpoint (descriptive only — no p-value here, see above)

```sql
-- Pooled (the headline comparison)
SELECT
    q.cohort,
    r.checkpoint,
    ROUND(AVG(r.brand_mentioned) * 100, 1) AS soa_pct,
    COUNT(*) AS n
FROM runs r
JOIN questions q ON q.id = r.question_id
WHERE r.parse_ok = 1
GROUP BY q.cohort, r.checkpoint
ORDER BY q.cohort, CASE r.checkpoint WHEN 'baseline' THEN 1 WHEN 'canary' THEN 2 WHEN 'after' THEN 3 END;

-- Per surface — check this before trusting the pooled number above
SELECT
    q.cohort,
    r.surface,
    r.checkpoint,
    ROUND(AVG(r.brand_mentioned) * 100, 1) AS soa_pct,
    COUNT(*) AS n
FROM runs r
JOIN questions q ON q.id = r.question_id
WHERE r.parse_ok = 1
GROUP BY q.cohort, r.surface, r.checkpoint
ORDER BY q.cohort, r.surface, CASE r.checkpoint WHEN 'baseline' THEN 1 WHEN 'canary' THEN 2 WHEN 'after' THEN 3 END;
```

Baseline → after delta, if you just want the headline number:

```sql
WITH periods AS (
    SELECT q.cohort, r.checkpoint, AVG(r.brand_mentioned) AS soa
    FROM runs r
    JOIN questions q ON q.id = r.question_id
    WHERE r.parse_ok = 1 AND r.checkpoint IN ('baseline','after')
    GROUP BY q.cohort, r.checkpoint
)
SELECT
    cohort,
    MAX(CASE WHEN checkpoint='baseline' THEN ROUND(soa*100,1) END) AS soa_baseline,
    MAX(CASE WHEN checkpoint='after'    THEN ROUND(soa*100,1) END) AS soa_after,
    ROUND(
        MAX(CASE WHEN checkpoint='after' THEN soa END) -
        MAX(CASE WHEN checkpoint='baseline' THEN soa END), 4
    ) * 100 AS delta_pp
FROM periods
GROUP BY cohort;
```

### Near/far control breakdown — is the spillover risk showing up?

`cohort='control'` alone hides whether movement is concentrated in the semantically-close cluster (expected spillover) or spread into clusters that should be untouched (a real problem). Break it out by topic tier:

```sql
SELECT
    CASE
        WHEN q.topic = 'fixed_fee_positioning' THEN 'test'
        WHEN q.topic IN ('general_recommendation','switching_accountants') THEN 'near_control'
        ELSE 'far_control'
    END AS tier,
    r.checkpoint,
    ROUND(AVG(r.brand_mentioned) * 100, 1) AS soa_pct,
    COUNT(*) AS n
FROM runs r
JOIN questions q ON q.id = r.question_id
WHERE r.parse_ok = 1
GROUP BY tier, r.checkpoint
ORDER BY tier, CASE r.checkpoint WHEN 'baseline' THEN 1 WHEN 'canary' THEN 2 WHEN 'after' THEN 3 END;
```

Far control moving as much as test → market drift, not you. Near control moving but far control flat → plausible spillover, treat the test-vs-near-control comparison as softer evidence than test-vs-far-control.

### Framing cut — fixed fee vs monthly vs annual wording

Bonus, not the primary read — each framing group is only 3-4 questions, thinner than any full cluster. Directional only.

```sql
SELECT
    CASE
        WHEN q.notes LIKE '%framing:monthly%'   THEN 'monthly'
        WHEN q.notes LIKE '%framing:fixed_fee%' THEN 'fixed_fee'
        WHEN q.notes LIKE '%framing:annual%'    THEN 'annual'
        ELSE 'other'
    END AS framing,
    r.checkpoint,
    ROUND(AVG(r.brand_mentioned) * 100, 1) AS soa_pct,
    COUNT(*) AS n
FROM runs r
JOIN questions q ON q.id = r.question_id
WHERE r.parse_ok = 1 AND q.topic = 'fixed_fee_positioning'
GROUP BY framing, r.checkpoint
ORDER BY framing, CASE r.checkpoint WHEN 'baseline' THEN 1 WHEN 'canary' THEN 2 WHEN 'after' THEN 3 END;
```

The hypothesis this tests directly: Mighty's own hero copy already says "£60pm + VAT" (monthly-framed), but not "fixed fee." Predict `monthly` sits higher at baseline and moves *less* after the intervention; `fixed_fee` and `annual` sit lower at baseline and move *more*, since that's the actual gap being closed.

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

### Spillover check — direct evidence, not inference

Don't just infer spillover from whether near-control's number moved — check whether the actual URL you touched (the directory listing, the forum thread) shows up in a control cluster's citations:

```sql
SELECT r.question_id, q.topic, url.value AS cited_url
FROM runs r
JOIN questions q ON q.id = r.question_id,
     json_each(r.cited_urls) AS url
WHERE r.checkpoint = 'after'
  AND q.topic != 'fixed_fee_positioning'
  AND url.value IN (SELECT url FROM interventions WHERE url IS NOT NULL);
```

Matches in `general_recommendation`/`switching_accountants` (near control) only → spillover as expected, treat that comparison as softer evidence. Matches in the far-control topics too → something's off, investigate before writing up. No matches anywhere → the tiering held, test-vs-control is a cleaner read.

### How to read it

| Test delta | Control delta | Verdict |
|---|---|---|
| +12pp | +11pp | **The market moved. You did nothing.** |
| +12pp | +1pp | **Something real.** Test for significance. |
| +2pp | +1pp | Nothing happened either way. |
| -3pp | +8pp | You may have made it *worse*. Investigate. |

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

**Run this per surface too**, not just pooled (using the per-surface query above to get each surface's counts) — Day 1's evidence of real per-platform heterogeneity means the pooled rate can hide a real single-surface pattern. The *primary* significance test for whether anything happened at all is the paired bootstrap earlier in this appendix — this section only ever answers "did control move too."

### Per-topic breakdown

```sql
SELECT
    q.topic,
    q.cohort,
    ROUND(AVG(CASE WHEN r.checkpoint = 'baseline' THEN r.brand_mentioned END) * 100, 1) AS baseline_pct,
    ROUND(AVG(CASE WHEN r.checkpoint = 'canary'   THEN r.brand_mentioned END) * 100, 1) AS canary_pct,
    ROUND(AVG(CASE WHEN r.checkpoint = 'after'    THEN r.brand_mentioned END) * 100, 1) AS after_pct
FROM runs r
JOIN questions q ON q.id = r.question_id
WHERE r.parse_ok = 1
GROUP BY q.topic, q.cohort
ORDER BY q.cohort, after_pct - baseline_pct DESC;
```

### Before you believe anything

- [ ] Did control move too? (If yes → market, not you. Check near/far separately — see above.)
- [ ] Is it significant, or noise? (Run the test — pooled AND per-surface, not pooled alone)
- [ ] Was the power calc satisfied? (Could you even detect this? Check which framing you're using — "would this exact result look significant" and "80%-power MDE" are different, both-valid numbers — see Appendix K)
- [ ] Did the canary checkpoint show a consistent trend, or does after look like a one-off? (No holdout tier in this design — the canary checkpoint plus the direct spillover-URL check are what catch ambient drift instead)
- [ ] Does it reproduce on a fresh sample? (Re-run it)
- [ ] Are you reporting absolute, not relative?
- [ ] Would you defend this at Amazon in a design review?

### If nothing moved

Write it up anyway, honestly, with the power calc showing what you *could* have detected. In a niche where a small cottage industry is already forming around "AI visibility for accountants" with confident, unverifiable claims, a properly controlled null result — even a boring one — is a genuinely differentiated piece of content. The null result *is* the case study.
