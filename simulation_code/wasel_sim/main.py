from pathlib import Path

import click

from reporting.excel_export import build_excel_workbook
from reporting.report import write_markdown_report
from reporting.tables import build_summary_table, write_tables
from src.models.assumptions import WaselParams
from src.monte_carlo.mc_engine import compute_mc_statistics, run_monte_carlo
from src.sensitivity.tornado import run_one_way_sensitivity
from src.simulation.engine import run_simulation

ROOT = Path(__file__).resolve().parent
BASE_CASE = ROOT / "assumptions" / "base_case.yaml"
SCENARIO_DIR = ROOT / "assumptions" / "scenario_overrides"
OUTPUT_DIR = ROOT / "outputs"


def load_params(scenario: str = "base") -> WaselParams:
    if scenario == "base":
        return WaselParams.from_yaml(BASE_CASE)
    override_path = SCENARIO_DIR / f"{scenario}.yaml"
    if not override_path.exists():
        raise click.ClickException(f"Unknown scenario '{scenario}'")
    return WaselParams.from_yaml(BASE_CASE, override_path=override_path)


@click.group()
def cli():
    """Wasel simulation CLI."""


@cli.command("run")
@click.option("--months", default=60, type=int)
@click.option("--with-charts/--no-charts", default=False)
@click.option("--scenario", default="base", type=str)
def run_cmd(months: int, with_charts: bool, scenario: str):
    params = load_params(scenario)
    sim_df = run_simulation(params, months)
    write_tables(sim_df, OUTPUT_DIR)
    if with_charts:
        from reporting.charts import plot_driver_growth, plot_monthly_cash_curve, plot_supply_demand_balance

        plot_monthly_cash_curve(sim_df, scenario_name=scenario)
        plot_driver_growth(sim_df, scenario_name=scenario)
        plot_supply_demand_balance(sim_df)
    summary = build_summary_table(sim_df)
    click.echo(summary.to_string(index=False))


@cli.command("sensitivity")
@click.option("--with-charts/--no-charts", default=False)
@click.option("--scenario", default="base", type=str)
def sensitivity_cmd(with_charts: bool, scenario: str):
    params = load_params(scenario)
    detail, pivot = run_one_way_sensitivity(params)
    detail.to_csv(OUTPUT_DIR / "sensitivity_detail.csv", index=False)
    pivot.to_csv(OUTPUT_DIR / "sensitivity_tornado.csv", index=False)
    if with_charts:
        from reporting.charts import plot_tornado_chart

        plot_tornado_chart(pivot)
    click.echo(pivot.head(10).to_string(index=False))


@cli.command("monte-carlo")
@click.option("--trials", default=250, type=int)
@click.option("--months", default=60, type=int)
@click.option("--with-charts/--no-charts", default=False)
@click.option("--scenario", default="base", type=str)
def monte_carlo_cmd(trials: int, months: int, with_charts: bool, scenario: str):
    params = load_params(scenario)
    mc_df = run_monte_carlo(params, n_trials=trials, n_months=months)
    mc_df.to_csv(OUTPUT_DIR / "monte_carlo.csv", index=False)
    if with_charts:
        from reporting.charts import plot_monte_carlo_distribution

        plot_monte_carlo_distribution(mc_df)
    stats = compute_mc_statistics(mc_df)
    for key, value in stats.items():
        click.echo(f"{key}: {value}")


@cli.command("report")
@click.option("--scenario", default="base", type=str)
def report_cmd(scenario: str):
    params = load_params(scenario)
    sim_df = run_simulation(params, params.metadata.get("simulation_months", 60))
    path = write_markdown_report(sim_df, OUTPUT_DIR)
    click.echo(f"Wrote report to {path}")


@cli.command("export-excel")
@click.option("--months", default=60, type=int)
@click.option("--trials", default=2000, type=int)
@click.option("--output", default=str(OUTPUT_DIR / "wasel_simulation_results.xlsx"))
@click.option("--scenario", default="base", type=str)
def export_excel_cmd(months: int, trials: int, output: str, scenario: str):
    params = load_params(scenario)
    sim_df = run_simulation(params, months)
    summary_df = build_summary_table(sim_df)
    sensitivity_detail_df, sensitivity_rank_df = run_one_way_sensitivity(params, n_months=months)
    mc_df = run_monte_carlo(params, n_trials=trials, n_months=months)
    mc_stats = compute_mc_statistics(mc_df)
    workbook_path = build_excel_workbook(
        out_path=Path(output),
        assumptions_path=BASE_CASE if scenario == "base" else SCENARIO_DIR / f"{scenario}.yaml",
        summary_df=summary_df,
        sim_df=sim_df,
        sensitivity_detail_df=sensitivity_detail_df,
        sensitivity_rank_df=sensitivity_rank_df,
        mc_df=mc_df,
        mc_stats=mc_stats,
    )
    write_tables(sim_df, OUTPUT_DIR)
    sensitivity_detail_df.to_csv(OUTPUT_DIR / "sensitivity_detail.csv", index=False)
    sensitivity_rank_df.to_csv(OUTPUT_DIR / "sensitivity_tornado.csv", index=False)
    mc_df.to_csv(OUTPUT_DIR / "monte_carlo.csv", index=False)
    click.echo(f"Wrote workbook to {workbook_path}")


if __name__ == "__main__":
    cli()
