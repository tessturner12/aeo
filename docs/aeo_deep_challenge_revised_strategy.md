# AEO / AI Search Business Plan — Deep Challenge & Revised Strategy

## Executive conclusion

The underlying opportunity is worth pursuing, but the original plan should be changed materially.

The strongest version of the business is **not an AEO monitoring dashboard**. Monitoring is increasingly becoming a commodity. The stronger proposition is:

> **AI search experimentation: measure what AI recommends, identify the evidence driving those recommendations, make legitimate interventions, and test whether those interventions actually change AI visibility.**

The first project should therefore focus on discovering whether there are **repeatable interventions that measurably change AI recommendations**, rather than trying to prove that AEO generally "works."

---

## 1. Overall judgement

| Question | Current judgement |
|---|---:|
| Is AI visibility a real phenomenon? | 9/10 |
| Will businesses care? | 7/10 |
| Will SMEs pay for monitoring? | 5/10 |
| Will businesses pay for optimisation? | 7/10 |
| Will businesses pay for proven experiments? | 8/10 |
| Is accountancy a good test niche? | 8/10 |
| Is Mighty a good experimental subject? | 9/10 |
| Is Mighty likely to be the ideal long-term customer? | 4/10 |
| Is the current experiment causally rigorous? | 5/10 |
| Can the experiment be fixed? | 9/10 |
| Is the market crowded? | 8/10 — yes |
| Is differentiation still possible? | 8/10 |
| Is monitoring itself a moat? | 2/10 |
| Is experimentation a potential moat? | 8/10 |
| Could this become a good side business? | 8/10 |
| Could this become a serious company? | 6/10 |
| Should the project be built now? | 8/10 — but lean |

---

# 2. What should stay

- Keep the project.
- Keep the initial budget small.
- Keep Mighty as the initial experimental subject.
- Keep the API-based measurement rig.
- Keep raw answer storage.
- Keep repeated runs to measure stochasticity.
- Keep citation extraction.
- Keep competitor tracking.
- Keep baseline → intervention → re-test.
- Keep honest reporting of null results.
- Keep the focus on high-intent commercial questions.
- Keep the ability to configure the system for other businesses.

The downside of the initial experiment is small, while the learning value could be high.

---

# 3. The central change in the business thesis

## Original-style thesis

> "Can I prove AEO works?"

## Better thesis

> **"Which specific interventions can reliably change AI recommendations, for which types of queries, on which AI systems?"**

This is much stronger because:

- AEO monitoring is increasingly commoditised.
- Competitors already offer AI visibility dashboards and monitoring.
- Simply detecting whether a business is mentioned is relatively easy to copy.
- The valuable knowledge is understanding **what changes visibility and under what circumstances**.

The long-term asset could become a proprietary dataset of:

- businesses
- industries
- questions
- AI platforms
- citations
- interventions
- before/after outcomes.

Over time this could support statements such as:

> "We've tested 42 different interventions and these five consistently increase recommendation probability."

That is much harder to copy than a dashboard.

---

# 4. The biggest experimental flaw: sample size

The current experiment has repeated API calls, but repeated calls do not create the same amount of independent evidence as unique questions.

For example:

- 10 questions
- 10 runs
- 3 platforms

creates 300 API observations.

But it is not equivalent to having 300 independent customer intents.

A better conceptual structure is:

**Question × Platform × Run**

Where:

- question = commercial intent
- platform = AI surface
- run = stochastic repetition

Use repeated runs to estimate variance.

Use unique questions to estimate generalisability.

Do not present the total number of API calls as if it were the number of independent observations.

### Recommended reporting

Always report:

- unique questions
- number of runs
- number of platforms
- unique question/platform combinations
- total API observations.

---

# 5. The biggest causal flaw: treatment and control are too different

A treatment such as:

> "fixed-fee accountant"

compared with controls such as:

- general accountant recommendation
- switching accountants
- IR35
- tax
- software
- freelancer/agency

creates topic-level confounding.

If fixed-fee visibility changes while another topic does not, you cannot confidently conclude that the intervention caused the difference.

The topics themselves may behave differently.

## Better design: matched question pairs

Examples:

**Treatment**

> Best fixed-fee accountant for a UK contractor

**Control**

> Best accountant for a UK contractor

---

**Treatment**

> Small fixed-fee accountant for a UK limited company

**Control**

> Small accountant for a UK limited company

This allows the experiment to test the effect of the intervention much more directly.

---

# 6. Better experimental structure

Instead of one treatment concept, eventually test several intervention types.

### T1 — Owned-site positioning

