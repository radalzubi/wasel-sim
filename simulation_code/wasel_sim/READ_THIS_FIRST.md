# Read This First

Updated: 2026-04-13

This is the current handoff file for anyone reopening or continuing work on the Wasel simulation.

## Current model state

- The model was rebuilt to be decision-useful, not optimistic.
- Rider subscription revenue is removed.
- Competitor response is still active.
- Regulatory/license economics are still explicit.
- The previous collapse loop was redesigned so the model does not fail automatically by construction.

## What changed in the latest revision

- Replaced the hard same-month driver cap with a soft utilization-based recruitment throttle.
- Replaced same-month income-triggered churn punishment with a capped utilization-based churn pressure.
- Relaxed the stacked launch geography and share-cap squeeze to an Amman-first but still conservative ramp.
- Kept competitor pressure but reduced triple-penalization across CAC, organic growth, and share cap.
- Kept annual license as a cash event while removing it from monthly OPEX accrual.
- Raised opening capital to a funded-launch level so survival analysis tests the business, not guaranteed underfunding.

## Latest headline numbers

- Base case: Year 1 NI `-246,972.40 JOD`, Year 2 NI `-50,730.73 JOD`, EoY1 cash `163,027.60 JOD`, breakeven month `24`, EoY5 drivers `5,387.77`
- Bear case: Year 1 NI `-258,096.83 JOD`, Year 2 NI `-124,416.93 JOD`, EoY1 cash `151,903.17 JOD`, breakeven month `41`, EoY5 drivers `2,042.65`
- Bull case: Year 1 NI `-234,148.30 JOD`, Year 2 NI `45,670.21 JOD`, EoY1 cash `175,851.70 JOD`, breakeven month `16`, EoY5 drivers `16,056.44`
- Monte Carlo: P10 / P50 / P90 Year 2 NI `-112,664.44 / -59,843.40 / 1,623.31 JOD`, probability of Year 2 profitability `10.8%`, probability of 18-month survival `71.2%`

## Files to trust first

- `outputs/final_summary.md`
- `outputs/assumption_audit.csv`
- `outputs/base_case.csv`
- `outputs/bear_case.csv`
- `outputs/bull_case.csv`
- `outputs/sensitivity.csv`
- `outputs/monte_carlo.csv`

## Critical modeling notes

- Do not reintroduce rider subscription revenue unless the product decision changes.
- Do not use a universal rider:driver ratio as the controlling mechanic.
- Treat Amman-first launch density as the main operational reality.
- If the model starts collapsing back to near-zero drivers in most paths, inspect churn pressure, launch reach, and recruitment throttling first.
- `avg_trips_per_driver_per_day_assumed` is per-driver ride capacity, and utilization is measured against it. Raising it lowers Year 2 net income and lowering it raises income: fewer, busier drivers pay fewer flat subscriptions, and driver churn does not respond to driver earnings (`min_viable_driver_income_net` is loaded but not used). Read the sensitivity and Monte Carlo results for this variable with that in mind, and keep it out of demand-only scenarios such as `stress_low_demand`.

