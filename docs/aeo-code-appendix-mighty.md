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

**Step 6 — Cron (the 3am scheduler).**
```bash
crontab -e
```
Add:
```
0 3 * * * cd /home/tess/aeo-rig && /home/tess/aeo-rig/venv/bin/python rig.py >> /home/tess/aeo-rig/logs/cron.log 2>&1
```

**Step 7 — Verify it actually ran.**
```bash
tail -50 ~/aeo-rig/logs/cron.log
sqlite3 ~/aeo-rig/aeo.db "SELECT COUNT(*), DATE(ts) FROM runs GROUP BY DATE(ts);"
```

### Backups

```bash
# crontab addition — daily DB snapshot
30 3 * * * cp /home/tess/aeo-rig/aeo.db /home/tess/backups/aeo-$(date +\%Y\%m\%d).db
```

```bash
# pull a copy down periodically
scp tess@YOUR_SERVER_IP:~/aeo-rig/aeo.db ./aeo-backup.db
```

---

## Appendix B: API Setup

*Referenced from: Part 2 — The API cost maths*

Unchanged — four accounts, same as any brand.

| Provider | Where | Notes |
|---|---|---|
| Perplexity | perplexity.ai/settings/api | Your workhorse. Add ~$5 credit. |
| Anthropic | console.anthropic.com | Claude as surface + the parser |
| OpenAI | platform.openai.com | ChatGPT as surface |
| Brave | brave.com/search/api | 2,000 free/month |

### SET BILLING CAPS. NOW. BEFORE ANY CODE.

Set every provider's spend limit to £15. Not because Mighty's volume will be expensive — it's the same tiny volume as any brand — but because an unattended loop bug at 3am doesn't care whose name is in the config.

### `.env` and `.gitignore`

```
PERPLEXITY_API_KEY=pplx-xxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxxxx
BRAVE_API_KEY=BSA-xxxxxxxxxxxx
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
| `cohort` | text | `test` / `control` / `holdout` — filled Day 8 |
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

```sql
-- schema.sql

