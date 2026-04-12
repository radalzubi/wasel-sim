from pathlib import Path

from src.finance.financial_model import compute_financials
from src.models.assumptions import WaselParams
from src.models.state import DriverCohortState, OperationsState, RiderState


def test_financials_produce_revenue():
    params = WaselParams.from_yaml(Path("assumptions/base_case.yaml"))
    drivers = DriverCohortState(m1_drivers=10, m2p_early_drivers=20, m2p_mature_drivers=10)
    riders = RiderState(total_riders=100)
    ops = OperationsState(actual_rides=500, supply_capacity=700, demand_rides=600)
    fin = compute_financials(1, drivers, riders, ops, 100000, 0, params)
    assert fin.total_revenue > 0
    assert fin.cash_balance != 0


def test_month_three_includes_annual_license_payment():
    params = WaselParams.from_yaml(Path("assumptions/base_case.yaml"))
    drivers = DriverCohortState(m1_drivers=10, m2p_early_drivers=20, m2p_mature_drivers=10)
    riders = RiderState(total_riders=100)
    ops = OperationsState(actual_rides=500, supply_capacity=700, demand_rides=600)
    month_two = compute_financials(2, drivers, riders, ops, 100000, 0, params)
    month_three = compute_financials(3, drivers, riders, ops, 100000, 0, params)
    assert month_three.total_opex < month_two.total_opex + 10000
    assert month_three.license_cash_payment == params.annual_ltrc_license
    assert month_three.cash_balance < month_two.cash_balance - 90000
