# Deep Dive Response — Independent Review of the AEO Plan + Claude Code's Challenge

Companion to [plan-challenge.md](plan-challenge.md), the plan, and the appendix. This is my own pass — I verified the challenge doc's load-bearing claims against live sources rather than taking them on trust, added what I think it missed, and gave a direct answer to the actual question: is this worth your time.

## Bottom line

**Do I agree with Claude Code's document? Yes, on almost everything — and on the one thing I checked hardest (the "uncontested niche" claim), the real picture is** ***worse*** **than it reported, not better.** The niche isn't lightly contested. It's got at least seven active players as of 2026. That doesn't kill the project — it changes what you're actually selling, and I'll get specific about that below.

**Keep building. Change the timeline, the pitch, and the claims you make about it. Don't change the fact that you're building it.**

---

## 1. What I verified, and what changed when I checked

I ran the document's specific, checkable claims against live sources rather than assuming a research agent got them right. Four-agent adversarial reviews are exactly the kind of output that can smuggle in a confident-sounding but wrong number, so this mattered.

**Confirmed accurate:**
- Renownly's 93-firm study and the 28-firm IR35/contractor cut (19% carrying basic AI-visibility signals) — real, live on their site, matches the doc's numbers exactly.
- GetVisus's "almost entirely uncontested" line — real, verbatim, on their `/use-cases/accountant` page.
- Gemini's Search grounding pricing (5,000 free grounded prompts/month on the 3.x family, then $14/1,000) — confirmed across multiple current sources.
- The repo ground-truth (`rig.py`/`parser.py`/`schema.sql` as empty stubs, `questions.csv` fully populated) — matches exactly what I found doing the same check with you a few messages ago.

**Couldn't independently verify:**
- The specific "50 unsolicited AI-visibility audits → 1 positive reply" case. I couldn't find that exact example. What I *did* find: general B2B cold-email benchmarks put positive reply rates at 0.5–2%, so "1 in 50" isn't an outlier or a special penalty for the audit-as-opener genre — it's just what cold outreach looks like, full stop. Slightly different framing than the doc implies (audits aren't uniquely bad; outreach in general is just low-yield), same practical conclusion.

**Materially understated — the niche is more contested than the doc found:**

The doc checked three names and confirmed two (Renownly, GetVisus). I searched independently and found five more active, live products doing essentially the same thing, specifically for UK accountants:

| Player | What they actually offer |
|---|---|
| **TendorAI** | Free AI-visibility scoring, per-city landing pages (has one for "AI Visibility for Accountants in London"), £299/mo tier, explicitly targets ChatGPT/Gemini/Claude/Perplexity/Copilot |
| **MarGen** | Free AI Visibility Audit, "GEO for UK Accountancy Practices" content marketing, same ICAEW/schema/entity-signal playbook |
| **Tenacious Marketing** | Runs a recurring "AI Visibility Index" scoring UK accounting/CFO firms across ChatGPT, Claude, Perplexity |
| **SearchScore** | Audited **1,038 UK accountancy firms** and published a scored report — this is a serious, resourced competitor, not a side project |
| **myaivisibility.co.uk** | Publishes *sample reports specifically for a Leeds IR35/contractor accountant* — this is the closest direct analogue to Mighty of anything I found |

So: not "two of three checked out." **At least seven real, live competitors**, several with published research, free audit tools, and existing pricing. This is not an early, empty field.

**The good news inside that bad news:** I read all seven closely. Every single one sells a *snapshot* — a score, a checklist, an audit, a one-time visibility index. **Not one of them does a controlled experiment.** None mention test/control splits, confidence intervals, or "here's what actually moved vs what the market did anyway." The rigor gap Claude Code's document flagged as "genuinely underused" is real, and it's more real now that I've seen what the competition actually ships. You're not entering an empty room. You're entering a room full of people selling photographs, with the only person offering a video.

That's a stronger, more specific pitch than "uncontested niche" ever was — and it survives the correction. "Uncontested" was always the weakest, most disprovable claim in the plan. Replace it with "the only one measuring change instead of scoring a snapshot," which is both true and better.

---

## 2. Methodology — what I'd add to Claude Code's review

I've been in this build with you the whole way, so I want to flag what I already caught independently before this document existed, plus one thing I think it underweights.

**Already caught, independently, in this conversation:** the `new_company_setup` wipeout (0/7 survived the filter) and `tax_efficiency` thinning to 2/10 — I flagged both when we did the questions.csv sense-check, before this challenge document existed. Good that an independent adversarial pass landed on the same finding from a different angle (topic-count math vs. my direct read of the CSV) — that's real convergent validation, not one analysis just echoing the other.

**What I'd add:** the construct-validity point (raw API vs. consumer app) is the sharpest thing in the whole document and I think it's underweighted relative to the statistics critique. Here's why it matters more than it sounds: the entire commercial pitch is "I measured this, here's the number." If Mighty's own founder opens the ChatGPT app on their phone and gets a different answer than your rig reports — which is *likely*, given different search-triggering thresholds and no personalization in the API path — the natural reaction isn't "interesting methodological nuance," it's "your numbers are wrong." That's not a stats problem you can fix with a bigger N. It's a framing problem: the rig measures *a* real thing, precisely, but you need to be explicit that it's "the API-level answer engines, not necessarily what you'd see in the consumer app" from the first sentence of any client-facing write-up, not as a caveat buried in an appendix.

