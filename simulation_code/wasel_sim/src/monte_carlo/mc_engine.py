from __future__ import annotations

from copy import deepcopy
from dataclasses import replace

import numpy as np
import pandas as pd

from src.models.assumptions import WaselParams
from src.simulation.engine import run_simulation


def sample_parameters(base_params: WaselParams, rng: np.random.Generator) -> WaselParams:
    params = base_params
    params = replace(
        params,
        monthly_growth_rate=float(np.clip(rng.normal(base_params.monthly_growth_rate, 0.035), 0.08, 0.30)),
    )
    params = replace(
        params,
        m0_m1_churn=float(np.clip(rng.normal(base_params.m0_m1_churn, 0.05), 0.16, 0.40)),
        m1_m2_churn=float(np.clip(rng.normal(base_params.m1_m2_churn, 0.03), 0.06, 0.18)),
        m2_m6_monthly_churn=float(
            np.clip(rng.normal(base_params.m2_m6_monthly_churn, 0.010), 0.02, 0.07)
        ),
        m6_plus_monthly_churn=float(
            np.clip(rng.normal(base_params.m6_plus_monthly_churn, 0.006), 0.01, 0.05)
        ),
    )
    params = replace(
        params,
        avg_trips_per_driver_per_day_assumed=float(
            np.clip(rng.normal(base_params.avg_trips_per_driver_per_day_assumed, 0.55), 6.0, 9.5)
        ),
    )
    sampled_blended_fee = float(np.clip(rng.normal(base_params.blended_fee, 2.0), 28.0, 36.0))
    params = deepcopy(params)
    ratio = sampled_blended_fee / params.blended_fee if params.blended_fee else 1.0
    for tier in params.tiers.values():
        tier.monthly_fee *= ratio
    params.blended_fee = sampled_blended_fee
    rider_cac = float(np.clip(rng.normal(base_params.rider_cac_base, 0.7), 3.0, 6.5))
    params = replace(params, rider_cac_base=rider_cac)
    rider_churn = float(
        np.clip(rng.normal(base_params.early_rider_churn_rate, 0.025), 0.06, 0.18)
    )
    params = replace(
        params,
        early_rider_churn_rate=rider_churn,
        steady_rider_churn_rate=rider_churn * 0.60,
    )
    boycott = float(np.clip(rng.normal(base_params.boycott_multiplier_initial, 0.12), 1.0, 1.35))
    params = replace(params, boycott_multiplier_initial=boycott)
    opex_mult = float(np.clip(rng.normal(1.0, 0.08), 0.85, 1.20))
    params = replace(
        params,
        monthly_team_overhead=params.monthly_team_overhead * opex_mult,
        monthly_regulatory=params.monthly_regulatory * opex_mult,
        blended_insurance_per_driver=float(np.clip(rng.normal(base_params.blended_insurance_per_driver, 1.5), 9.0, 16.0)),
    )
    if rng.random() < 0.20:
        params = replace(
            params,
            rider_cac_base=params.rider_cac_base * 1.15,
            competition_cac_weight=params.competition_cac_weight * 1.10,
        )
    if rng.random() < 0.15:
        params = replace(
            params,
            launch_reachable_share_year1=max(0.45, params.launch_reachable_share_year1 - 0.05),
            launch_reachable_share_year3=max(0.65, params.launch_reachable_share_year3 - 0.04),
            launch_reachable_share_year5=max(0.80, params.launch_reachable_share_year5 - 0.03),
        )
    return params


def run_monte_carlo(
    base_params: WaselParams,
    n_trials: int = 1000,
    n_months: int = 60,
    seed: int = 42,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for trial in range(n_trials):
        params = sample_parameters(base_params, rng)
        df = run_simulation(params, n_months)
        eoy1_month = min(12, n_months)
        eoy2_month = min(24, n_months)
        year1 = df[df["month"] <= 12]["net_income"].sum()
        year2 = df[(df["month"] >= 13) & (df["month"] <= 24)]["net_income"].sum()
        year3 = df[(df["month"] >= 25) & (df["month"] <= 36)]["net_income"].sum()
        year5 = df["net_income"].sum()
        break_even_hits = df[df["contribution_margin"] > 0]
        break_even_month = int(break_even_hits["month"].iloc[0]) if len(break_even_hits) else 999
        rows.append(
            {
                "trial": trial,
                "monthly_growth_rate": params.monthly_growth_rate,
                "m0_m1_churn": params.m0_m1_churn,
                "m6_plus_monthly_churn": params.m6_plus_monthly_churn,
                "blended_fee": params.blended_fee,
                "year1_net_income": year1,
                "year2_net_income": year2,
                "year3_net_income": year3,
                "year5_cum_net_income": year5,
                "eoy1_cash": float(df[df["month"] == eoy1_month]["cash_balance"].iloc[0]),
                "eoy2_cash": float(df[df["month"] == eoy2_month]["cash_balance"].iloc[0]),
                "breakeven_month": break_even_month,
                "survived_18mo": bool((df[df["month"] <= 18]["cash_balance"] > 0).all()),
            }
        )
    return pd.DataFrame(rows)


def compute_mc_statistics(mc_df: pd.DataFrame) -> dict:
    stats: dict = {}
    for col in [
        "year1_net_income",
        "year2_net_income",
        "year3_net_income",
        "year5_cum_net_income",
        "eoy1_cash",
        "breakeven_month",
    ]:
        clean = mc_df[col].dropna()
        stats[col] = {
            "p10": float(clean.quantile(0.10)),
            "p50": float(clean.quantile(0.50)),
            "p90": float(clean.quantile(0.90)),
            "mean": float(clean.mean()),
            "std": float(clean.std()),
        }
    stats["prob_year2_profitable"] = float((mc_df["year2_net_income"] > 0).mean())
    stats["prob_survived_18mo"] = float(mc_df["survived_18mo"].mean())
    stats["prob_breakeven_by_month18"] = float((mc_df["breakeven_month"] <= 18).mean())
    return stats
