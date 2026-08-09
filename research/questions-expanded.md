# Questions — Expanded

Day 2, step 2: expanded phrasings, before clustering.

Reconstructed from the actual Day 2 conversation and cross-checked against
the final `questions.csv` for exact wording. Organised by the seed/cluster
each batch was expanded from — this is genuinely what Step 2 produced,
before Step 3 trimmed and Step 4 tiered it into the final set.

---

## Seed: general recommendation

- cheapest monthly online accountants uk
- what's the cheapest accountant i can get for a ltd company
- anyone know a cheap online accountant for a one person ltd co
- is there a cheap but decent accountant for freelancers
- good value accountants for small uk companies
- affordable accountant for a small uk limited company
- best london accountants for contractors
- cheapest london accountants for freelancers
- does it matter if my accountant isn't based in london
- accountant recommendations london freelancer limited company

## Seed: IR35 compliance

- ir35 accountants
- ir35 compliant accountant for contractors
- accountant for it contractor ir35 inside vs outside
- best accountant for someone operating outside ir35
- do i need a specialist ir35 accountant or will any ltd company accountant do
- anyone recommend an accountant who actually knows ir35 inside out
- ir35 accountant recommendations 2026
- need an accountant who won't get my ir35 status wrong

## Seed: fixed fee / small firm positioning — Mighty's natural home

First pass:
- is pay monthly or one off accountant better
- fixed monthly fee vs one off accountant fee which is better value
- sick of surprise invoices from my accountant, is there a fixed fee option
- fixed fee accountant no hidden costs contractor
- accountant that does one flat monthly fee, everything included
- looking for predictable accountant costs, hate surprise bills
- small firm fixed fee accountant, not a big impersonal agency
- accountant that actually understands one person consultancies, fixed monthly cost
- fixed fee accountant for a one person ltd co, no add on charges
- monthly accountant subscription that includes bookkeeping and tax return

A second pass was added later, since this is Mighty's single most important
cluster and it was worth more coverage:
- accountant with a simple monthly plan for a small limited company
- accountant that offers a yearly plan instead of hourly billing
- looking for an accountant with an annual plan, not per-task charges
- accountant with one straightforward monthly plan, no big firm
- small accountancy firm with a clear annual plan for contractors

## Seed: switching accountants

*Not from personal experience — I've never switched accountants. Kept
because the plan flags it as a likely-real cluster, but worth being
honest that this one is guessed, not lived, unlike the others.*

- switching accountants mid tax year limited company
- how do i switch accountants without messing up my tax return
- sick of my accountant never replying to emails, anyone recommend someone actually good for a one person ltd co
- is it a hassle to change accountants partway through the year
- my current accountant keeps making mistakes, how do i find a better one
- process for switching limited company accountants uk
- good accountants for contractors switching from a big impersonal firm
- how much notice do i need to give my accountant before switching
- can i switch accountants without losing my financial history
- looking to leave my current accountant, need someone more responsive
- best accountants for people fed up with slow or unresponsive current provider
- switching from a big contractor accountancy firm to a smaller one
- what to check before switching accountants for a limited company
- accountant switch mid year, will my corporation tax be affected
- recommend an accountant, leaving my current one after a bad experience

## Seed: tax efficiency (dividends / salary / DLA)

- accountant that can advise on dividends vs salary and how much i can safely take out
- accountant to help figure out retained profit rules for dividends
- best accountant for advice on paying myself dividends vs salary
- need an accountant who explains director's loan account rules clearly
- who can advise on the right mix of salary and dividends for a one person company
- who's a good accountant for figuring out how much dividend tax i'll owe at year end

## Seed: VAT — *not one of the plan's original 8 clusters*

This came from a real seed in my own brain dump (VAT registration worth
it?), and it took up more of the actual brain dump than any other single
topic. **Decision made at Step 3:** fold into `tax_efficiency` rather than
promote to a 9th cluster — reflected in the final schema as
`tax_efficiency` covering "dividends/salary + VAT."

- accountant who can advise whether vat registration is worth it for a small limited company
- is vat registration worth it financially as a small contractor
- accountant to explain flat rate vs standard vat for a consultancy
- do i need an accountant to register for vat or can i do it myself
- best accountant for vat advice, small limited company
- accountant that handles vat returns for contractors
- flat rate vat accountant recommendations uk
- accountant who can tell me if i should voluntarily register for vat
- need an accountant to help decide vat scheme for a one person company
- accountant that files vat returns, how much extra does that cost
- small business accountant who explains vat registration threshold clearly
- accountant to help work out if vat registration actually saves me money

*(After folding + trimming, the tax_efficiency + VAT set that made it into
`questions.csv` was rewritten with explicit "uk"/"limited company"
anchoring — e.g. "uk accountant that can advise on dividends vs salary for
my limited company and how much i can safely take out" — for the same
reason `freelancer_agency` needed it: this cluster doesn't naturally
contain a UK/contractor anchor word the way IR35 or "contractor" phrasings
do.)*

## Seed: software compatibility

- accountant that works with pandle for a small limited company
- accountant familiar with pandle bookkeeping software
- which accounting software do most contractor accountants prefer, xero or freeagent
- accountant that supports freeagent for limited company contractors
- does my accountant need me to use a specific software like xero
- best accounting software an accountant will actually work with for a small ltd co

## Seed: new company setup

- do i need an accountant for a limited company
- can i run a limited company without an accountant
- is it possible to not have an accountant as a first time contractor
- do i actually need an accountant for a short 3 month contract
- first time setting up a ltd company, do i need an accountant from day one
- new contractor here, is an accountant essential or can i manage myself
- first time director, should i get an accountant straight away

## Seed: freelancer / agency

*Authored, not researched from personal experience — I'm a solo
contractor, not an agency operator. Flagged explicitly at the time as a
cluster to be honest about in any documentation or pitching.*

First-pass phrasings lacked a UK/limited-company anchor and pulled entirely
US-based CPA firms in a spot-check — every row was rewritten to add "uk"
and "limited company" explicitly, since this cluster (unlike IR35 or
"contractor" phrasings) doesn't naturally contain an anchor word. Final set:

- accountant for a small uk digital agency, not just solo contractors, limited company
- best uk accountant for a two or three person freelance agency, limited company
- uk accountant that handles payroll for a small limited company agency with a couple of employees
- looking for a uk accountant who works with small creative agencies, limited company, not just sole traders
- uk accountant for a growing freelance collective limited company, more than one director

---

## Gaps and decisions made at Step 3 (for reference)

1. **VAT folded into `tax_efficiency`** rather than becoming a 9th cluster,
   despite being the single biggest topic in the raw brain dump — see note
   above.
2. **`switching_accountants` has no seed from lived experience** — kept as
   a plausible cluster per the plan, but honestly flagged as guessed.
3. **`freelancer_agency` is authored, not researched** — flagged explicitly,
   carried through to the project brief.
