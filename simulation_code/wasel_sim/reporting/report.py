from pathlib import Path

from reporting.tables import build_summary_table


def write_markdown_report(sim_df, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = build_summary_table(sim_df).iloc[0].to_dict()
    path = out_dir / "simulation_report.md"
    path.write_text(
        "\n".join(
            [
                "# Wasel Simulation Report",
                "",
                "## Headline Metrics",
                "",
                f"- Year 1 net income: {summary['year1_net_income']:.2f} JOD",
                f"- Year 2 net income: {summary['year2_net_income']:.2f} JOD",
                f"- Cumulative net income: {summary['cumulative_net_income']:.2f} JOD",
                f"- End of Year 1 cash: {summary['end_of_year1_cash']:.2f} JOD",
                f"- Operational break-even month (contribution margin > 0): {int(summary['operational_break_even_month'])}",
                f"- Financial break-even month (monthly NI > 0): {int(summary['financial_break_even_month'])}",
                f"- End active drivers: {summary['end_active_drivers']:.0f}",
                f"- End riders: {summary['end_riders']:.0f}",
            ]
        ),
        encoding="utf-8",
    )
    return path