- clearer service positioning
- explicit target customer
- comparison content
- FAQ content
- concrete service information
- technical/structured information

### T2 — Legitimate earned evidence

- professional directories
- legitimate industry profiles
- genuine reviews
- genuine editorial mentions

### T3 — Evidence density

Pages containing concrete:

- pricing
- services
- qualifications
- client types
- locations
- differentiators
- factual claims.

### T4 — Technical/entity consistency

- consistent company information
- entity details
- structured data where appropriate
- internal linking
- clear service pages.

The goal is eventually to learn **which intervention classes actually move AI recommendations**.

---

# 7. Do not overclaim causality

AI search is affected by:

- model changes
- retrieval changes
- search provider changes
- web-index changes
- competitor changes
- query rewriting
- location
- personalisation
- stochastic generation.

Therefore the language should be:

> "We observed a statistically significant increase in visibility in the treatment queries."

rather than:

> "We proved our intervention caused ChatGPT to recommend the company."

Unless the experimental design becomes substantially stronger.

A null result should be interpreted as:

> "These interventions did not materially move these queries during this measurement period."

It should not be interpreted as:

> "AEO does not work."

---

# 8. Change the primary KPI

A raw "mention" is not necessarily a positive outcome.

A business can be mentioned negatively or merely as a secondary comparison.

The primary metric should become something closer to:

## Recommendation share

Measure:

- mentioned
- recommended
- shortlisted
- recommendation position
- positive recommendation
- negative mention
- citation
- primary recommendation.

A useful hierarchy is:

**Mention → Recommendation → Prominence → Citation → Commercial outcome**

The key KPI should be the probability that the business is **positively recommended**, rather than simply named.

---

# 9. Validate the parser

The LLM parser needs a manually labelled gold dataset.

Create approximately 100 answers and manually label:

- Was the business mentioned?
- Was it recommended?
- What position?
- Was the recommendation positive/negative/neutral?
- Which competitors were named?
- Was the business's own website cited?
- Which external domains were cited?

Then compare the automated parser against the manual labels.

Calculate:

- precision
- recall
- false-positive rate.

This prevents the measurement system from accidentally measuring:

> AI answer + parser error.

Special cases should include:

- ambiguous brand names
- unrelated businesses with similar names
- negative recommendations
- comparisons
- citations without explicit brand mentions.

---

# 10. Citation research may be more valuable than visibility scores

The most commercially interesting finding is not necessarily:

> "Mighty was mentioned 3 times."

It may be:

> "The AI ecosystem is learning about Mighty and its competitors from these 130 domains."

The Day 1 data is particularly useful because it showed:

- 672 URLs
- 130 domains
- Mighty domain cited once
- substantial citation activity for competitors
- Reddit, Crunch, Gorilla and ContractorUK appearing repeatedly.

This suggests a much stronger product:

> **AI recommendation → citation → evidence → intervention → outcome**

rather than:

> **AI recommendation → score**

---

# 11. Earned vs owned evidence is a strong thesis

The existing analysis suggests that general recommendation questions may rely heavily on third-party evidence, while specific questions can be more influenced by owned content.

This is commercially interesting.

Instead of simply telling a business:

> "Your homepage needs better AEO."

the product can tell them:

> "AI is learning about your competitors from these external sources, while your business is missing from them."

That is much more actionable.

However, do not overgeneralise this into:

> "You need Reddit."

The correct principle is:

> **legitimate independent evidence matters.**

---

# 12. Do not manipulate Reddit or communities

This should be an explicit rule.

Do not:

- create fake Reddit accounts
- manufacture customer comments
- seed fake recommendations
- pay for covert mentions
- create artificial community experiences.

AI-search optimisation that relies on astroturfing could create serious reputational problems.

The strategy should be:

**genuine evidence + legitimate earned mentions + useful content + accurate business information.**

---

# 13. The competitive landscape is already real

The market is not empty.

Current tools/services already offer combinations of:

- AI visibility tracking
- multi-platform monitoring
- repeated queries
- competitor mapping
- audits
- dashboards
- recommendations
- low-cost monthly monitoring.

Examples include:

- Renownly
- TendorAI
- Visus
- other emerging GEO/AEO platforms.

Therefore, do not compete primarily on:

- number of AI platforms
- number of queries
- dashboards
- monitoring
- AI visibility scores.

Those features are becoming commodity capabilities.

The differentiation needs to be:

> **"We don't just measure whether AI recommends you. We test what actually changes the recommendation."**

---

# 14. The null-result strategy is useful but should not be overvalued

A rigorous null result is valuable research.

It can produce useful content such as:

> "We tested X intervention across Y AI questions and found no material change."

