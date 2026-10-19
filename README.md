# Wasel Simulation

Wasel is a ride-hailing startup for Jordan and the wider MENA region. This repository holds the Python simulation used to stress-test Wasel's launch economics, alongside the planning materials (brand, financials, execution plan, rider demand playbook, pitch decks) that the model supports. The simulation is a 60-month, cohort-based model of driver supply, rider demand, competitor pressure, regulatory costs, and cash, with scenario runs, one-way sensitivity analysis, and a Monte Carlo engine. Its inputs are planning assumptions, not observed operating data, so its outputs show what follows from those assumptions rather than forecasts.

## What the simulation models

The model advances month by month for 60 months (`src/simulation/engine.py`). Each month it updates drivers, riders, and the market, matches supply to demand, and computes the financials.

- **Business model.** Drivers pay a flat monthly subscription instead of a per-ride commission. Month-0 drivers pay nothing, month-1 drivers pay 10 JOD, and established drivers pay by tier: Starter 20 JOD (45% of drivers), Core 35 JOD (35%), Pro 55 JOD (20%), a blended 32.25 JOD. Rider subscription revenue is switched off (all riders are on the free tier).
- **Driver cohorts.** Drivers move through M0, M1, M2+ early, and M2+ mature stages with different churn rates (25% M0 to M1, 12% M1 to M2, 4% per month in months 2-6, then 2% per month). 500 drivers are seeded in month 1; after that, new recruits each month equal 18% of the active base, throttled when driver utilization falls below 82%.
- **Riders.** Starts from a 12,000-rider waitlist, grows through a monthly marketing schedule (12,000 JOD in months 1-3, tapering to 5,000 JOD) at a 4.80 JOD base acquisition cost plus 3% organic growth, with 12% early and 6% steady monthly churn.
- **Market and matching.** Rides served each month are the minimum of driver capacity and demand. Demand is limited by rider-supported demand and a market ceiling built from 1.5M base monthly rides in Jordan, 5.2% annual growth, seasonality factors, an Amman-first "launch reachable" share (55% in year 1 rising to 90% in year 5), and a market share ceiling (11% rising to 23%) scaled by a driver-liquidity index. Utilization feeds back into driver churn and recruitment.
- **Competition.** Uber, Careem, Jeeny, Petra Ride, and Taxi F are configured in `base_case.yaml`. The model uses each one's initial market share, price-war probability, and maximum rider discount to compute a share-weighted discount pressure, which raises rider acquisition cost, slows organic growth, and lowers the share ceiling, fading out linearly over 24 months.
- **Costs, regulation, and cash.** Team overhead, legal, support, cloud, maps, SMS, insurance, driver and rider marketing, and a 100,000 JOD annual license paid as a cash event in month 3 and every 12 months after. Opening cash is 650,000 JOD seed capital minus 140,000 JOD of pre-launch capex.
- **Analysis layers.** Named scenarios (`bear`, `bull`, and `stress_low_demand` are override files merged onto the base case), a one-way sensitivity run over 10 variables on Year 2 net income, and a Monte Carlo engine that samples growth, churn, trips per driver, pricing, acquisition cost, and operating cost, with occasional acquisition-cost and market-reach shocks.

Assumptions live in YAML under `simulation_code/wasel_sim/assumptions/` and are range-checked on load. Amounts are in Jordanian dinar (JOD).

## Results from the committed assumptions

Re-running the commands below reproduces these figures (JOD). They are outputs of the assumptions, not predictions.

| Scenario | Year 1 net income | Year 2 net income | Cash at end of Year 1 | First month with positive net income | Active drivers at month 60 |
|---|---|---|---|---|---|
| Base | -246,972 | -50,731 | 163,028 | 24 | 5,388 |
| Bear | -258,097 | -124,417 | 151,903 | 41 | 2,043 |
| Bull | -234,148 | 45,670 | 175,852 | 16 | 16,056 |

Monte Carlo (500 trials, seed 42, base case): Year 2 net income P10 / P50 / P90 of -112,664 / -59,843 / 1,623 JOD, a 10.8% chance of a profitable Year 2, and a 71.2% chance that cash stays positive through month 18. In the one-way sensitivity run, monthly driver growth rate, blended subscription fee, and insurance cost per driver move Year 2 net income the most.

