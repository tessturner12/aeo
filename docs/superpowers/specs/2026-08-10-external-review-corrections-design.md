# Design: Corrections from the external review pass

**Date:** 2026-08-10
**Status:** proposed, awaiting approval
**Inputs:** two rounds of adversarial critique from a second model, and [`docs/external-review-response.md`](../../external-review-response.md) — a point-by-point rebuttal written with the repo in hand, checking every load-bearing claim against real data or live sources.

## What this is

Before touching any code or doc, every empirical claim in `external-review-response.md` was independently re-run against the actual repo data rather than trusted on the page. All of it reproduced exactly. This document is the resulting decision list: what changes, what doesn't, and why — the thing to approve before it becomes an implementation plan.

## Verification performed (2026-08-10, independent of the response doc's own author)

| Claim | Check | Result |
|---|---|---|
| ICC ≈ 0.80 on `is_product`, from `step5_recheck_log.jsonl` | Re-ran the ANOVA ICC calculation from scratch | **ICC = 0.8041**, grand mean p = 0.4833 — exact match, including the design-effect table (2.61 / 4.22 / 8.24) |
| Appendix M's current significance test has an inflated false-positive rate (~22.5%) | Re-ran the Monte Carlo simulation across 5 different random seeds (1, 2, 3, 42, 99) | **21.5–24.3% FPR in every seed** — not a fluke of one run, robust |
| Paired baseline→after test has correct-to-conservative coverage | Re-ran the paired-test simulation | Reproduced closely (53.5%/64.9% power at 10q×10r vs. their 53%/65%) |
| Day-1 directory presence: 11/20 cells cite a planned intervention target | Re-parsed `day1-category-check.md` from scratch | **11/20 exact match**, every per-domain count matched to the digit (crunch.co.uk 10/20, reddit.com 9/20, contractoruk 8/20, etc.) |
| Per-surface breakdown: Claude/Gemini cite neither Reddit nor target directories | Re-parsed per-surface | **Exact match** — Claude 2/5 directories, 0/5 Reddit; Gemini 1/5 directories, 0/5 Reddit |
| Market is stratified, not just commoditized at the bottom | Independent web search (not the response doc's sources) | Direction confirmed by multiple independent sources — but several of those sources are GEO/AEO agencies' own marketing content, so treat specific figures as industry self-reporting, not audited data |

**One addition beyond the response doc, found while verifying it:** with only 7 topic-level clusters (1 test, 6 control), the finest possible p-value from *any* cluster-level randomization test is 1/7 ≈ 0.143 — mathematically incapable of reaching conventional significance (p<0.05) regardless of true effect size or which statistical model is used. This is a stronger version of the response doc's finding: it's not that the current test is miscalibrated and a better model would fix it — no valid between-cluster test can work at this cluster count, full stop. This forecloses "use a mixed-effects model later" as a future fix and confirms demoting the between-cluster comparison to descriptive-only is the complete answer, not a stopgap.

**Conclusion: the response document's empirical work is sound.** Nothing was rounded favorably, nothing failed to reproduce. The decision list below adopts its recommendations, with the cluster-count point strengthening the case for #1.

## Decisions

### A. Before the baseline checkpoint runs (text/schema/prompt edits, no API spend)

| # | Change | Where | Why |
|---|---|---|---|
| 1 | Rewrite Appendix M's primary analysis as a per-question paired bootstrap (baseline→after, same questions). Demote the test-vs-control cluster comparison to descriptive — report the deltas side by side, no p-value. | Appendix M | Current `proportions_ztest` between clusters has a ~22% false-positive rate, confirmed by simulation across 5 seeds; the 1/7 cluster-count argument shows no fix at the cluster level is possible |
| 2 | Pre-register Perplexity as the primary surface, dated, before baseline runs | Plan doc | Testing across 3 surfaces independently gives ~14% family-wise error; also the surface with the strongest intervention mechanism (§5 evidence) |
| 3 | Log the three Week 2 interventions as distinct `type` values (`directory`, `forum`, `social`) in the `interventions` table | DB usage (column already exists) | Free — enables attributing any observed movement to a specific lever afterward |
| 4 | Make the astroturfing/disclosure rule prominent and non-negotiable: no manufactured evidence ever; any forum/social mention discloses in the post itself that the poster isn't a customer and this is part of a measurement experiment | Plan doc, Week 2 section | Currently a buried bullet on a real reputational risk |
| 5 | Write the 8–14pp intervention-ceiling estimate into Appendix K, replacing the unsourced +10pp guess, with the 55%/11-20 Day-1 evidence behind it | Appendix K | Evidence-backed number should replace a guess |
| 6 | Add `recommended` (boolean) and `recommendation_rank` to `schema.sql` and the parser prompt. Recommendation share becomes the primary KPI; mention share becomes secondary. | `schema.sql`, `parser.py` | "Mentioned but not recommended" (e.g. "however, Gorilla has more experience...") currently counts as a win; it shouldn't. Cheaper before the run than an `ALTER TABLE` after. |
| 7 | `config.yaml` for brand/competitors/questions, so the rig is reusable per-client rather than hardcoded to Mighty | `rig.py` / new config file | Cheapest item on the list today, expensive retrofit later, and this is the actual reusable asset behind any future business |
| 8 | Add 8 matched question pairs (fixed-fee-framed vs. generic-framed) at N=5 as a secondary, drift-robust comparison alongside the tiered topic comparison | `questions.csv`, `rig.py` | ~$12. The only comparison in the design that's robust to market-wide drift over the 4-week window — don't replace the existing tiering, add to it |
| 9 | Recover `q026` as a `borderline` tag rather than deleted; store the Step-5 vote fraction, not just the binary, on the rows that were rechecked | `questions.csv` | Low cost, low value, but free information currently thrown away |

### B. After baseline runs, before Week 2 (needs real data, so can't be done yet)

- Run the baseline gate (pooled and per-surface — already in the plan).
- Compute the real ICC on `brand_mentioned` specifically (not `is_product`) from the actual baseline data. This is the number the whole clustering argument turns on, and it's currently a proxy measured on a different, more structural outcome.
- Label ~60 stratified answers by hand; report parser precision/recall/false-positive rate on `brand_mentioned`.

### C. Direction decided now, not urgent, doesn't block baseline

- Question-sourcing cross-check against real ContractorUK/Reddit thread titles (~2 hrs) — sanity-check, not a rebuild.
- Google AI Overviews as a future 4th surface (not Gemini — Day 1 showed Gemini has no citation mechanism the current interventions could reach).
- Fold 2-3 agencies into the eventual demand-test conversations, in parallel with individual businesses, not as a fallback.
- Drop "30-day" and "AEO" from anything client-facing; lead with "how often does ChatGPT recommend your business?"
- Add a short platform-risk paragraph to the plan's framing (this project has already been bitten once by a model going EOL mid-project — that's evidence for "we continuously measure what changed" as the durable value, not "we know the algorithm").