But it does not prove:

> "AEO is ineffective."

It only proves that the tested intervention did not produce a measurable effect under the specific experimental conditions.

The commercial story should therefore be:

> **"We test what works rather than assuming every AEO tactic works."**

---

# 15. Mighty is a good test subject but probably not the ideal customer

Mighty is useful because:

- it is a real business
- it operates in a recommendation-heavy niche
- competitors are identifiable
- customers ask commercially meaningful questions
- AI visibility can be measured.

However, a small accounting firm may not have a large enough marketing budget to justify a high recurring fee.

Therefore:

**Mighty = excellent case study**

does not necessarily mean:

**Mighty = ideal customer profile.**

---

# 16. Target higher-value customers eventually

Better commercial targets may include:

- solicitors
- financial advisers
- mortgage brokers
- recruitment firms
- B2B consultancies
- specialist professional services
- high-value education providers
- estate agencies
- specialist healthcare businesses.

The common characteristic is:

> **One additional customer is worth enough to justify meaningful acquisition spend.**

If a customer is worth £10,000+, paying £500–£1,500/month for a proven acquisition/visibility mechanism becomes much easier to justify.

---

# 17. Agencies may be a better distribution channel

Agencies should be moved from a "reserve" option to an early test segment.

SEO/marketing agencies already understand:

- rankings
- reporting
- retainers
- client acquisition
- client churn
- marketing budgets.

Potential proposition:

> **"An AI visibility experimentation layer for your clients."**

One agency could potentially provide access to many end customers.

This may produce better economics than acquiring dozens of small businesses individually.

---

# 18. Reconsider the initial pricing

Do not assume £500–£1,000/month immediately.

A more realistic product ladder is:

### Free
**AI Visibility Snapshot**

Basic visibility and competitor result.

### £99–£199
**AI Visibility Audit**

Detailed competitive/citation analysis.

### £299–£499
**AI Visibility Experiment**

Baseline → intervention → re-test.

### £500–£1,500/month
**AI Visibility Optimisation**

Ongoing measurement + implementation.

### £2,000+
**AI Search Experimentation**

Larger professional services firms or agencies.

The key is:

> Higher prices require implementation and evidence of commercial value.

---

# 19. Do not sell "AEO reporting"

A business owner may not understand AEO.

A clearer proposition is:

> **"When someone asks ChatGPT for a business like yours, what happens?"**

Then:

> "We test that across the major AI search systems, identify which competitors get recommended instead, trace those recommendations back to the sources influencing them, and test what changes actually improve your visibility."

That is much easier to understand.

---

# 20. The eventual commercial funnel

A strong product ladder could become:

**AI Visibility Snapshot**

↓

**AI Visibility Audit**

↓

**AI Visibility Experiment**

↓

**AI Visibility Optimisation**

↓

**AI Search Experimentation**

This allows a low-risk entry product to lead into higher-value recurring work.

---

# 21. Visibility does not automatically equal revenue

The chain is:

**AI mention**

↓

**AI recommendation**

↓

**user awareness**

↓

**click**

↓

**website visit**

↓

**lead**

↓

**sales call**

↓

**customer**

↓

**revenue**

The current project mostly measures the first few stages.

The eventual business needs to measure the final stages.

However, AI answers may increasingly influence decisions without generating a click, so **recommendation/brand influence itself may remain commercially valuable**.

Do not assume AI search works exactly like conventional SEO.

---

# 22. Do not build the business around AI traffic

A better positioning is:

> **"Increase the probability that AI recommends your business when a customer is making a decision."**

rather than:

> "We'll drive AI traffic to your website."

This distinction matters because AI summaries can satisfy users without a click.

---

# 23. AI platforms are not independent votes

ChatGPT, Claude, Perplexity and Gemini are useful separate surfaces, but they should not be treated as four independent search markets.

They have:

- different retrieval systems
- different models
- different search providers
- different ranking behaviour
- different citation mechanisms.

Report:

> **AI surface coverage**

rather than treating the platforms as four independent votes.

---

# 24. Add Google AI search eventually

The product should eventually cover Google's AI search experiences as well.

Google remains a huge distribution channel.

The eventual system should ideally measure:

- ChatGPT
- Google AI search / AI Overviews / AI Mode
- Gemini
- Perplexity
- Claude

However, Google should be added after the basic experimental methodology is working.

---

# 25. API results need a prominent caveat

API results may differ from consumer products.

Reports should explicitly state:

> "Results reflect API-based measurements conducted on the stated date/time. Consumer applications may produce different answers due to product configuration, retrieval, personalisation, location, memory and ongoing model changes."

