# Plan Challenge — Adversarial Review of the AEO Measurement Project

*Referenced from: the main plan ([aeo-30-day-plan-mighty.md](aeo-30-day-plan-mighty.md)) and code appendix ([aeo-code-appendix-mighty.md](aeo-code-appendix-mighty.md)).*

**What this is:** a deliberately adversarial stress-test of the plan, run via four parallel research agents — methodology, execution feasibility, market viability, and a pure devil's-advocate pass on whether this is worth doing at all. Each was briefed to actively hunt for flaws, not to be diplomatic. This doc captures their findings, the synthesis, and a concrete plan for the monetization phase the original 30-day plan never actually scoped.

**Bottom line going in:** the tool-building is worth doing. The business thesis as originally scoped has real cracks — mainly in the "uncontested niche" claim, the 30-day timeline, and the causal-proof framing. None of these are fatal; they mean *adjust scope and claims*, not *stop*.

---

## 1. Methodology — can the stats support the causal claim being sold?

**Verdict: No, not as currently specified** — for the strong claim ("we moved this, not the market"). Could support a **yes-with-caveats** directional/hypothesis-generating claim if reframed.

### High severity

**Randomization unit vs. sample size.** Cohort assignment (Appendix J) randomizes at the *topic* level. After the real `is_product` filter ran on the actual 68-question dataset, `new_company_setup` came back with **zero** surviving product questions (0/7) — it silently drops out of cohort assignment, leaving **7** usable topics, not the "6-8" the plan assumes. Split into test/control/holdout, that's roughly 3/3/1 topics per arm. Topic sizes also vary 4.5x (general_recommendation kept 9/10 questions after filtering; tax_efficiency kept only 2/10). Randomizing this few, this uneven, a set of units means a convincing-looking delta between test and control is nearly as likely to be topic-composition luck as a real intervention effect — no amount of within-arm confidence-interval math fixes a design where the units being randomized are this few and this heterogeneous.

**API vs. consumer product.** The rig calls raw `sonar`, `claude-sonnet-4-5` + explicit `web_search` tool, and `gpt-4o-search-preview` — not the default consumer experience most buyers of "AI visibility" actually mean (no memory/personalization, different default search-triggering thresholds, a model pin consumer apps may not use). This is a real construct-validity gap between what's measured and what's sold as "how people actually experience AI." If a client manually checks the ChatGPT app and gets a different answer than the rig reports, the "rigorous" positioning collapses fast.

**N=5 runs, sliced four ways.** Once crossed by surface (3) × cohort × topic × before/after, cells for smaller topics (tax_efficiency: 2 product questions) collapse to ~n=10 runs per surface per period. Binomial confidence intervals at that n are enormous — a single flip moves the point estimate 10+ percentage points.

### Medium severity

**Gemini gap.** Confirmed directly in `rig.py`: `SURFACES = {"perplexity": ..., "claude": ..., "openai": ...}` — no Gemini anywhere, despite Day 1's manual test including it by hand and the plan's own framing claiming coverage "across four AI platforms." This is an easily-checked, easily-embarrassing overclaim — someone just has to ask "show me the Gemini numbers."

**LLM-as-judge circularity.** Both the `is_product` filter and the mention parser are Claude Haiku judging its own category of task, validated only by a 30-sample manual spot-check plus an informal "N=3 recheck" pattern. No inter-rater reliability stat, no held-out human-labeled gold set, no check for *systematic* (vs. random) bias.

**Power analysis boundary cases.** Appendix K correctly special-cases a 0%/100% baseline and is honest about not forcing a power calc at a true zero — one of the more self-aware parts of the plan. Still flagged medium because several topics (tax_efficiency at 2/10 baseline) sit close enough to the boundary that MDE calculations will be unstable in practice.

### What's genuinely well-designed

The control-group discipline against the "misattribution" trap, the holdout set for ambient drift, structured LLM parsing over regex (with an explicit adversarial test set for "Mighty Networks" and the plain adjective "mighty"), per-row error logging instead of silent failure, and the "before you believe anything" checklist — all more rigorous than anything else visible in this market. The Day 1 empirical honesty (correcting the competitor set, flagging QAccounting overweighting) is genuinely good practice, rare in this space.

