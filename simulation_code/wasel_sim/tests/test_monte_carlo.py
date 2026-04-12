from pathlib import Path

from src.models.assumptions import WaselParams
from src.monte_carlo.mc_engine import run_monte_carlo


def test_monte_carlo_runs_small_sample():
    params = WaselParams.from_yaml(Path("assumptions/base_case.yaml"))
    df = run_monte_carlo(params, n_trials=5, n_months=6, seed=1)
    assert len(df) == 5
    assert "year1_net_income" in df.columns