**One thing I'd push back on slightly:** the document treats the N=5-collapsing-to-thin-cells problem as purely a statistics issue. It's also a *design* opportunity — since you already know from the real `is_product` data which clusters are thin (`tax_efficiency`, and `new_company_setup` is gone entirely), you could deliberately weight remaining budget toward the clusters that can actually support a claim (`fixed_fee_positioning` at 9+ questions, `general_recommendation` at 9) rather than spreading N=5 evenly across clusters that can't. That's a cheap fix that doesn't require more budget or timeline, just re-allocating runs you were going to spend anyway.

---

## 3. Business viability — my independent read

Putting my research and the document's together, here's the honest shape of it:

**Is it a legitimate way to make money?** In principle, yes — real agencies at this price point exist and are apparently trading (TendorAI, Rank4AI, the SaaS case studies). But every verified revenue case study is B2B tech with an existing marketing budget, not a 5-15 person professional-services firm. **Zero verified cases of a small accountancy paying for this and attributing revenue to it.** That's not "this doesn't work," it's "nobody has proven it works for this specific buyer yet" — which cuts both ways: real risk, but also real option value if you're one of the first to actually try it properly.

**Is it a good niche?** Better than "good or bad" — it's a niche where the specific thing you'd be selling (controlled measurement) doesn't exist yet, inside a market that's otherwise now crowded with people selling something adjacent but weaker (snapshots). That's a genuinely useful position. It is not, and was never, an empty field.

**Is it worth your time — vs. more content, vs. something else?**

Here's the actual math on cost, since it keeps getting lost in the strategy discussion: **~£20-35 and, realistically, 6-8 weeks of part-time evenings/weekends** (not the 30 days originally scoped — see below). Against that:

- The skills (Python, REST APIs, a real statistical experiment) are valuable to you *regardless of whether Mighty ever replies*, and directly reinforce the "data careers" content pillar you already have an audience for.
- The case study — positive, negative, or null — is publishable content either way. The plan's own "the null result is the case study" idea is genuinely good, and rare: almost nobody in this space publishes honest negative results, so even "I built this properly and nothing moved" is more differentiated content than 90% of what these seven competitors publish.
- The realistic payoff path isn't "Mighty signs a retainer." It's much more likely to be: a strong piece of content, a credible portfolio artifact, and *maybe* a productized tool later if a demand test says so. Direct retainer sales to a cold-approached small accountancy is the least probable outcome of the five paths Claude Code's document ranks, and I agree with that ranking.

So: **not a competing use of time against content creation — a feeder into it.** The framing "should I do this instead of content, or keep on with content" is close to a false choice at this cost and scope. The actual choice is whether to let a cheap, already-half-built side experiment run in the background while content stays the main channel — which is exactly what the document's synthesis recommends, and I'd endorse it without softening it.

**Should you try a different business instead?** I don't have a concrete alternative in front of me to weigh this against, so I can't give you a real comparison — but I'd note the bar for "abandon a nearly-free, already-70%-researched, skills-building project with guaranteed content value" is high, and "I haven't decided what else I'd do instead" doesn't clear it. If there's a specific other idea you're weighing, bring it and I'll give it the same treatment this got.

---

## 4. Concrete changes to make — synthesized

Agreeing with the document's synthesis, with the corrections above folded in:

1. **Re-scope to 6-8 weeks.** Treat that as the real baseline for a first Python project with unattended infra, not a missed deadline.
2. **Keep "four platforms" as the target, reached in two phases — don't drop it.** On reflection this is different from Brave: Brave was cut because it was redundant with a surface already being measured (Claude's own web_search likely already runs on Brave's index). Gemini isn't redundant with anything already in the rig, and Day 1 already found Mighty at 0% there by hand — real baseline data the automated rig would otherwise never use. The plan and appendix both land on the right sequencing: stabilize the 3-surface rig through Day 5's validation first, then add Gemini as a fast-follow with its own mini validation pass, before the real before/after run. Don't say "four platforms" out loud until it's actually in.
3. **Reframe the eventual result as directional, not proof.** Say "seven usable topics, here's the topic-composition sensitivity" openly rather than letting the confidence-interval math imply more certainty than a 7-unit randomization can support.
4. **Kill "uncontested" entirely — replace with the sharper, truer claim.** "A market with real, active competitors, none of whom run a controlled experiment" is both more honest and a better pitch than "uncontested," which one email or one Google search disproves.
5. **Change the opener.** Transparent, no-ask share ("I built this as a learning project, here's what I found") over "I've been measuring you" — the document's fix here is right, and the base-rate cold-outreach numbers I found reinforce it rather than undercut it.
6. **Content stays primary.** This stays a side experiment that feeds content, not a pivot.

I'd add one more, from the construct-validity point above:

7. **Add one sentence to any client-facing or public write-up, every time**, along the lines of: "measured via each platform's API, which can differ from what you'd see in the consumer app." Cheap insurance against the single fastest way this could look wrong to someone checking your work by hand.