### D. Rejected, with reasons

| Recommendation | Why not |
|---|---|
| Track revenue attribution from day one | Not measurable at Mighty's traffic volume; the two critique passes contradicted each other on this and the second one (which reversed itself) is better sourced |
| Approach Mighty before baseline | Would contaminate the baseline measurement irreversibly |
| Stop building, focus on selling first | The build is already done; remaining spend is ~$63, not weeks of engineering |
| Rebuild the whole design around matched pairs, replacing the topic tiering | Add matched pairs as a secondary read (item A8); the existing tiering is already built and answers a different, still-useful question |
| Reallocate budget from repeated runs to more questions | Simulated as power-neutral; the current 10×10 allocation is fine |

## The one framing-level change

The project's headline claim shifts from **"we proved AEO works"** to **"a methodology finding (how many runs you actually need before an AI-visibility estimate stabilizes, how much surfaces disagree with each other, where citation evidence concentrates) plus an honest, clearly-labeled, likely-underpowered pilot intervention on top of it."** The baseline checkpoint alone — before any intervention — is already a complete, publishable asset that cannot produce a null result, because it isn't testing an intervention at all. That's the strongest single idea in either critique pass, and it changes what gets sold, not just what gets coded.

## What doesn't change

Mighty as case-study subject (not assumed customer), the 3-checkpoint cadence, the cost fixes, the near/far control tiering as a descriptive tool, the pricing ladder already adopted (£99-299 audit before any £500+/month conversation), Perplexity/Claude/OpenAI as the current 3 surfaces, and the overall verdict that this is worth finishing (~$63 remaining, not a rebuild).
