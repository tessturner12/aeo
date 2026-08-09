# Log

Daily journal, one entry per day.

## Day 1 — Category verification

Ran the plan's 5 test questions by hand across ChatGPT, Claude, Perplexity and Gemini, each asked twice (40 answers total).

- **Category verified — go.** Named firms appear across the large majority of answers.
- **Mighty appears in 3 of 5 questions, ChatGPT only** — zero mentions on Claude, Perplexity, or Gemini across all 5. Where it appears, framing is positive ("best value," top-3 in a ranked shortlist of 6), but visibility rests almost entirely on one Reddit thread (`r/ContractorUK`) being cited repeatedly, not broad-based citation.
- **Absent from its own natural-home question** ("fixed-fee accountant, not a big impersonal firm"). Checked against Mighty's own site: "fixed fee" is real and prominent (Google meta description, pricing page) — the nuance is that the homepage hero leads with "£60pm + VAT. No hidden costs," not "fixed fee," so the phrase is secondary framing, not the primary pitch.
- **mightyaccounting.com cited once** across all 40 answers (672 total URLs, 130 unique domains).
- **Citation landscape:** crunch.co.uk (55), reddit.com (52), gorillaaccounting.com (33), forums.contractoruk.com (13), limitedcompanyhelp.com (12), umbrellacompany.com (10). Reddit + ContractorUK forums combined outweighed any single directory.
- **Competitor set corrected:** SG Accounting, InTouch Accounting, Ember, and Mazuma added — all outranked QAccounting (1 mention across 40 answers), which stays listed but downgraded to "watch, don't assume dominant."
- **Verdict: go**, with the pitch reframed from "Mighty is invisible" to "Mighty has thin, single-source, single-platform visibility, and is invisible on its own strongest positioning."

## Day 2 — Question research

- Brain dump → Claude-expanded phrasings → clustered into 8 topics → tiered head/mid/long.
- Ran the Day 2 Step 5 product-question filter (`step5_product_filter.py`) against Perplexity for every question — `is_product` TRUE/FALSE filled in for all rows, none left blank.
- Went further than the plan called for: ran an additional N=3 reliability recheck pass (`step5_recheck.py`) on top of the base script, logged in `step5_recheck_log.jsonl`.
- Final output: 68 questions in `questions.csv` across 8 clusters (general_recommendation, ir35_compliance, fixed_fee_positioning, switching_accountants, tax_efficiency, software_compatibility, new_company_setup, freelancer_agency).
- Open issue carried forward: `new_company_setup` came back with **zero** product questions after filtering (0/7) — it will silently drop out of cohort assignment later since that only pulls topics with `is_product = 1`. Needs a different control-group topic when cohort assignment happens (Day 8-9).

## Setup, tooling & plan stress-test

- Resolved PowerShell execution policy (`RemoteSigned`, `-Scope CurrentUser`) so the venv activates without admin rights.
- Created `.env` (Perplexity, Anthropic, OpenAI keys) and `admin/keys.md` as the durable local record — both gitignored, confirmed never reaching GitHub.
- Wrote and ran `test_apis.py` — Perplexity key confirmed working (200, correct answer returned).
- Installed the remaining Appendix A dependencies (`openai`, `pandas`) into the venv and generated `requirements.txt`.
- Dropped Brave as a fourth retrieval surface (its free tier now requires a card; Claude's own `web_search` likely already runs on Brave's index) — rig now pulls citations directly from each platform's own response instead. Committed and pushed.
- Ran a four-agent adversarial review of the whole plan — methodology, execution feasibility, market viability, and a devil's-advocate pass on whether this is worth the time at all. Findings, synthesis, and a "Day 30+" monetization phase (missing from the original plan) written up in `docs/plan-challenge.md`.
- **Not yet started:** the rig itself (Appendix E/F/G/H) — `src/rig.py`, `parser.py`, `schema.sql` are still empty stubs. That's the actual Day 3-5 work, still ahead.