CREATE TABLE IF NOT EXISTS questions (
    id          TEXT PRIMARY KEY,
    text        TEXT NOT NULL,
    topic       TEXT NOT NULL,
    tier        TEXT CHECK (tier IN ('head','mid','long')),
    is_product  BOOLEAN NOT NULL,
    cohort      TEXT CHECK (cohort IN ('test','control','holdout')),
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
    parse_ok          BOOLEAN DEFAULT 1,
    error             TEXT
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
- competitors_named: every OTHER accountancy firm named, exact
  names (e.g. "Gorilla Accounting", "GoForma", "Crunch",
  "QAccounting", "Caroola", "SJD Accountancy", "Brookson",
  "Aardvark Accounting", "Nixon Williams", "The Accountancy
  Partnership", "Accounting Wise", "More Than Accountants").
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

Full working script, config swapped for Mighty. Read it, then hand it to Claude Code to adapt.

```python
# rig.py
import os, json, time, sqlite3, random
from datetime import datetime
import requests
from dotenv import load_dotenv
from anthropic import Anthropic
from openai import OpenAI

load_dotenv()

BRAND   = "Mighty Accounting"
N_RUNS  = 5
DB      = "aeo.db"

anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
openai_client    = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


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
    msg = anthropic_client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": question}],
    )
    text = ""
    for block in msg.content:
        if block.type == "text":
            text += block.text
    return text, []


def ask_openai(question):
    resp = openai_client.chat.completions.create(
        model="gpt-4o-search-preview",
        messages=[{"role": "user", "content": question}],
    )
    return resp.choices[0].message.content, []


def get_brave_retrieval_set(question):
    r = requests.get(
        "https://api.search.brave.com/res/v1/web/search",
        headers={"X-Subscription-Token": os.getenv("BRAVE_API_KEY")},
        params={"q": question, "count": 10},
        timeout=30,
    )
    r.raise_for_status()
    results = r.json().get("web", {}).get("results", [])
    return "", [x["url"] for x in results]


SURFACES = {
    "perplexity": (ask_perplexity, "sonar"),
    "claude":     (ask_claude,     "claude-sonnet-4-5"),
    "openai":     (ask_openai,     "gpt-4o-search-preview"),
    "brave":      (get_brave_retrieval_set, "brave-search"),
}


# ---------- MAIN LOOP ----------

def run_cycle():
    conn = sqlite3.connect(DB)
    questions = conn.execute(
        "SELECT id, text FROM questions WHERE is_product = 1"
    ).fetchall()

    print(f"[{datetime.now()}] Starting cycle: "
          f"{len(questions)} questions x {len(SURFACES)} surfaces x {N_RUNS} runs")

    for qid, qtext in questions:
        for surface_name, (fn, model) in SURFACES.items():
            for run_index in range(N_RUNS):
                try:
                    answer, urls = fn(qtext)
                    parsed = (parse_answer(answer, BRAND)
                              if answer else {"brand_mentioned": None})

                    conn.execute("""
                        INSERT INTO runs (
                            question_id, surface, model, run_index, ts,
                            raw_answer, cited_urls, brand_mentioned,
                            brand_position, competitors_named, parse_ok
                        ) VALUES (?,?,?,?,?,?,?,?,?,?,?)
                    """, (
                        qid, surface_name, model, run_index,
                        datetime.now().isoformat(),
                        answer,
                        json.dumps(urls),
                        parsed.get("brand_mentioned"),
                        parsed.get("brand_position"),
                        json.dumps(parsed.get("competitors_named", [])),
                        parsed.get("parse_ok", True),
                    ))
                    conn.commit()

                except Exception as e:
                    print(f"  ERROR {qid}/{surface_name}/{run_index}: {e}")
                    conn.execute("""
                        INSERT INTO runs (
                            question_id, surface, model, run_index, ts,
                            raw_answer, parse_ok, error
                        ) VALUES (?,?,?,?,?,?,?,?)
                    """, (qid, surface_name, model, run_index,
                          datetime.now().isoformat(), "", 0, str(e)))
                    conn.commit()

                time.sleep(random.uniform(0.5, 1.5))

    conn.close()
    print(f"[{datetime.now()}] Cycle complete")


if __name__ == "__main__":
    run_cycle()
```

### The design decisions, called out (unchanged rationale, still applies)

**`temperature: 1.0`.** You're measuring the world as real users experience it, including the variance. Don't suppress it.

**try/except around every call.** One blip at 3am shouldn't kill the whole night's cycle.

**`time.sleep` with jitter.** Avoids rate limits, avoids hammering in lockstep.

**Commit per row.** A crash at question 47 shouldn't lose questions 1-46.

**Errors get a row, not silence.** Ambiguity between "failed" and "never ran" corrupts your denominators.

### Rough runtime

60 questions × 4 surfaces × 5 runs × ~2s = **~40 minutes**. Fine at 3am.

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

This is the slide that sells. Expect it to show Caroola/SJD, Gorilla Accounting, GoForma, Crunch, QAccounting and the wider set (Aardvark, Nixon Williams, TAP, Accounting Wise, More Than Accountants) dominating — with Mighty near zero. That comparison, laid out plainly, is the entire pitch.

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

Unchanged mechanics — randomise at the topic level, always.

```python
import random, sqlite3

random.seed(42)

conn = sqlite3.connect("aeo.db")
topics = [r[0] for r in conn.execute(
    "SELECT DISTINCT topic FROM questions WHERE is_product = 1"
).fetchall()]

random.shuffle(topics)
mid = len(topics) // 2
test, control = topics[:mid], topics[mid:]
holdout = [control.pop()] if len(control) > 2 else []

print(f"TEST:    {test}")
print(f"CONTROL: {control}")
print(f"HOLDOUT: {holdout}")

for topic in test:
    conn.execute("UPDATE questions SET cohort='test' WHERE topic=?", (topic,))
for topic in control:
    conn.execute("UPDATE questions SET cohort='control' WHERE topic=?", (topic,))
for topic in holdout:
    conn.execute("UPDATE questions SET cohort='holdout' WHERE topic=?", (topic,))

conn.commit()
```

With Mighty's clusters (general_recommendation, ir35_compliance, fixed_fee_positioning, switching_accountants, dividend_tax_efficiency, software_compatibility, new_company_setup, freelancer_agency), a sensible split puts `fixed_fee_positioning` — Mighty's clearest differentiator — in the **test** group, since that's where an intervention is most likely to land, and something broad and less differentiated like `new_company_setup` in **control**.

---

## Appendix K: Power Analysis

*Referenced from: Day 10 — The power calculation*

Unchanged mechanics.

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
         "caroola.com", "aardvarkaccounting.co.uk",
         "nixonwilliams.com", "theaccountancy.co.uk",
         "a-wise.co.uk", "morethanaccountants.co.uk"]
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

Unchanged mechanics — dates below are placeholders, adjust to your actual Day 15 intervention date.

### The only chart that matters

```sql
WITH periods AS (
    SELECT
        q.cohort,
        CASE WHEN DATE(r.ts) < '2026-09-08' THEN 'before' ELSE 'after' END AS period,
        AVG(r.brand_mentioned) AS soa,
        COUNT(*)               AS n
    FROM runs r
    JOIN questions q ON q.id = r.question_id
    WHERE r.parse_ok = 1
      AND q.cohort IN ('test','control')
    GROUP BY q.cohort, period
)
SELECT
    cohort,
    MAX(CASE WHEN period='before' THEN ROUND(soa*100,1) END) AS soa_before,
    MAX(CASE WHEN period='after'  THEN ROUND(soa*100,1) END) AS soa_after,
    ROUND(
        MAX(CASE WHEN period='after' THEN soa END) -
        MAX(CASE WHEN period='before' THEN soa END), 4
    ) * 100 AS delta_pp
FROM periods
GROUP BY cohort;
```

### How to read it

| Test delta | Control delta | Verdict |
|---|---|---|
| +12pp | +11pp | **The market moved. You did nothing.** |
| +12pp | +1pp | **Something real.** Test for significance. |
| +2pp | +1pp | Nothing happened either way. |
| -3pp | +8pp | You may have made it *worse*. Investigate. |

### Significance test

```python
from statsmodels.stats.proportion import proportions_ztest
import numpy as np

counts = np.array([test_hits_after, control_hits_after])
nobs   = np.array([test_n_after,   control_n_after])

stat, pval = proportions_ztest(counts, nobs)
print(f"z = {stat:.3f}, p = {pval:.4f}")

if pval < 0.05:
    print("Difference is statistically significant.")
else:
    print("Not significant. Report that plainly.")
```

### Per-topic breakdown

```sql
SELECT
    q.topic,
    q.cohort,
    ROUND(AVG(CASE WHEN DATE(r.ts) <  '2026-09-08' THEN r.brand_mentioned END) * 100, 1) AS before_pct,
    ROUND(AVG(CASE WHEN DATE(r.ts) >= '2026-09-08' THEN r.brand_mentioned END) * 100, 1) AS after_pct
FROM runs r
JOIN questions q ON q.id = r.question_id
WHERE r.parse_ok = 1
GROUP BY q.topic, q.cohort
ORDER BY q.cohort, after_pct - before_pct DESC;
```

### Before you believe anything

- [ ] Did control move too? (If yes → market, not you)
- [ ] Is it significant, or noise? (Run the test)
- [ ] Was the power calc satisfied? (Could you even detect this?)
- [ ] Did the holdout set move? (If yes → ambient drift)
- [ ] Does it reproduce on a fresh sample? (Re-run it)
- [ ] Are you reporting absolute, not relative?
- [ ] Would you defend this at Amazon in a design review?

### If nothing moved

Write it up anyway, honestly, with the power calc showing what you *could* have detected. In a niche where a small cottage industry is already forming around "AI visibility for accountants" with confident, unverifiable claims, a properly controlled null result — even a boring one — is a genuinely differentiated piece of content. The null result *is* the case study.
