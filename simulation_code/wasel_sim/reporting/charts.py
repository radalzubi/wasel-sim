import os
from pathlib import Path

import numpy as np
import pandas as pd

MPL_DIR = Path(".mplconfig").resolve()
MPL_DIR.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPL_DIR))

import matplotlib.pyplot as plt

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

try:
    import plotly.graph_objects as go  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    go = None


def plot_monthly_cash_curve(sim_df: pd.DataFrame, scenario_name: str = "base"):
    if go is not None:
        fig = go.Figure()
        fig.add_scatter(x=sim_df["month"], y=sim_df["cash_balance"], mode="lines+markers", name="cash")
        fig.add_hline(y=0, line_dash="dash")
        fig.update_layout(title=f"Cash curve - {scenario_name}")
        fig.write_html(OUTPUT_DIR / f"cash_curve_{scenario_name}.html")
        return fig
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(sim_df["month"], sim_df["cash_balance"])
    ax.axhline(0, linestyle="--", color="red")
    ax.set_title(f"Cash curve - {scenario_name}")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / f"cash_curve_{scenario_name}.png", dpi=150)
    return fig


def plot_driver_growth(sim_df: pd.DataFrame, scenario_name: str = "base"):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.stackplot(
        sim_df["month"],
        sim_df["m0_drivers"],
        sim_df["m1_drivers"],
        sim_df["m2p_early_drivers"],
        sim_df["m2p_mature_drivers"],
        labels=["M0", "M1", "M2+ Early", "M2+ Mature"],
    )
    ax.axhline(1200, linestyle=":", color="green")
    ax.set_title(f"Driver growth - {scenario_name}")
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / f"driver_growth_{scenario_name}.png", dpi=150)
    return fig


def plot_supply_demand_balance(sim_df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(sim_df["month"], sim_df["supply_capacity"], label="Supply capacity")
    ax.plot(sim_df["month"], sim_df["rider_supported_demand"], label="Rider-supported demand")
    ax.plot(sim_df["month"], sim_df["constrained_demand_rides"], label="Constrained demand")
    ax.plot(sim_df["month"], sim_df["market_ride_cap"], label="Market cap")
    ax.set_title("Supply vs demand balance")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "supply_demand_balance.png", dpi=150)
    return fig


def plot_tornado_chart(tornado_df: pd.DataFrame, metric_name: str = "Year 2 Net Income"):
    top = tornado_df.head(10)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(top["variable"], top["high"], color="#4CAF50", alpha=0.7, label="high")
    ax.barh(top["variable"], top["low"], color="#F44336", alpha=0.7, label="low")
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_title(f"Tornado chart - {metric_name}")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "tornado_chart.png", dpi=150)
    return fig


def plot_monte_carlo_distribution(mc_df: pd.DataFrame, metric: str = "year2_net_income"):
    clean = mc_df[metric].dropna()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    ax1.hist(clean, bins=40, color="steelblue", edgecolor="white", alpha=0.85)
    ax1.axvline(0, linestyle="--", color="red")
    ax1.set_title(f"Distribution - {metric}")
    sorted_vals = np.sort(clean)
    cdf = np.arange(1, len(sorted_vals) + 1) / len(sorted_vals)
    ax2.plot(sorted_vals, cdf)
    ax2.set_title(f"CDF - {metric}")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / f"mc_{metric}.png", dpi=150)
    return fig