## Plan revision, round two — independent verification + corrections applied

- Took `docs/plan-challenge.md` into the companion claude.ai Project chat for a second, independent pass — not just trusting the first review, but checking its own claims against live sources.
- That pass **confirmed the review was right, and found the "uncontested niche" problem was worse than first reported**: not 3 competitor names to check, but at least 7 real, active players already selling "AI visibility for UK accountants" specifically — including one (Renownly) with published research on the exact 28-firm IR35/contractor slice this project targets, and another (myaivisibility.co.uk) with a sample report for a Leeds IR35/contractor accountant, the closest direct analogue found to Mighty itself.
- Result written up in `docs/plan-deep-dive-response.md`.
- Applied the corrections directly to the plan and appendix: real Day 2 results with the per-cluster kept/deleted breakdown, the corrected competitor landscape (traced the original "uncontested" claim back to a competitor's own marketing copy), a 6-8 week timeline reality check (not 30 days), an explicit API-vs-consumer-app caveat, and the missing "Day 30+" monetization phase.
- Caught and fixed one internal contradiction between the two review docs on whether to add Gemini as a 4th surface (one said drop the claim, one said add it as a fast-follow) — resolved in favour of adding it, sequenced after the 3-surface rig is proven stable, since real Gemini baseline data already exists from Day 1 and just isn't being used yet.
- Also fixed `research/questions-raw.md`, which had been accidentally overwritten with a duplicate of `questions-expanded.md` — restored the real Day 2 Step 1 brain-dump content (the actual personal questions from running Tess Turner Ltd).
- All of the above committed and pushed to GitHub.

## Appendix D through G — build begins

Worked through the appendix systematically, verifying and building for real rather than just reading:

- **Appendix D (question filtering) — confirmed already fully done.** Re-ran the `pandas` loading/filter snippet against the real `questions.csv`: 36 product questions survive across 7 topics (`new_company_setup` doesn't appear at all, as expected). Confirmed via the raw CSV that all 68 rows have `is_product` filled in, none left blank or `BORDERLINE` — the Step 5 filter and the extra N=3 recheck pass were both genuinely completed already.
- **Appendix E (Python primer) — walked through hands-on.** Ran all six core concepts (variables, dicts, lists, functions, f-strings, try/except) against real project data instead of toy examples, including the SQL-analogy mapping. No code to build here, just the concepts needed before F onward.
- **Appendix F (database) — built for real.** Wrote the actual `src/schema.sql` (three tables: `questions`, `runs`, `interventions`), created `src/aeo.db`, and loaded the 36 filtered questions. **Caught and fixed a real bug in the appendix's own loading script**: `df.to_sql(..., if_exists='replace')` silently drops and rebuilds the table from pandas' inferred types, which wipes out the `PRIMARY KEY` and `CHECK` constraints `schema.sql` defines. Fixed by restoring the schema and reloading with `if_exists='append'` instead — verified afterward that the primary key constraint genuinely rejects a duplicate `id` insert.
- **Appendix G (the LLM parser) — built and unit-tested, full validation still blocked.** Wrote the real `src/parser.py`. Since the `runs` table is still empty (the rig hasn't run yet), the appendix's own Day 5 validation step (sampling 30 real answers) can't run yet — so tested the parser instead against 6 hand-crafted adversarial cases covering the traps the appendix specifically warns about: the plain adjective "mighty," the unrelated company "Mighty Networks," a purely informational no-firms-named answer, positive and negative sentiment, and — the hardest case — an answer that describes Mighty ("the small fixed-fee firm run by Mark and James") without ever naming it. All 6 passed correctly, including that last one, which is exactly the false-negative case naive string-matching would miss.
- **Not yet started: Appendix H (the rig itself).** `src/rig.py` is still an empty stub. This is the next real step — once it runs, it'll populate the `runs` table and unblock Appendix G's full 30-sample validation pass.

