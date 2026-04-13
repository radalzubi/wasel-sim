from pathlib import Path

from src.models.assumptions import WaselParams
from src.models.state import DriverCohortState, RiderState
from src.operations.matching import compute_matching


def test_matching_caps_at_demand():
    params = WaselParams.from_yaml(Path("assumptions/base_case.yaml"))
    drivers = DriverCohortState(m2p_mature_drivers=100)
    riders = RiderState(total_riders=10)
    ops = compute_matching(drivers, riders, params)
    assert ops.actual_rides <= ops.constrained_demand_rides
    assert ops.actual_rides <= ops.supply_capacity


def test_matching_uses_rider_tolerance_and_market_cap():
    params = WaselParams.from_yaml(Path("assumptions/base_case.yaml"))
    drivers = DriverCohortState(m2p_mature_drivers=10)
    riders = RiderState(total_riders=100)
    ops = compute_matching(drivers, riders, params, market_ride_cap=500)
    assert ops.rider_supported_demand > 500
    assert ops.constrained_demand_rides == 500


def test_matching_churn_pressure_is_soft_and_capped():
    params = WaselParams.from_yaml(Path("assumptions/base_case.yaml"))
    drivers = DriverCohortState(m2p_mature_drivers=100)
    riders = RiderState(total_riders=20)
    ops = compute_matching(drivers, riders, params)
    assert 1.0 <= ops.income_churn_amplifier <= params.churn_pressure_max_multiplier