This protects credibility.

---

# 26. Query volume is a major unknown

There is no simple equivalent of Google's keyword-volume data for many AI questions.

Therefore:

Do not claim:

> "Mighty has 10% AI market share."

Instead say:

> **"Mighty appeared in X% of our measured high-intent AI recommendation tests."**

That is precise and defensible.

---

# 27. Question generation needs human validation

A strong process is:

**Real customer questions**

↓

**Human question bank**

↓

**AI expansion**

↓

**Human filtering**

↓

**Final experimental set**

Potential sources:

- real customer questions
- sales FAQs
- website analytics
- Google Search Console
- Reddit
- industry forums
- support questions
- interview research.

AI should expand the question universe, not define commercial relevance by itself.

---

# 28. Do not automatically delete informational questions

The current "Product Question" filter is useful, but too absolute.

Use two categories:

### Commercial recommendation questions

Likely to name providers.

### Influence questions

May not name providers but can shape the information ecosystem that later influences recommendations.

Prioritise commercial questions for the experiment, but don't assume informational questions are worthless.

---

# 29. Technical SEO/schema should be treated as a hypothesis

Do not assume:

> "Add schema and AI will recommend you."

Structured data and technical clarity may help machine understanding, but they are not magic recommendation switches.

If a technical intervention produces no measurable change:

**record that finding.**

One of the advantages of the proposed business is that it can test AEO assumptions rather than repeating them.

---

# 30. The biggest long-term risk is platform dependency

The business depends on systems controlled by:

- OpenAI
- Google
- Anthropic
- Perplexity
- other AI/search providers.

They can change:

- models
- retrieval
- ranking
- pricing
- APIs
- access
- product behaviour
- citation systems.

Therefore, don't build the moat around knowing a secret algorithm.

Build it around:

> **continuous measurement and experimentation.**

---

# 31. Do not overbuild the software

For V1:

### Build

- Python rig
- raw answer storage
- citation extraction
- simple parsing
- experiment configuration
- repeat runs
- basic statistical analysis
- report generation.

### Do not build yet

- polished SaaS dashboard
- authentication
- multi-tenancy
- billing
- complex front-end
- elaborate analytics platform
- full automated deployment infrastructure.

The first commercial product can be a **high-quality report**.

---

# 32. Hetzner is unnecessary for V1

Run locally initially.

The workload is small.

Move to a server when:

- a paying customer requires unattended monitoring
- reliability becomes a problem
- multiple clients make local execution inconvenient.

Avoid solving scale before there is demand.

---

# 33. The first commercial experiment should happen earlier

Do not spend two months building a perfect system.

A sensible progression is:

### Week 1
Build the measurement rig.

### Week 2
Run Mighty baseline.

### Week 3
Validate parser + analyse citations.

### Week 4
Produce a polished case study.

### Then
Start selling the experiment.

The overall build may realistically take **6–8 weeks part-time**, but the first useful commercial output should appear much earlier.

---

# 34. The first real business experiment is willingness to pay

Eventually, the most important test is not:

> "Does the system work?"

It is:

> **"Will someone pay for the output?"**

Better questions for potential customers:

> "Would you pay £299 for this report?"

Even better:

> **"I'll run this for £149. Do you want one?"**

Actual payment is much stronger evidence than:

> "That's interesting."

---

# 35. Research/content could be part of the acquisition engine

The project naturally creates content:

- Which businesses does ChatGPT recommend?
- Which domains does AI trust?
- Does Reddit influence recommendations?
- Does schema change AI visibility?
- Do directory listings matter?
- Does changing a service page work?
- Does AI visibility persist after intervention?

This can generate:

**research → content → authority → inbound leads → consulting.**

This is potentially much cheaper than pure outbound sales.

---

# 36. The first case study should not just be "Mighty is invisible"

The more interesting story is:

> **"Mighty has fragmented AI visibility, with thin direct evidence and heavy dependence on external sources."**

That creates a specific optimisation problem.

The case study should show:

1. baseline
2. recommendation rate
3. competitor rate
4. citation sources
5. missing evidence
6. intervention
7. after measurement
8. matched control
9. commercial interpretation.

---

# 37. The ideal long-term architecture

Conceptually:

```text
Brand
Industry
Competitors
Questions
        ↓
AI Query Engine
        ↓
Raw Responses
        ↓
Parser / Classifier
        ↓
Recommendation Metrics
        ↓
Citation Graph
        ↓
Evidence Diagnosis
        ↓
Intervention
        ↓
Re-test
        ↓
Outcome Database
```

The long-term asset is the **outcome database**, not merely the dashboard.

