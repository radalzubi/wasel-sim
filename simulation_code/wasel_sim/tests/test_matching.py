from pathlib import Path

from src.models.assumptions import WaselParams
from src.models.state import DriverCohortState, RiderState
from src.operations.matching import compute_matching


def test_matching_caps_at_demand():
    params = WaselParams.from_yaml(Path("assumptions/base_case.yaml"))
    drivers = DriverCohortState(m2p_mature_drivers=100)
    riders = RiderState(total_riders=10)
    ops = compute_matching(drivers, riders, params)
    assert ops.actual_rides <= ops.demand_rides
    assert ops.actual_rides <= ops.supply_capacity


def test_matching_uses_rider_tolerance_and_market_cap():
    params = WaselParams.from_yaml(Path("assumptions/base_case.yaml"))
    drivers = DriverCohortState(m2p_mature_drivers=10)
    riders = RiderState(total_riders=100)
    ops = compute_matching(drivers, riders, params, market_ride_cap=500)
    assert ops.demand_rides == 500
