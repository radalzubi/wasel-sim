from pathlib import Path

from src.models.assumptions import WaselParams


def test_scenario_override_changes_base_case():
    base = WaselParams.from_yaml(Path("assumptions/base_case.yaml"))
    bear = WaselParams.from_yaml(
        Path("assumptions/base_case.yaml"),
        override_path=Path("assumptions/scenario_overrides/bear.yaml"),
    )
    assert bear.monthly_growth_rate != base.monthly_growth_rate
    assert bear.initial_waitlist_riders != base.initial_waitlist_riders
