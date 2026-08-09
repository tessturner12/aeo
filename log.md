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