---

# 38. Potential business models

## Model A — Productised audits

Low complexity.

Good for:

- customer acquisition
- case studies
- cash flow.

Risk:

- easily copied
- low recurring revenue.

## Model B — Managed optimisation

Higher value.

Good for:

- recurring revenue
- implementation
- measurable outcomes.

Risk:

- service-heavy.

## Model C — Agency infrastructure

Potentially scalable.

Good for:

- distribution
- multiple end clients
- recurring revenue.

Risk:

- dependency on agencies.

## Model D — Experimentation platform

Highest potential.

Good for:

- proprietary data
- recurring SaaS
- methodology moat.

Risk:

- requires much more evidence before customers will trust it.

---

# 39. Realistic outcomes

### Scenario A — Nobody pays

You spend a small amount and gain:

- Python/API experience
- AI-search expertise
- a case study
- content
- portfolio material.

Still a reasonable outcome.

### Scenario B — 3–5 clients

At £500/month:

**£1,500–£2,500/month**

A plausible side business.

### Scenario C — Productised consultancy

20 clients × £750/month:

**£15,000/month**

Requires:

- repeatable reports
- implementation
- sales pipeline
- client retention.

### Scenario D — Agency model

10 agencies × £1,000/month:

**£10,000 MRR**

Potentially attractive if each agency brings multiple end clients.

### Scenario E — Larger platform

Potentially much larger, but requires:

- proprietary intervention data
- strong distribution
- automation
- commercial attribution
- defensible methodology.

Do not assume this outcome.

---

# 40. The actual moat

The moat is NOT:

- Python
- API access
- A dashboard
- four AI platforms
- query volume
- AEO terminology.

The potential moat is:

## Longitudinal intervention data

Over time:

- 100 businesses
- thousands of questions
- tens of thousands of observations
- hundreds of interventions
- before/after results
- commercial outcomes.

This could reveal which interventions work:

- by industry
- by query type
- by AI platform
- by business maturity
- by evidence type.

That is potentially proprietary intelligence.

---

# 41. Revised business thesis

The strongest version is:

> **Businesses are increasingly being discovered and evaluated through AI systems. Existing tools can measure whether a business is visible, but measurement alone is becoming commoditised. The opportunity is to build a system that identifies the evidence influencing AI recommendations, tests legitimate interventions, and measures whether those interventions reliably change recommendation probability and ultimately commercial outcomes.**

---

# 42. Revised project thesis

Do not ask:

> "Does AEO work?"

Ask:

> **"Can I demonstrate a repeatable causal relationship between a legitimate intervention and increased AI recommendation visibility?"**

If yes:

**you have the foundation of a valuable consultancy/product.**

If no:

**you still have useful research, but should not overstate the commercial opportunity.**

---

# 43. Final recommended strategy

### Phase 1 — Measurement proof

- 20–30 high-intent questions
- 4 AI surfaces
- 5 repetitions
- raw answers
- citations
- competitor analysis
- manual parser validation.

### Phase 2 — Baseline case study

- Mighty
- preserve raw data
- produce report
- identify evidence gaps.

### Phase 3 — Intervention experiment

- matched treatment/control questions
- multiple intervention types
- baseline → intervention → re-test.

### Phase 4 — Commercial validation

Approach:

- accountants
- solicitors
- financial advisers
- agencies.

Offer a paid pilot.

### Phase 5 — Productisation

Only after customers pay:

- automated reports
- monitoring
- dashboard
- multi-client architecture
- cloud infrastructure.

### Phase 6 — Proprietary intelligence

Accumulate:

- interventions
- outcomes
- industries
- platforms
- citation networks.

Turn the database into the moat.

---

# 44. Bottom line

## I would pursue it.

But I would **not pursue it as originally framed**.

The weakest version is:

> "I built an AEO dashboard that tells businesses whether ChatGPT mentions them."

That market is already becoming crowded.

The stronger version is:

> **"I run controlled experiments to find out what makes AI recommend a business."**

And the strongest eventual version is:

> **"We have proprietary evidence from hundreds of AI-search experiments showing which interventions increase recommendation probability and commercial outcomes."**

That is the business I would try to build.

## Priority order

1. **Fix experimental design**
2. **Run the Mighty baseline**
3. **Validate the parser**
4. **Map the citation/evidence ecosystem**
5. **Run a genuine intervention**
6. **Prove before/after movement**
7. **Test willingness to pay**
8. **Sell audits/experiments**
9. **Move into recurring optimisation**
10. **Only then build the SaaS layer**

**Do not spend months building software before completing steps 1–7.**