---

## 2. Execution & timeline feasibility

**Verdict: Not achievable as scoped in 30 days.** Realistic estimate: **45-55 days.**

### Repo state (ground truth, not narrative)

- `research/questions.csv`: fully populated, no blanks — Day 2 is genuinely done.
- `requirements.txt`: real, matches Appendix A.
- `src/rig.py` (61 bytes), `src/parser.py` (22 bytes), `src/schema.sql` (~14 bytes): **all three are empty stubs.** None of Appendix H/G/F has actually been written. The instrument does not exist yet.

Days 1-2 being done was the low-risk, no-code half of the plan. ~100% of the coding, infra, and stats work is still ahead.

### Why 30 days is optimistic

Remaining work: write `rig.py`/`parser.py`/`schema.sql` from scratch (first real Python project), debug three different SDKs' citation/annotation shapes (the appendix itself admits these "shift between SDK versions"), provision and harden a Hetzner box, get cron + VS Code Remote-SSH reliable, run enough unattended nights for a real before/after comparison, execute a real content intervention on someone else's live site, run cohort assignment, run a power analysis that may come back saying "can't detect anything," run significance tests, and write a publishable case study — as a first-time Python developer. Each is individually a multi-day task for a beginner; several (SDK debugging, SSH/cron reliability) typically eat 2-3x the estimate on a first attempt.

### Top risks, ranked

1. **Silent unattended failure, undetected for days.** No dead-man's-switch, no alerting if cron stops firing or every call errors out. Directly corrupts the before/after comparison the whole pitch depends on.
2. **Three new skills at once** — Python, three REST/SDK integrations, Linux/cron/SSH admin — learned simultaneously under time pressure, on infrastructure a business pitch rests on.
3. **Dependency on Mighty actually implementing a content change** on a live commercial site inside a compressed window — entirely outside the builder's control.
4. **Power analysis may return "cannot detect anything"** — Mighty was cited once in 40 Day-1 answers; several clusters will likely sit at literal 0%.
5. **Cost creep at 3am** — mitigated by account-level billing caps, but no per-run spend ceiling in the code itself.

### Confirmed facts

