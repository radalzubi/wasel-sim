from copy import deepcopy
from dataclasses import replace

import pandas as pd

from src.models.assumptions import WaselParams
from src.simulation.engine import run_simulation

SENSITIVITY_VARS = {
    "monthly_growth_rate": (0.12, 0.28),
    "m0_m1_churn": (0.18, 0.38),
    "avg_trips_per_driver_per_day_assumed": (6.0, 9.5),
    "m6_plus_monthly_churn": (0.01, 0.05),
    "blended_fee": (28.0, 36.0),
    "m2_m6_monthly_churn": (0.02, 0.06),
    "launch_reachable_share_year1": (0.48, 0.62),
    "boycott_multiplier_initial": (1.0, 1.30),
    "monthly_team_overhead": (6500.0, 9000.0),
    "blended_insurance_per_driver": (9.0, 16.0),
}


def extract_metric(df: pd.DataFrame, metric: str) -> float:
    if metric == "year2_net_income":
        return df[(df["month"] >= 13) & (df["month"] <= 24)]["net_income"].sum()
    if metric == "year1_net_income":
        return df[df["month"] <= 12]["net_income"].sum()
    if metric == "year1_cash_eoy":
        return float(df[df["month"] == 12]["cash_balance"].iloc[0])
    if metric == "breakeven_month":
        hits = df[df["contribution_margin"] > 0]
        return int(hits["month"].iloc[0]) if len(hits) else 999
    raise ValueError(f"Unsupported metric: {metric}")


def _set_param(params: WaselParams, name: str, value: float) -> WaselParams:
    if name == "blended_fee":
        params_copy = deepcopy(params)
        ratio = value / params_copy.blended_fee if params_copy.blended_fee else 1.0
        for tier in params_copy.tiers.values():
            tier.monthly_fee *= ratio
        params_copy.blended_fee = value
        return params_copy
    return replace(params, **{name: value})


def run_one_way_sensitivity(
    base_params: WaselParams,
    var_ranges: dict = SENSITIVITY_VARS,
    metric: str = "year2_net_income",
    n_months: int = 60,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    base_df = run_simulation(base_params, n_months)
    base_value = extract_metric(base_df, metric)
    rows = []
    for var_name, (low, high) in var_ranges.items():
        for case, value in [("low", low), ("high", high)]:
            sim_df = run_simulation(_set_param(base_params, var_name, value), n_months)
            metric_value = extract_metric(sim_df, metric)
            rows.append(
                {
                    "variable": var_name,
                    "case": case,
                    "value": value,
                    "metric": metric_value,
                    "delta": metric_value - base_value,
                }
            )
    detail = pd.DataFrame(rows)
    pivot = detail.pivot(index="variable", columns="case", values="delta").reset_index()
    pivot["swing"] = (pivot["high"] - pivot["low"]).abs()
    pivot = pivot.sort_values("swing", ascending=False)
    return detail, pivot


def run_two_way_sensitivity(
    base_params: WaselParams,
    var_a: str,
    range_a: list[float],
    var_b: str,
    range_b: list[float],
    metric: str = "year2_net_income",
    n_months: int = 60,
) -> pd.DataFrame:
    rows = []
    for a in range_a:
        for b in range_b:
            params = _set_param(_set_param(base_params, var_a, a), var_b, b)
            value = extract_metric(run_simulation(params, n_months), metric)
            rows.append({var_a: a, var_b: b, metric: value})
    return pd.DataFrame(rows).pivot(index=var_a, columns=var_b, values=metric)
