from __future__ import annotations

from copy import deepcopy
from dataclasses import replace

import numpy as np
import pandas as pd

from src.models.assumptions import WaselParams
from src.simulation.engine import run_simulation


def sample_parameters(base_params: WaselParams, rng: np.random.Generator) -> WaselParams:
    params = base_params
    params = replace(params, monthly_growth_rate=float(np.clip(rng.beta(2.5, 4.5), 0.05, 0.50)))
    params = replace(params, m0_m1_churn=float(np.clip(rng.beta(2.0, 4.0), 0.10, 0.70)))
    params = replace(params, m1_m2_churn=float(np.clip(rng.beta(2.0, 7.0), 0.05, 0.45)))
    params = replace(params, m2_m6_monthly_churn=float(np.clip(rng.beta(2.0, 28.0), 0.01, 0.20)))
    params = replace(params, m6_plus_monthly_churn=float(np.clip(rng.beta(1.5, 43.0), 0.005, 0.10)))
    params = replace(
        params,
        avg_trips_per_driver_per_day_assumed=float(np.clip(rng.normal(7.5, 1.5), 4.0, 12.0)),
    )
    sampled_blended_fee = float(rng.uniform(27.0, 38.0))
    params = deepcopy(params)
    ratio = sampled_blended_fee / params.blended_fee if params.blended_fee else 1.0
    for tier in params.tiers.values():
        tier.monthly_fee *= ratio
    params.blended_fee = sampled_blended_fee
    rider_cac = float(np.clip(rng.lognormal(1.1, 0.4), 1.5, 8.0))
    params = replace(params, rider_cac_base=rider_cac)
    rider_churn = float(np.clip(rng.beta(3.0, 25.0), 0.03, 0.25))
    params = replace(
        params,
        early_rider_churn_rate=rider_churn,
        steady_rider_churn_rate=rider_churn * 0.5,
    )
    boycott = float(np.clip(rng.triangular(1.0, 1.2, 1.5), 1.0, 1.5))
    params = replace(params, boycott_multiplier_initial=boycott)
    opex_mult = float(np.clip(rng.normal(1.0, 0.15), 0.7, 1.5))
    params = replace(
        params,
        monthly_team_overhead=params.monthly_team_overhead * opex_mult,
        monthly_regulatory=params.monthly_regulatory * opex_mult,
        blended_insurance_per_driver=float(np.clip(rng.triangular(6.0, 8.65, 15.0), 5.0, 25.0)),
    )
    if rng.random() < 0.30:
        params = replace(params, rider_cac_base=params.rider_cac_base * 1.40)
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
        break_even_hits = df[df["m2p_total"] >= 1200]
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
                "survived": bool((df["cash_balance"] > -1_000_000).all()),
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
    stats["prob_survived_18mo"] = float(mc_df["survived"].mean())
    stats["prob_breakeven_by_month18"] = float((mc_df["breakeven_month"] <= 18).mean())
    return stats