- **Gemini is not implemented anywhere in the automated rig** — confirmed by reading `SURFACES` directly. Adding it is not hard: Gemini's Search grounding API is comparable to what's already built for the other three (5,000 free grounded prompts/month, then $14/1k — comfortably covers this rig's volume). Roughly a few hours of work, not days — but currently unscheduled anywhere.
- **Hetzner CX22 cost checks out**: €4.35-4.59/month currently, matching the plan's €4.50 estimate. The £20-35 total budget is still directionally accurate.
- **Reliability engineering is solid for what it covers**: try/except per call, commit-per-row, errors logged as rows not silence, jittered sleep. Missing: retry/backoff on transient failures, and any alerting layer.

---

## 3. Market viability — is the niche and pricing real?

**Verdict: legitimate learning project (moderate-high confidence); weak, unproven business thesis for this specific target (low confidence).**

### The niche is not uncontested

Two of the three competitor names in the plan checked out as real, active, and already targeting this exact sub-niche:

- **Renownly** has already published first-party research on 93 UK accountancy firms across three niches, including **28 IR35/contractor-specialist firms specifically** — the identical slice this project measures — finding only 19% have basic machine-readable AI-visibility signals.
- **GetVisus** has a dedicated `/use-cases/accountant` page offering a free 60-second audit, and asserts "the vast majority of UK accountancy practices have no AI visibility strategy... a market that is almost entirely uncontested." This is the exact source of the plan's own "uncontested" framing — meaning the evidence for "nobody's here" came from a competitor's marketing copy, written by someone who is, in fact, already here.
- **"Tramwai"** could not be verified as a real, operating company under any spelling searched. Treat as unconfirmed, possibly wrong.

### Pricing and market maturity

Real agencies with concrete pricing exist in 2026 (Rank4AI ~£1,000-1,500+/mo, Impact Digital audit+retainer, TendorAI £299/mo indexing UK accountancy firms from the ICAEW directory) — roughly corroborating the plan's $1-2.5k entry-tier estimate. But the larger, verifiable revenue case studies found (Optimist, ABM Agency, a SaaS closing $64K from a GEO campaign) are all B2B tech/SaaS companies with existing marketing budgets — not bootstrapped 5-15 person professional-services firms. **No verified case study surfaced of a small accountancy or similar SMB paying a retainer and generating attributable revenue from AEO work.**

### Is test/control rigor a real differentiator?

Genuinely underused by GetVisus and Renownly — neither shows test/control design or confidence intervals; both sell scored audits or descriptive counts. So there's a real rigor gap to exploit. Caveat: it's unclear whether a 5-15 person accountancy firm's decision-maker would value or even understand a confidence interval enough to pay a premium over a cheaper scored report.

### Base rate: does "free case study, then pitch" convert?

No direct evidence found either way for this exact genre (bespoke tool → unsolicited case study on one unengaged small business → paid retainer). Adjacent evidence is thin-to-discouraging: normal cold-email response rates are low (~2%), and professional-services firms are a notoriously referral-driven, low-marketing-spend buyer category — a risk the original plan already self-flags.

---

## 4. Devil's advocate — is this worth the time at all?

**Verdict: (B) — pursue, but change the opener before Day 1's pitch, not the build.**

### Opportunity cost

30 days of unpaid, first-time technical work, for one prospect who hasn't agreed to anything, only beats "make more content for the audience that already exists" if the project (a) finishes, (b) produces a story compelling enough to post regardless of outcome, and (c) doesn't cannibalize the posting cadence that's currently building the real asset. That's three conditions, not a given.

### Ethics/relationship risk — real, and underrated in the original plan

Search on "unsolicited audit as a sales opener" turns up a consistent pattern: a spam genre already exists built on exactly this move, and it has poisoned the well. One directly relevant data point: a solo builder sending 50 unsolicited AI-visibility audit emails to founders got **1** positive reply. A founder's default read of "I ran an unannounced analysis of your business and now I'm contacting you" is *scam*, not *flattered*, until proven otherwise. Mighty's own About page inviting open contact narrows this gap, but it's a bet on the founders' mood that day, not a controlled variable — and this is a small, tightly-networked space where a bad first impression follows you to client #2.

### Survivorship bias

No evidence found, in either direction, for the specific transition claimed: unsolicited experiment → free case study → recurring paid retainer, for a first-time solo operator with no consulting track record. The plan argues from first principles (measurement skill + niche knowledge + audience) — a reasonable capability argument, not evidence of conversion.

### Most likely failure mode, ranked

1. **It finishes fine and becomes one Instagram post, not a client** (most likely — the modal outcome for completed self-directed side projects).
2. Mighty never replies or has no budget (already self-flagged in the original plan).
3. Execution stalls before producing anything (first-time Python + unattended infra, 30 consecutive days without silent failure).
4. Null/inconclusive result with no story (least likely to be fatal — the plan's own "the null result is the case study" framing is genuinely one of its stronger, non-wishful ideas).

### Steelman

Cost is genuinely trivial (~£20-35 + time). Python/API/statistics skills transfer regardless of outcome. The niche knowledge (own IR35 contracting, own bookkeeping via Pandle) is real and rare. Worst case is still a differentiated, rigor-flagged Instagram post in a content category the audience already cares about.

---

## 5. Synthesis — what to actually change

1. **Re-scope the timeline** to 6-8 weeks. Treat that as normal for a first Python project, not a failure.
2. **Add Gemini, or explicitly narrow every "four platforms" claim to three** before this is in front of anyone.
3. **Reframe the eventual result as directional evidence, not proof.** Show topic-composition sensitivity; don't oversell the control group given the effective n=7 randomization units.
4. **Correct the "uncontested niche" claim.** At least two real competitors (GetVisus, Renownly) already target this exact sub-niche. The honest pitch is "a market with real competitors, where nobody's doing rigorous causal measurement yet" — not "uncontested."
5. **Change the opener.** Don't cold-approach Mighty with "I've been measuring you." Lead transparently with "I did this as a learning project for my audience, here's what I found, no ask." Commercial conversation becomes a possible second step, not the plan's built-in endpoint.
6. **Keep content creation as the primary channel** in the meantime. Treat this as a lower-priority side experiment that feeds content either way, not a pivot away from what's already working.

---

## Day 30+ — turning the artifact into money

*The original 30-day plan stops at "analysis and packaging." It has no monetization phase. This is the missing piece — a deliberately staged, low-commitment path from "finished case study" to "possible product," with explicit kill criteria at each stage so time isn't sunk into a direction with no real signal.*

### Ranked paths, by realistic likelihood of payoff

1. **Content/audience monetization** — highest probability, lowest risk. The case study (positive *or* null result) becomes strong content for an audience that already exists. No dependency on Mighty saying yes to anything.
2. **Portfolio/skills leverage** — high probability, indirect money. "SQL/BI depth + now Python/APIs + a real controlled experiment" is a legitimate freelance/contract signal independent of AEO as a niche.
3. **Productized tool, not bespoke consulting** — moderate probability, better economics than direct consulting. The rig scales (new brand = config change, not a rebuild) in a way competitors' manual audits don't.
4. **Direct retainer sales to Mighty or similar bootstrapped firms** — lowest probability. The plan's original bet. Weak first-customer profile, real competitors already there, no evidence the free-case-study-to-retainer path converts.
5. **Sell to agencies instead of SMBs directly** — worth keeping in reserve. Different buyer (existing budget, existing client relationships), same tool. A bigger pivot, not a Day 30 move.

### Concrete staged plan

**Day 30 — Ship the case study as content, no ask attached.**
Post it. Framed as "I built a tool to measure this, here's what I found." This alone captures most of paths 1 and 2 and is close to free option value — it doesn't require Mighty's cooperation or response.

**Day 31-33 — Send Mighty the results, transparently, with no pitch.**
"I did this because I was curious and you're a great example for content I make about AI/data — here's what I found, no ask." This directly implements the devil's-advocate fix to the opener. Only if they respond warmly: mention, low-pressure, that you're exploring whether this could become a small recurring report, and gauge genuine interest — don't pitch a retainer cold.

**Day 34-40 — Test real demand before building anything else.**
Draft a one-page mockup of a recurring "AI Visibility Report" (using Mighty's real data if they're comfortable with that, otherwise an anonymized/illustrative version). Show it to 5-10 small professional-services businesses — not just accountants; widen the pool (solicitors, financial advisers, other trust-heavy comparison-driven niches) to reduce dependency on any single vertical or Mighty specifically. The question being tested: would anyone actually pay something like £49-99/month for this, recurring? This is a demand test, not a build commitment.

**Day 41+ — Branch on the signal.**
- **If several prospects show real interest** (willing to pay a deposit, or clearly say "yes I'd pay for that"): build the minimal productized version — parameterize the rig to take brand name, competitor list, and niche as config; automate report generation into a simple templated email/PDF; set up a lightweight signup/payment flow. Start small, one paying pilot customer before generalizing further.
- **If there's no real signal** (polite interest but nobody willing to commit, or no replies at all): stop building. Bank the case study as portfolio and content value — that outcome is still a complete, successful project on its own terms — and redirect full attention back to content creation rather than continuing to invest in an unconfirmed business direction.

### Kill criteria

Stop pursuing the productized/consulting path (fall back fully to content + portfolio value) if:
- Zero of the 5-10 demand-test prospects show even mild interest, or
- Nobody is willing to pay anything (even a small deposit) to move forward, or
- Mighty's own response to the transparent, no-ask share is cold or negative — a signal worth taking seriously given how small and networked this niche is.

None of these are failure of the *project* — the content and skills value is banked regardless. They're failure of *this specific monetization path*, which is exactly the distinction the original plan never drew.
