from pathlib import Path

from src.models.assumptions import WaselParams
from src.simulation.engine import run_simulation

BASE_CASE = Path("assumptions/base_case.yaml")
SCENARIO_DIR = Path("assumptions/scenario_overrides")


def test_scenario_override_changes_base_case():
    base = WaselParams.from_yaml(BASE_CASE)
    bear = WaselParams.from_yaml(
        BASE_CASE,
        override_path=SCENARIO_DIR / "bear.yaml",
    )
    assert bear.monthly_growth_rate != base.monthly_growth_rate
    assert bear.initial_waitlist_riders != base.initial_waitlist_riders


def test_low_demand_scenario_shrinks_both_sides_of_the_network():
    # Weaker rider demand should leave Wasel with fewer riders and fewer drivers than the
    # base case, not a larger driver network.
    base = run_simulation(WaselParams.from_yaml(BASE_CASE))
    stress = run_simulation(
        WaselParams.from_yaml(BASE_CASE, override_path=SCENARIO_DIR / "stress_low_demand.yaml")
    )
    for month_index in (23, 59):
        assert stress.loc[month_index, "total_riders"] < base.loc[month_index, "total_riders"]
        assert (
            stress.loc[month_index, "total_active_drivers"]
            < base.loc[month_index, "total_active_drivers"]
        )
    assert stress["cumulative_net_income"].iloc[-1] < base["cumulative_net_income"].iloc[-1]
