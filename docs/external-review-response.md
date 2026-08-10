# Response to the External Review

*Companion to [aeo-30-day-plan-mighty.md](aeo-30-day-plan-mighty.md), [aeo-code-appendix-mighty.md](aeo-code-appendix-mighty.md), [plan-challenge.md](plan-challenge.md) and [plan-deep-dive-response.md](plan-deep-dive-response.md).*

**Date:** 2026-08-10
**What this is:** a point-by-point response to a two-part critique of this project produced by a different model — an initial review of the plan, then a deeper second pass after being challenged. Unlike `plan-challenge.md` (which was a paper review of the plan's prose, run before any code existed), this response was written with the repo in hand and with the load-bearing claims checked empirically or against live sources.

**Method note, and the reason this document exists at all:** the earlier adversarial pass missed the nightly-cron cost blowup because it read the plan rather than executing anything. That lesson is applied here. Every numerical claim below was either computed from data already in this repo or verified against a live source. Where a claim could not be checked, it is flagged as unchecked rather than asserted.

**Bottom line:** the review is good, and one of its central claims is right in a way that invalidates a test currently written into Appendix M. But my own first reading of that claim was wrong in direction, and correcting it changes the recommended fix substantially. Roughly a third of the review is stale (it critiques a build that has already happened), a third is right and actionable, and a third is right but lower-priority than it appears.

---

## Contents

- [0. Verification of the source material](#0-verification-of-the-source-material)
- [1. Pseudoreplication — the central claim, and my own retraction](#1-pseudoreplication--the-central-claim-and-my-own-retraction)
- [2. Matched pairs](#2-matched-pairs)
- [3. More questions vs more runs](#3-more-questions-vs-more-runs)
- [4. The product-question filter](#4-the-product-question-filter)
- [5. Intervention design — the largest gap](#5-intervention-design--the-largest-gap)
- [6. Multiplicity across surfaces — a gap nobody flagged](#6-multiplicity-across-surfaces--a-gap-nobody-flagged)
- [7. Astroturfing and disclosure](#7-astroturfing-and-disclosure)
- [8. Parser: gold set and recommendation-vs-mention](#8-parser-gold-set-and-recommendation-vs-mention)
- [9. Reporting hygiene and language rules](#9-reporting-hygiene-and-language-rules)
- [10. Question sourcing](#10-question-sourcing)
- [11. Commercial: the commoditisation claim, checked](#11-commercial-the-commoditisation-claim-checked)
- [12. Commercial: buyer, channel, naming, platform risk](#12-commercial-buyer-channel-naming-platform-risk)
- [13. Where the two review passes contradict each other](#13-where-the-two-review-passes-contradict-each-other)
- [14. What is stale](#14-what-is-stale)
- [15. The reframe](#15-the-reframe)
- [16. Decision list, ordered](#16-decision-list-ordered)
- [17. Where this response could itself be wrong](#17-where-this-response-could-itself-be-wrong)
- [Appendix: reproducible code for the empirical checks](#appendix-reproducible-code-for-the-empirical-checks)

---

## 0. Verification of the source material

The review leans on external citations. Spot-checked before accepting any of the arguments built on them.

**The core methodological citation is real and supportive.** arXiv:2604.07585, *"Don't Measure Once: Measuring Visibility in AI Search (GEO)"*, Schulte, Bleeker & Kaufmann, submitted 8 April 2026, cs.IR. Verified directly on arXiv. Its argument is that answers vary across runs, prompts and time, making one-off observations unreliable, and that visibility should be characterised as a distribution rather than a single-point outcome — i.e. it independently validates the N≥5 repeated-runs design that is already this project's core method decision.

Its reported instability figures are useful as priors for our own variance work: cited-source overlap between repeated runs of roughly 32–43%, brand-mention overlap averaging 45–59% day-to-day, and citation concentration averaging a Gini coefficient of around 0.715 across platforms (highest on Google AI Mode, most distributed on Perplexity).

**What the paper does not report is an intraclass correlation.** That matters — see §15.

**Market pricing claims were checked and found to be cherry-picked.** See §11.

**One claim was not checked and should not be relied on:** the Google AI Overviews click-behaviour study (arXiv:2608.04831, cited for the "~1% of AI Overview visits produce a cited-source click" figure). The conclusion drawn from it in this response — that click attribution is infeasible at Mighty's scale — holds on volume grounds regardless of whether that specific figure is accurate, so nothing here depends on it.

---

## 1. Pseudoreplication — the central claim, and my own retraction

### The claim

> 10 questions × 10 runs × 3 surfaces is not 300 independent observations. It is 10 underlying questions with repeated stochastic observations. The power analysis treats repeated runs as sample size, and it should not.

This is the review's strongest point and it is correct as a statement about statistics. What follows is what happens when it is applied to this specific design.

### Step 1: measure the ICC from data already in the repo

`research/step5_recheck_log.jsonl` contains 40 questions × 3 repeated Perplexity draws, each scored TRUE/FALSE by the Haiku classifier. That is a clustered binary dataset that was sitting unused.

Vote distribution across the 40 rechecked questions:

| votes | questions |
|---|---|
| 0/3 | 18 |
| 1/3 | 2 |
| 2/3 | 4 |
| 3/3 | 16 |

ANOVA intraclass correlation estimate: **ICC ≈ 0.80**. Grand mean p = 0.483.

Design effects and effective sample sizes on that basis:

| runs per question (m) | design effect | 10 questions → effective n |
|---|---|---|
| 3 | 2.61 | 11.5 |
| 5 | 4.22 | 11.9 |
| 10 | 8.24 | 12.1 |

On this reading, raising `fixed_fee_positioning` from N=5 to N=10 bought roughly **0.2 of an effective observation for about $13**.

### Step 2: argue against that

Two objections to the above, both of which I think are correct:

**(a) `is_product` is not `brand_mentioned`.** "Does *any* firm get named" is almost purely structural — an informational question returns zero on every draw, which is exactly why 34 of 40 questions sit at 0/3 or 3/3. Whether *one specific small firm* is selected from a candidate set of ten is a far more stochastic outcome. The true ICC on `brand_mentioned` is probably materially lower — a 0.3–0.6 range is a reasonable guess, and Schulte et al.'s 45–59% day-to-day brand overlap is consistent with substantial-but-not-total stability rather than ICC 0.8.

**(b) More important: the design effect applies to comparisons between *different* questions. The baseline→after comparison uses the *same* questions.** Between-question variance is shared by both arms and largely differences out. The clustering penalty does not apply to a paired comparison in the way the review implies.

### Step 3: simulate it

3,000 replications. Question-level baseline rates drawn logit-normal around a true baseline of 5% (sd 1.5 on the logit scale); +10pp true lift; α = 0.05.

**Power, baseline→after on the same questions:**

| design | naive pooled z-test | paired per-question bootstrap |
|---|---|---|
| 10q × 10r | 53% | 65% |
| 10q × 5r | 30% | 39% |
| 16q × 6r | 53% | 61% |
| 20q × 5r | 53% | 62% |
| 25q × 4r | 53% | 59% |
| 33q × 3r | 51% | 58% |

**False positive rate under a true null (nominal 5%):**

| design | naive pooled z-test | paired bootstrap |
|---|---|---|
| 10q × 10r | 1.7% | 4.3% |
| 20q × 5r | 1.5% | 3.8% |

### What this means

**Appendix K's N=5→10 decision was correct.** It roughly doubled real power (30% → 53% naive, 39% → 65% paired). My initial reading — that the increase was wasted — was wrong, and is retracted here. The clustering argument does not apply to the paired comparison, because pairing is precisely the mechanism that removes the clustered variance component.

**And on the paired comparison the naive test is conservative, not liberal** — a 1.5–1.7% false positive rate against a nominal 5%. It under-claims rather than over-claims.

### Step 4: but the headline test in Appendix M is not the paired comparison

Appendix M's significance test is:

```python
counts = np.array([test_hits_after, control_hits_after])
nobs   = np.array([test_n_after,   control_n_after])
stat, pval = proportions_ztest(counts, nobs)
```

That compares the **test cluster to the control cluster** — entirely different questions in each arm. There, between-question variance does not cancel, and the clustering penalty applies in full.

Simulated false positive rate under a true null (no real difference between arms), nominal α = 5%:

| comparison | observed FPR |
|---|---|
| 10q test vs 26q control, m=5 | **13.9%** |
| 10q test vs 26q control, m=10 | **22.5%** |
| 10q test vs 8q control, m=10 | 23.3% |
| 10q test vs 8q control, m=5 | 14.5% |
| 10q test vs 26q control, m=10, heterogeneity halved | 10.0% |

Three to five times inflated. And note the direction of the m effect: **more runs makes it worse.** Additional runs sharpen each question's individual estimate without adding independent units, so between-question heterogeneity comes to dominate a larger share of the observed variance. The N=5→10 increase, which *helped* the paired test, actively *worsened* the between-cluster test.

This is the real bug. It is not "the power analysis is too optimistic." It is: **the significance test currently written into Appendix M would produce a false positive roughly one time in five, in a project whose entire selling proposition is not producing false positives.**

### Recommendation

- **Primary analysis: per-question rate difference, baseline→after, bootstrapped over questions.** This is a paired design, it is the strongest comparison available, and it has approximately correct coverage.
- **Test-vs-control cluster comparison: demote to descriptive.** Report the deltas side by side as a drift check. Do not run `proportions_ztest` on it and do not report a p-value from it.
- If a formal between-cluster test is wanted later, it needs a clustered or mixed-effects model with question as a random effect — not a two-proportion z-test.

This is a small edit to Appendix M and one to Appendix K's framing. It should be made before the baseline checkpoint runs, because it determines what is worth measuring.

### The cost of the fix, stated honestly

Demoting the test-vs-control comparison weakens the "control group" language that is the project's stated commercial differentiator. This is a real trade-off, not a free correction.

The honest resolution: the control group still does its job — it detects market drift, which is Trap #1 from Part 0 and the reason it exists. What it cannot do at this N is carry a *p-value*. "Test moved 12pp, control moved 1pp, and here is why that comparison is directional rather than significant at this sample size" is still a stronger claim than any competitor in this market makes, and it is defensible. A p-value from a test with a 22% false positive rate is not.

---

## 2. Matched pairs

### The claim

Topic-level test/control confounds the intervention with the topic. Use minimal pairs instead:

- Treatment: *"best fixed-fee accountant for a UK contractor"*
- Control: *"best accountant for a UK contractor"*

### Assessment

Simulated at 10 pairs × 10 runs with pair correlation 0.8: **55% power** for a +10pp differential. 10 pairs × 5 runs: 36%. 16 pairs × 5 runs: 46%. Comparable to the paired baseline→after test.

**Argument against, which neither review pass raises:** the intervention is **web-level, not query-level**. If a directory listing simply raises Mighty's overall citation surface, it lifts both arms of every pair and the matched comparison reads null while a real effect exists. Matched pairs therefore test a narrower hypothesis — *does fixed-fee-specific evidence preferentially move fixed-fee-framed queries* — not *did the intervention work*.

**Argument for, which is stronger than the confounding argument the review actually makes:** matched pairs are the only comparison in the design that is robust to **market drift**. The paired baseline→after test is not — if AI visibility for all UK contractor accountants rises over four weeks, that test happily calls it a win. Guarding against exactly this is why the control group exists, and the tiered-control comparison that was meant to catch it is the one with the inflated false positive rate.

### Recommendation

Add, at reduced scale: **8 pairs × 5 runs**, roughly $12 across baseline and after. Report as a secondary, drift-robust read alongside the primary paired test. Do not replace the topic-level tiering with it — the tiering is already built, costs nothing extra, and answers a different question.

---

## 3. More questions vs more runs

### The claim

Repeated runs estimate variance; questions estimate the effect. Spend on questions.

### Assessment

**Wrong, or at least not supported.** Budget-neutral at ~100 calls on the test cluster, paired analysis:

| design | power |
|---|---|
| 10q × 10r | 53% |
| 20q × 5r | 53% |
| 33q × 3r | 51% |

Essentially flat. My own earlier assertion that "more questions beats more runs" was made with unearned confidence and is retracted alongside the N=5→10 claim.

The choice is therefore not about power. It is about what can be claimed:

- **More questions** buys generalisability — "this holds across a range of phrasings."
- **More runs** buys distribution characterisation — the variance, the ICC, the runs-to-stability curve. That is the publishable methodology finding (§15).

### Recommendation

**No change.** Keep 10 × 10 on the test cluster. Do not reallocate the budget.

---

## 4. The product-question filter

### The claim

The filter is circular: Perplexity decides which questions count, and Perplexity is then one of three measured surfaces. A question with real commercial value that happened not to name firms on Perplexity that day was deleted for the wrong reason.

### Assessment

The circularity is real. The damage is smaller than implied, and the review under-credits the work already done — an N=3 majority-vote recheck with every raw answer logged was already run on the four clusters most likely to be unreliable.

The six FALSE-tagged `fixed_fee_positioning` rows:

| id | question | recheck votes |
|---|---|---|
| q019 | is pay monthly or one off accountant better | F,F,F |
| q020 | fixed monthly fee vs one off accountant fee which is better value | F,F,F |
| q021 | sick of surprise invoices from my accountant, is there a fixed fee option | F,F,F |
| q024 | looking for predictable accountant costs, hate surprise bills | F,F,F |
| **q026** | **accountant that actually understands one person consultancies, fixed monthly cost** | **F,T,F** |
| q064 | accountant with a simple monthly plan for a small limited company | F,F,F |

And three questions in the *kept* set were also borderline: q023 (T,F,T), q025 (F,T,T), q027 (F,T,T).

So the TRUE/FALSE boundary is a thresholded stochastic variable for roughly 15% of questions. One question — q026 — was deleted on a 1/3 draw.

### The more interesting version of the point

`is_product` should not be binary. It is a **rate**. A question at 1/3 is not worthless; it has a lower ceiling for *anyone* getting named, which is directly relevant context when interpreting a low `brand_mentioned` rate on that question. Storing the vote fraction rather than the binary costs nothing and preserves information currently being thrown away.

This is also, incidentally, the same phenomenon the whole project is about — a stochastic AI output being collapsed to a single-draw binary — appearing inside our own tooling.

### Recommendation

Low priority. Recover q026 with a `borderline` tag; store the vote fraction alongside the binary. Do not re-run the filter across a second surface; the cost/benefit does not justify it for one or two questions.

---

## 5. Intervention design — the largest gap

Both review passes flag that the interventions are weak. Neither quantifies it. It is quantifiable from Day 1 data.

`research/day1-category-check.md` was parsed into its 20 model×question cells and each checked for citations to the planned intervention targets:

| domain | cells citing it |
|---|---|
| crunch.co.uk | 10/20 (50%) |
| reddit.com | 9/20 (45%) |
| contractoruk | 8/20 (40%) |
| limitedcompanyhelp | 6/20 (30%) |
| umbrellacompany | 3/20 (15%) |
| **any of the three planned directories** | **11/20 (55%)** |
| mightyaccounting.com | 1/20 (5%) |

**The intervention has a real mechanism in 55% of answers** — considerably better than "these are weak levers" implies.

But 55% is not the ceiling. Being *listed* on a cited directory is not being *named* in the answer; the directory lists dozens of firms and the model selects three to six. At a plausible 15–25% conditional selection rate, the realistic ceiling is **roughly 8–14pp**.

That lands almost exactly on the +10pp Appendix K assumed. That assumption was previously a guess; it is now an evidence-backed estimate and should be written into Appendix K as such.

### The per-surface split is the finding

| surface | planned directories present | reddit present |
|---|---|---|
| Perplexity | 4/5 | 4/5 |
| ChatGPT | 4/5 | 5/5 |
| Claude | 2/5 | **0/5** |
| Gemini | 1/5 | **0/5** |

**Claude and Gemini cite neither Reddit nor the target directories. The planned intervention has almost no mechanism to move them.** Pooling three surfaces when one is structurally immovable by the treatment guarantees dilution of any real effect.

This independently confirms **Perplexity as the primary surface**: highest directory leverage, and Mighty at genuine zero there per Day 1. That recommendation was previously a hunch; it now has evidence behind it.

### Recommendation

- Write the 8–14pp ceiling estimate into Appendix K, replacing the unsourced +10pp assumption.
- **Log the three interventions as separate `type` values** in the `interventions` table (`directory`, `forum`, `social`) rather than as one undifferentiated treatment. The table already has a `type` column that was not being used distinctly. This costs nothing and lets the after-checkpoint's `cited_urls` data attribute which lever, if any, carried the movement.
- Do not expect Claude or Gemini to move. Say so in advance, in writing, so it reads as a prediction rather than an excuse.

---

## 6. Multiplicity across surfaces — a gap nobody flagged

Both review passes push per-surface analysis, and there is good external support: industry measurement work reports that only around 11% of domains are cited by both ChatGPT and Perplexity on the same queries. Pooling really does average three different systems.

But splitting three ways gives three chances to find significance at α = 0.05. Family-wise error is approximately 14% before any of the clustering problems above are even considered. Neither review pass raises this, and it is the easiest remaining way to accidentally manufacture a false positive after all this care.

### Recommendation

**Pre-register one primary surface before the baseline checkpoint runs.** Perplexity, on the evidence in §5. The other two are secondary and reported without p-values. Write the pre-registration into the plan doc with a date, so it is verifiably prior to seeing the data.

---

## 7. Astroturfing and disclosure

The second review pass calls for a bold line on this. It is right, and it is currently a buried bullet in the Week 2 section.

Week 2's intervention list includes a forum mention. Reddit is actively fighting covert promotional manipulation, and the AEO field has an existing reputation problem in exactly this area. Two things need to be explicit and prominent, not implicit:

1. **No manufactured evidence, ever.** No sock-puppet accounts, no seeded comments, no paid covert mentions, no invented customer experiences. If a mention is not true and useful on its own terms, it does not get posted. This applies to the case study and to any future client work, and it is a standing rule rather than a per-engagement judgement.
2. **Disclosure.** Any forum or social mention of Mighty is made by someone who is not a Mighty customer, in the context of running an experiment on Mighty. That needs disclosing in the post itself, not only in the project notes.

The commercial reason, not just the ethical one: the moment this becomes a product sold to clients, "AEO means manipulating AI" is the reputational failure mode that ends the business. The defensible position is *measurement plus legitimate evidence creation*.

---

## 8. Parser: gold set and recommendation-vs-mention

### Gold set

Both passes call for a manually-labelled validation set — the second asks for ~100 answers with precision, recall and false-positive rate. Appendix G currently specifies a 30-sample eyeball check.

Neither is a blocker for the baseline run, because `raw_answer` is stored in full. **Every parser improvement is retroactive** — re-parsing is a Haiku call against stored text, not a re-run of the experiment. This is a genuine strength of the existing design that neither review credits.

**Recommendation:** after baseline, label ~60 stratified answers by hand (stratified on surface and on parser-predicted outcome, to get enough positives). Report precision, recall and FPR on `brand_mentioned` specifically. Do not attempt to validate `sentiment` to the same standard — it is a secondary field and the labelling burden is disproportionate.

### Recommendation vs mention

The second pass's example is exactly right: *"Mighty Accounting is a small UK accountant. However, Gorilla Accounting has more experience..."* counts as a mention and is not a win.

The parser already returns `brand_position` and `sentiment`, so a `recommended` flag is nearly derivable — but it should be an explicit field with its own prompt rules, not inferred downstream.

**Recommendation:** add `recommended` (boolean) and `recommendation_rank` to the parser schema. **Recommendation share becomes the primary KPI; mention share becomes secondary.** Retroactive, so it does not block baseline — but adding the field to `schema.sql` before the run is cheaper than an `ALTER TABLE` after.

---

## 9. Reporting hygiene and language rules

Small, free, and worth writing in as standing constraints.

**Reporting:**

- **Never report "n=300."** Always report the four numbers separately: unique questions, runs per question, surfaces, and unique question×surface combinations. The single pooled figure is the exact overclaim the review is objecting to, and stating the components makes it unavailable.
- Report per-surface alongside pooled, always. Already corrected in Appendices K and M; keep it.
- Report **retrieval-source visibility** as a first-class output, not just brand visibility — "72% of answers cite Reddit, 40% cite ContractorUK, 5% cite mightyaccounting.com." Appendix I's citation-frequency query already produces this; it should be promoted from a working query to a headline deliverable, because it is the most actionable thing the rig produces.

**Language:**

1. **Never say "caused."** Say "we observed a statistically significant increase in the treatment queries." Given §1, this is accuracy, not modesty.
2. **Never equate visibility with market share.** There is no query volume data for AI questions — that is a stated premise of the whole project. It is "measured AI recommendation visibility," never "% of potential customers reached."
3. **API-vs-consumer caveat in the first sentence of every output**, not in a methodology footnote. Already a principle in Part 0; make it a fixed template line so it cannot be forgotten under deadline.

---

## 10. Question sourcing

The second pass notes that questions came from brain dump → Claude expansion, which measures questions that *sound* plausible rather than questions people actually ask.

This is a real methodological gap and it is cheap to at least partially close. Day 1 already identified `forums.contractoruk.com` and `r/ContractorUK` as heavy citation sources — those forums are simultaneously a corpus of how contractors actually phrase this, in their own register. Pulling 20 real thread titles and comparing them against the authored phrasings would either validate the list or expose a systematic register mismatch.

**Recommendation:** not urgent, does not block baseline, but much cheaper to check now than to be told by a reviewer later. Roughly two hours.

---

## 11. Commercial: the commoditisation claim, checked

### The claim

Measurement is commoditised. Renownly sells a £129 audit and £29/month monitoring; therefore "I measure AI visibility," "I run queries five times," and "I use four platforms" are all commodity features and none of them is a moat.

### What checking found

The £129 figure is accurate — Renownly's own decision guide presents three routes: DIY for free, a one-off £129 audit, or an agency retainer. But that is the bottom of a **stratified** market, not the market.

Also currently live:

- Specialist agency audits at **£2,000–£5,000** as one-time engagements; one provider's audit starts at £2,500 covering 50+ prompts across five platforms over 14 business days.
- Self-serve GEO software at **$95–$828/month** without interpretation.
- Monitoring-only subscriptions at **$99–$295/month** (Gauge, AthenaHQ).
- Mid-tier AI visibility platforms at **$500–$2,000/month**.
- One European survey describes GEO audits ranging from €200 to €15,000 for services of radically different real value, attributing the dispersion primarily to method maturity.

So the market is stratified along **exactly the axis this project is building on**. One competitor's own buyer guide argues that credible measurement runs prompts repeatedly over a period rather than grabbing one day's answers, and that anyone promising a full audit in 48 hours is selling a snapshot.

### Assessment

The review cherry-picked the cheap end. The **snapshot** is commoditised; the **methodology** tier is not. The plan's existing "everybody is selling a photograph; you're the only one offering a video" line survives this better than the review allows — and unlike "uncontested," it survives someone checking.

**But one part of the criticism does land:** it is not enough to *have* a better methodology. Until a successful intervention has actually been run, "I measure whether an intervention works" is a proposition, not a demonstrated capability. The first credible before/after experiment is the commercial asset, not the software.

### Recommendation

Soften the review's pessimism; adopt its ladder. Entry at **£99–£299 for an audit** before any £500+/month retainer conversation. Do not lead with monitoring, which is where the commodity pressure actually is.

---

## 12. Commercial: buyer, channel, naming, platform risk

**Google, not Gemini, is the bigger platform gap.** Both passes flag the missing Gemini surface. The second correctly points at Google AI Overviews / AI Mode as the actual distribution channel. Day 1 data adds a reason to care less about Gemini specifically: it cited neither Reddit nor any target directory, so it is both hard to move by the planned intervention *and* not the important Google surface. If a fourth surface is added post-baseline, AI Overviews is the higher-value target. Both stay after the three-surface rig is validated.

**Test agencies in parallel, not in reserve.** Currently path 5 in the Day 30+ plan. The second pass is right to promote it: an agency already understands retainers, reporting, rankings and churn, so the education step disappears entirely, and one agency represents 10–50 end clients. Concretely: when the 5–10 person demand test runs, make three of them agencies rather than adding agencies as a later pivot.

**Sharpen the vertical selection rule.** The kill-criteria demand test already widens beyond accountants. Add the actual criterion: target verticals where one client is worth £5k+, because that is what makes a £500/month programme arithmetically defensible for the buyer. Contractor accountancy at roughly £60/month per end client is close to worst-case economics in professional services — which is fine for a *case study* and poor for a *first customer*. The plan already ranks direct retainer sales to Mighty last; this is the reason, stated numerically.

**Naming.** Drop "30-day" — it is 6–8 weeks and the plan already says so, so the label is a self-inflicted credibility problem. Drop "AEO" from anything client-facing; *"How often does ChatGPT recommend your business?"* is the headline and the technical category sits underneath. Both free.

**Platform risk.** Neither the plan nor the review's framing acknowledges that OpenAI, Google, Anthropic and Perplexity can change models, retrieval, citation behaviour, API shape and pricing overnight — something this project has already been bitten by once, when `gpt-4o-search-preview` turned out to be past its shutdown date. This is an argument *for* the positioning rather than against it: a business whose value is "we know the algorithm" dies on those changes; one whose value is "we continuously measure what changed" gets stronger each time they happen. Worth a paragraph in Part 0.

---

## 13. Where the two review passes contradict each other

Worth recording, because the contradictions are informative about which conclusions are stable.

| Question | First pass | Second pass | Verdict |
|---|---|---|---|
| Approach Mighty before baseline? | Yes — commercially better, unlocks stronger interventions | **No** — explicitly reverses; baseline contamination | Second pass. No change to plan. |
| Track revenue attribution from day one? | Yes, build it in immediately | Undercuts itself: AI Overview clicks ~1%, so it is brand influence not traffic | Not feasible at Mighty's volume. No change. |
| Realistic SMB pricing? | £500–£1,000/mo plausible (7/10) | £29–£199 commodity band; £500+ requires implementation (5/10 for SMB monitoring) | Second pass is better sourced, and it vindicates the plan's existing ranking. |

The second pass being willing to reverse its own recommendation is the main reason to weight it more heavily than the first.

---

## 14. What is stale

A substantial fraction of the first pass critiques a build that has already happened. Ground truth from the repo:

| Review recommendation | Actual state |
|---|---|
| "Don't overbuild before selling" | `schema.sql`, `parser.py`, `rig.py`, `estimate_cost.py` are all built, smoke-tested against live APIs, and cost ~$63 remaining to run |
| "Don't rent Hetzner" | Already deprioritised; local-first, no recurring cron |
| "Don't build a dashboard" | Was never in the plan |
| "Version 0: 20–30 questions × 4 platforms × 5 reps, one good report" | Materially what exists, minus Gemini |
| "Rename from 30 days to a pilot" | Timeline reality check already in the plan; the label is not |
| "Correct the uncontested-niche claim" | Already corrected in the plan, with the source of the original error identified |
| "The result is directional, not proof" | Already the plan's own framing |

The build-versus-sell trade-off the first pass warns about is already resolved. The marginal remaining cost is roughly $63 and a handful of evenings.

---

## 15. The reframe

Both passes circle this without landing on it, and the empirical work above sharpens it.

**Stop trying to prove "can I move AI visibility."** The intervention list is weak (though not as weak as claimed — see §5), the power is genuinely marginal, and a null result there is ambiguous: it would establish only that three specific cooperation-free interventions did not move these specific queries in this period.

**The baseline checkpoint alone is a publishable asset.** It answers questions the field does not currently have answers to:

- What is the intraclass correlation on brand mentions within a question? Schulte et al. do not report one.
- How many runs are actually needed before a visibility estimate stabilises?
- How much do the three surfaces disagree, on the same questions, at the same moment?
- Where is the citation evidence concentrated, and how much of it is reachable?

This needs no intervention, no Mighty cooperation, and **cannot produce a null**. It plugs directly into an academic conversation that is already running. And "here is how many runs you actually need, measured" is a considerably harder thing for a £129 audit to copy than "here is your score."

The intervention experiment then ships as a second, clearly-labelled, honestly-underpowered pilot on top of the methodology finding — rather than being the thing the entire project stands or falls on.

This also resolves the tension in §1: demoting the between-cluster significance test costs much less if the headline finding was never that test in the first place.

---

## 16. Decision list, ordered

### A. Before the baseline checkpoint runs

| # | Change | Cost | Why now |
|---|---|---|---|
| 1 | Rewrite Appendix M's primary test as a per-question paired bootstrap; demote test-vs-control to descriptive | ~30 min | The only genuinely load-bearing fix. 22% FPR otherwise. |
| 2 | Pre-register Perplexity as the primary surface, dated | ~10 min | Family-wise error ≈14% across three surfaces; must be prior to data |
| 3 | Log the three interventions as distinct `type` values | 0 | Column already exists; enables attribution later |
| 4 | Add the astroturfing/disclosure rule prominently to Week 2 | ~15 min | Currently a buried bullet on a live risk |
| 5 | Write the 8–14pp ceiling estimate into Appendix K | ~15 min | Replaces an unsourced assumption with an evidenced one |
| 6 | Add `recommended` / `recommendation_rank` to `schema.sql` and the parser prompt | ~30 min | Cheaper than `ALTER TABLE` later; makes recommendation share the primary KPI |
| 7 | `config.yaml` for brand, competitors, questions | ~1 hr | Cheapest item on the list today, painful retrofit after |
| 8 | Add 8 matched control pairs at N=5 | ~1 hr + ~$12 | Only drift-robust comparison in the design |
| 9 | Recover q026 as borderline; store `is_product` vote fraction | ~15 min | Low value, trivially cheap |

### B. After baseline, before Week 2

- Run the baseline gate (already in the plan), pooled **and** per-surface.
- **Compute the ICC on `brand_mentioned` from the real data.** This is the number the whole §1 argument turns on, and it is currently a guess. Recompute honest power against the measured value before committing any Week 2 effort.
- Label ~60 stratified answers by hand; report parser precision, recall and FPR on `brand_mentioned`.

### C. Not before baseline, but decide the direction now

- Question sourcing cross-check against real ContractorUK / Reddit phrasings (~2 hrs).
- Google AI Overviews as the fourth surface, ahead of Gemini.
- Fold three agencies into the 5–10 person demand test.
- Drop "30-day" and "AEO" from anything client-facing.
- Add the platform-risk paragraph to Part 0.

### D. Rejected

| Recommendation | Reason |
|---|---|
| Revenue attribution from day one | Un-measurable at Mighty's volume; the two passes contradict each other on it |
| Approach Mighty before baseline | Second pass self-reversed; contamination is irreversible |
| "Don't build, sell first" | The build is done; ~$63 remains |
| Rebuild the design around matched pairs | Add as a secondary read; do not demolish working tiering |
| Reallocate budget from runs to questions | Power-neutral under the correct analysis (§3) |

---

## 17. Where this response could itself be wrong

Stated explicitly, because the failure mode of a document like this is confident correction of someone else's confident correction.

1. **The ICC of 0.80 is measured on the wrong outcome.** `is_product` is far more structural than `brand_mentioned`. The true value is probably lower, and the whole design-effect argument softens if so. This is measurable from the baseline run and should be measured rather than assumed. It is listed in §16B for exactly that reason.

2. **The 8–14pp intervention ceiling rests on an invented conditional selection rate.** The 55% directory-presence figure is real and computed from Day 1 data. The 15–25% "probability of being named given the directory is cited and you are listed on it" is a guess. If the true rate is 5%, the intervention is decorative and the experiment cannot succeed at any N. This is the single weakest link in this document.

3. **The simulations assume a logit-normal distribution of question-level baseline rates with sd 1.5.** That shape was chosen, not measured. The false positive rates in §1 are sensitive to it — halving the heterogeneity drops the between-cluster FPR from 22.5% to 10.0%. The direction of the finding is robust; the magnitude is not.

4. **Day 1's per-surface citation counts are n=5 questions per surface.** The Claude 2/5 and Gemini 1/5 directory-presence figures are suggestive, not established. Treating "Claude and Gemini cannot be moved by this intervention" as settled on five observations would repeat exactly the single-draw error this project exists to correct.

5. **The market-stratification argument in §11 is built on provider marketing copy**, which is the same category of source that produced the original "uncontested niche" error. The £129 and £2,500 figures are real; the inference that the market is stratified by *method maturity* rather than by *sales ability* is not established.

None of these change the ordering in §16A, because every item there is cheap and most are corrections to things that are wrong regardless of how these uncertainties resolve. They do mean the baseline run should be treated as the point at which several of these guesses get replaced with measurements.

---

## Appendix: reproducible code for the empirical checks

### ICC from the existing recheck log

```python
import json
lines = [json.loads(l) for l in open('research/step5_recheck_log.jsonl')]
m, k = 3, len(lines)
ys = [sum(1 for v in l['votes'] if v) for l in lines]
n = k * m
pbar = sum(ys) / n

msb = sum(m * ((y / m) - pbar) ** 2 for y in ys) / (k - 1)
ssw = sum(y * (1 - y / m) ** 2 + (m - y) * (y / m) ** 2 for y in ys)
msw = ssw / (n - k)

icc = (msb - msw) / (msb + (m - 1) * msw)
print(f"ICC = {icc:.3f}")
for mm in (3, 5, 10):
    deff = 1 + (mm - 1) * icc
    print(f"m={mm}: design effect {deff:.2f}, 10q -> effective n {10*mm/deff:.1f}")
```

### Power and false-positive simulations

```python
import numpy as np
from statsmodels.stats.proportion import proportions_ztest
rng = np.random.default_rng(7)

def logit(p): return np.log(p / (1 - p))
def inv(x):   return 1 / (1 + np.exp(-x))

def sim_paired(k, m, lift, base=0.05, sd=1.5, effect_sd=0.0, reps=3000):
    """Baseline -> after on the SAME questions. Between-question variance cancels."""
    mu = logit(base); naive = paired = 0
    for _ in range(reps):
        p0 = inv(rng.normal(mu, sd, k))
        p1 = np.clip(p0 + lift + rng.normal(0, effect_sd, k), .001, .999)
        x0, x1 = rng.binomial(m, p0), rng.binomial(m, p1)
        _, pv = proportions_ztest([x1.sum(), x0.sum()], [k*m, k*m])
        if pv < 0.05 and x1.sum() > x0.sum(): naive += 1
        d = x1/m - x0/m
        bs = rng.choice(d, size=(2000, k), replace=True).mean(axis=1)
        if np.percentile(bs, 2.5) > 0: paired += 1
    return naive/reps, paired/reps

def sim_between(k_t, k_c, m, true_diff=0.0, base=0.05, sd=1.5, reps=4000):
    """Appendix M's headline test: DIFFERENT questions in each arm. Clustering bites."""
    mu = logit(base); sig = 0
    for _ in range(reps):
        pt = np.clip(inv(rng.normal(mu, sd, k_t)) + true_diff, .001, .999)
        pc = inv(rng.normal(mu, sd, k_c))
        xt, xc = rng.binomial(m, pt), rng.binomial(m, pc)
        _, pv = proportions_ztest([xt.sum(), xc.sum()], [k_t*m, k_c*m])
        if pv < 0.05: sig += 1
    return sig / reps

# Set true_diff=0.0 to read the false positive rate.
print(sim_between(10, 26, 10))   # ~0.225 against a nominal 0.05
```

### Day 1 per-answer directory presence

```python
import re
lines = open('research/day1-category-check.md').read().split('\n')
cells = [l.lower() for l in lines
         if l.startswith('| ') and any(m in l[:14]
         for m in ('ChatGPT', 'Claude', 'Perplexity', 'Gemini'))]

planned = ('contractoruk', 'umbrellacompany', 'limitedcompanyhelp')
hits = sum(1 for c in cells if any(p in c for p in planned))
print(f"{hits}/{len(cells)} cells cite at least one planned intervention target")
```
