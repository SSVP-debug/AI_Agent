# Sample Output — "AI-powered personal finance coaching for gig workers"

> **Note on how this file was produced:** this is a hand-authored example
> showing the exact structure and level of detail the pipeline produces,
> in the same format the `writer` agent outputs. It was not captured from
> a live API call, because generating this rebuild's documentation didn't
> have network access to the Gemini/Tavily APIs. Before you make this repo
> public, run `python main.py` once with your own API keys on a real topic
> and replace this file with the actual output — that's a five-minute step
> and it's worth doing so this file is a genuine capture, not a mockup.

**Input topic:** `AI-powered personal finance coaching for gig workers`

---

## Final Business Blueprint

### 1. Overview
A mobile-first app that ingests gig-work income data (Uber, DoorDash,
Upwork via Plaid-style bank feeds) and gives freelancers real-time
budgeting guidance suited to irregular income — smoothing weekly cash
flow, flagging under-saved tax liability, and nudging emergency-fund
contributions during high-income weeks.

### 2. MVP Scope
- Bank/gig-platform account linking (Plaid)
- Income variability dashboard (weekly/monthly smoothing view)
- Estimated quarterly tax set-aside calculator
- Simple rule-based savings nudges (not a full robo-advisor at MVP stage)

### 3. Competitors (from research agent)
- Found via live search: Hurdlr, QuickBooks Self-Employed, Keeper Tax —
  all cover tax estimation for gig workers but none combine it with
  cash-flow smoothing guidance in one view. That's the differentiation
  angle this idea has room to take.

### 4. Go-to-Market
- Land through gig-worker Facebook/Reddit communities and driver forums
  before paid acquisition — this audience is skeptical of fintech ads
  but responsive to peer recommendations.
- Freemium: free tax estimator, paid tier ($6-9/mo) for smoothing +
  savings automation.

### 5. Financial Model (directional, not audited)
- Assumption: 3% conversion from free to paid tier, $50 CAC via
  community-first acquisition, $7/mo ARPU on paid tier.
- Breakeven on CAC at ~7 months per paid user at these assumptions —
  sensitive to the conversion rate assumption, which is unvalidated
  until real usage data exists.

---

## Pitch Deck Outline (10 slides)

1. Title — problem statement in one line
2. The problem: income volatility + tax under-saving for gig workers
3. Why now: gig workforce growth, still-underserved by existing tools
4. Product: cash-flow smoothing + tax set-aside, one dashboard
5. How it works (simple flow diagram)
6. Competitive landscape (Hurdlr, QuickBooks SE, Keeper — positioning)
7. Business model: freemium, $7/mo paid tier
8. Go-to-market: community-first, then paid acquisition
9. Financial model summary (assumptions stated explicitly)
10. Ask: what's needed to reach 1,000 paid users
