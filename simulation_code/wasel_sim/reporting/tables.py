from pathlib import Path

import pandas as pd


def build_summary_table(sim_df: pd.DataFrame) -> pd.DataFrame:
    operational_hits = sim_df[sim_df["contribution_margin"] > 0]
    operational_break_even_month = int(operational_hits["month"].iloc[0]) if len(operational_hits) else 999
    financial_hits = sim_df[sim_df["net_income"] > 0]
    financial_break_even_month = int(financial_hits["month"].iloc[0]) if len(financial_hits) else 999
    eoy1_month = min(12, int(sim_df["month"].max()))
    return pd.DataFrame(
        [
            {
                "year1_net_income": sim_df[sim_df["month"] <= 12]["net_income"].sum(),
                "year2_net_income": sim_df[(sim_df["month"] >= 13) & (sim_df["month"] <= 24)]["net_income"].sum(),
                "cumulative_net_income": sim_df["net_income"].sum(),
                "end_of_year1_cash": float(sim_df[sim_df["month"] == eoy1_month]["cash_balance"].iloc[0]),
                "operational_break_even_month": operational_break_even_month,
                "financial_break_even_month": financial_break_even_month,
                "end_active_drivers": float(sim_df.iloc[-1]["total_active_drivers"]),
                "end_riders": float(sim_df.iloc[-1]["total_riders"]),
            }
        ]
    )


def write_tables(sim_df: pd.DataFrame, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    build_summary_table(sim_df).to_csv(out_dir / "summary.csv", index=False)
    sim_df.to_csv(out_dir / "monthly_simulation.csv", index=False)
