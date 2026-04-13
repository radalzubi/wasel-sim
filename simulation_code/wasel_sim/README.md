# Wasel Market Simulation

Production-grade simulation package for Wasel's Jordan launch economics.

## Read first

- Start with [`READ_THIS_FIRST.md`](./READ_THIS_FIRST.md) for the latest model status, current outputs, and handoff notes.

## What this includes

- Deterministic 60-month simulation
- Driver cohort onboarding and churn model
- Rider acquisition and churn model
- Supply-demand matching validation
- Financial model with cash tracking
- One-way and two-way sensitivity analysis
- Monte Carlo engine
- Markdown reporting and chart generation

## Quick start

```bash
cd /Users/radalzubi/Desktop/wg1/simulation_code/wasel_sim
python3 main.py run
python3 main.py sensitivity
python3 main.py monte-carlo --trials 250
python3 main.py report
pytest
```

## Notes

- `pydantic`, `plotly`, and `scipy` are not installed in this environment.
- This implementation uses compatible stdlib fallbacks so the project runs locally now instead of requiring network installs first.