## Tech stack

- Python 3.12 or newer (checked on 3.14)
- pandas and NumPy for the simulation and tables
- PyYAML for assumption files, with scenario overrides deep-merged onto the base case
- Click for the command-line interface
- Matplotlib for charts (Plotly is used for the cash curve only if installed)
- openpyxl for Excel export
- pytest for tests

Pinned versions are in `simulation_code/wasel_sim/requirements.txt`. Plotly is listed there as an optional, commented-out extra.

## Repository layout

| Path | Contents |
|---|---|
| `simulation_code/wasel_sim/` | The simulation package (see below) |
| `Brand strategy/` | Planning materials: brand strategy documents (.docx, .pdf) |
| `Financials/` | Planning materials: revised financial model and projection feedback (.xlsx), TAM analysis (.docx, .pdf) |
| `Master Plan/` | Planning materials: execution timeline (.docx, .pdf) and Gantt chart with budget (.xlsx) |
| `Rider Demand Playbook/` | Planning materials: rider demand playbook (.pdf) |
| `Pipeline-TImeline/` | Planning materials: pipeline fixes (.docx) |
| `Husam Khoury/` | Planning materials: project brief versions, pitch deck, and a Python script that builds the brief PDF |
| Repo root files | Pitch deck drafts (.pptx), rider acquisition strategy and master plan documents (.docx), Gantt and budget (.xlsx) |

Inside `simulation_code/wasel_sim/`:

| Path | Contents |
|---|---|
| `main.py` | Command-line entry point |
| `requirements.txt` | Pinned runtime and test dependencies |
| `assumptions/` | `base_case.yaml`, `scenario_overrides/` (bear, bull, stress_low_demand), and `competitor_profiles.yaml` (qualitative notes, not read by the code) |
| `src/` | Model code: `drivers`, `riders`, `market`, `operations` (matching), `competitors`, `finance`, `simulation`, `sensitivity`, `monte_carlo`, `models` |
| `reporting/` | Summary tables, Markdown report, charts, Excel export |
| `tests/` | Unit tests (9 tests) |
| `outputs/` | Committed results from earlier runs (see below) |
| `notebooks/` | Placeholder exploration notebook |

## Running the simulation

Run everything from `simulation_code/wasel_sim/`, because the chart code and tests use relative paths.

```bash
cd simulation_code/wasel_sim
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python3 main.py run                          # 60-month base case, prints a summary table
python3 main.py run --scenario bull          # or: bear, stress_low_demand
python3 main.py run --with-charts            # also writes PNG charts to outputs/
python3 main.py sensitivity                  # one-way sensitivity on Year 2 net income
python3 main.py monte-carlo --trials 500     # Monte Carlo statistics
python3 main.py report                       # writes outputs/simulation_report.md
python3 main.py export-excel --trials 500    # Excel workbook of all results
python3 -m pytest
```

Each command accepts `--scenario`. `run`, `monte-carlo`, and `export-excel` accept `--months`, and `sensitivity`, `monte-carlo`, and `run` accept `--with-charts`. Running commands overwrites files in `outputs/`.

## Outputs in the repo

Under `simulation_code/wasel_sim/outputs/`:

- `final_summary.md`: scenario and Monte Carlo headline numbers (matches the table above)
- `base_case.csv`, `bear_case.csv`, `bull_case.csv`: monthly results per scenario
- `sensitivity.csv` and `monte_carlo.csv`: sensitivity ranking and 500 Monte Carlo trials
- `assumption_audit.csv`: log of assumption changes and the reasoning for each
- `*.xlsx`: Excel workbooks (Summary, Assumptions, Monthly Simulation, sensitivity and Monte Carlo sheets) from several model revisions
- `simulation_report.md`: the committed copy is from an earlier model revision, so use `final_summary.md` or re-run `main.py report` for current figures

Charts are not committed. `--with-charts` generates `cash_curve_base.png` (an HTML file instead if Plotly is installed), `driver_growth_base.png`, `supply_demand_balance.png`, `tornado_chart.png`, and `mc_year2_net_income.png`.

For model status and design notes, see `simulation_code/wasel_sim/READ_THIS_FIRST.md`.
