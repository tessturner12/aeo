# AEO — Mighty Accounting: Baseline Findings (12 Aug 2026)

Doc mirror of the published summary artifact. Full narrative and styling live in the artifact; this is the same content in plain form for the repo.

## What this is

Mighty Accounting is a small, genuinely fixed-fee UK contractor accountancy firm. This project tests whether Mighty can be made visible in AI-generated answers (ChatGPT, Claude, Perplexity), not just search engines — before/after design: measure real visibility now (**baseline**), make targeted changes to one question cluster only, measure again after a wait period (**after**), with a **canary** checkpoint in between.

## The headline number

**0.0% — Mighty mentioned in 0 of 650 real baseline calls, across all three surfaces.**

| Topic | Claude | ChatGPT (OpenAI) | Perplexity | Pooled n |
|---|---|---|---|---|
| `fixed_fee_positioning` (test cluster) | 0.0% (n=30) | 0.0% (n=100) | 0.0% (n=100) | 230 |
| `general_recommendation` | 0.0% (n=24) | 0.0% (n=40) | 0.0% (n=40) | 104 |

A true zero baseline is the easiest starting point to detect a real lift from. Day 1's manual test on this question type was n=8, all zero, 95% interval [0%, 32%] — this real n=230 confirms it wasn't a fluke.

## The apparent contradiction — and the real mechanism

Day 1's manual ChatGPT test surfaced Mighty on 3 of 5 general questions — but that finding already carried its own warning: visibility rested "almost entirely on one Reddit thread being cited repeatedly, not broad-based citation." Checked directly against the real baseline data rather than assumed:

- **1 / 256** real OpenAI baseline calls cited any reddit.com URL at all.
- **4 / 256** cited anything from ContractorUK forums.

The rig runs OpenAI's search tool at `search_context_size="low"` (a cost lever added 2026-08-11, cutting the full 3-checkpoint budget from an estimated $83.59 to $67.11). A narrower search mostly doesn't retrieve the one thread Mighty's visibility depended on. Combined with Day 1's tiny 2-run sample, the real n=100 zero is the more trustworthy number, not a sign Mighty lost visibility it once had.

**Caveat for the writeup:** the narrowed search applies identically at every checkpoint, so the baseline→after *comparison* stays valid — but the absolute percentages specifically reflect visibility under the rig's cost-optimized search depth, not what a real end user sees on the full ChatGPT product. Written into `docs/aeo-30-day-plan-mighty.md` alongside the existing API-vs-consumer-app caveat.

## How the run actually went

- **09:32** — first attempt: all 203 calls failed on authentication. Root cause: `rig.py` imported its parser module before loading `.env`; the parser builds its own Anthropic client at import time, so it got permanently built with no key.
- **Correction:** Perplexity/OpenAI calls read their keys correctly at call-time and likely succeeded for real, then crashed on the next step and discarded the paid-for answer as an empty error row. An earlier "no money was spent" update was wrong and was corrected once traced properly.
- **Fix:** reordered the import, made the parser self-sufficient. Verified by exercising the real import chain and making a live parse call end-to-end, not just checking env vars looked set.
- **Attempt 2:** 114 real, correct calls, zero errors — then killed anyway by something outside the script (confirmed not the user). Likely the session's background-task tracking couldn't hold a ~3 hour job.
- **11:16 — attempt 3:** relaunched as a fully detached OS process, independent of session tracking, with the resume guard skipping the 114 already-real rows.
- **~13:20:** 650/650 complete, zero errors — 138 Claude, 256 ChatGPT, 256 Perplexity, matching the pre-registered weighted run counts exactly.

## Budget

| Provider | Cap set | Estimated | Real calls |
|---|---|---|---|
| Perplexity | $8.50 | $2.56 | 256, 0 errors |
| Claude | $12.00 | $6.90 | 138, 0 errors |
| OpenAI | $28.00 | $17.92 | 256, 0 errors |
| **Total** | **$48.50** | **$27.38** | **650, 0 errors** |

Auto-reload deliberately left off on every provider console.

## Data integrity

The 650 real rows in `runs` aren't regenerable without spending the $27.38 again. Backed up three ways in `backups/`:

1. Full database copy — `aeo_2026-08-12_baseline-complete.db`
2. CSV + JSON export of all 650 `runs` rows — plain-text, survives a corrupted SQLite file independently
3. Config, schema, and question-set snapshots frozen alongside the data, needed to interpret it correctly later

**Worth revisiting:** `.gitignore`'s note on `*.db` ("regenerable from schema.sql + questions.csv") predates any real run and is now stale — `runs` is real, paid-for data. The CSV/JSON exports aren't caught by that rule and can go to GitHub for off-machine durability if committed; the raw `.db` backup stays local-only under the existing convention unless that's deliberately changed.

## What's next

- **Week 2:** make the site changes — `fixed_fee_positioning` only; every other topic stays untouched as control.
- **Mid-wait:** canary checkpoint (~285 calls, ~$12.35) — catches a broken rig or dead API before the after-checkpoint budget is spent.
- **Week 3:** after checkpoint — same weighted run counts and settings as baseline.
- **Week 4:** analysis and writeup. Perplexity is the pre-registered primary surface for the significance test; Claude and OpenAI reported alongside without a p-value attached.
