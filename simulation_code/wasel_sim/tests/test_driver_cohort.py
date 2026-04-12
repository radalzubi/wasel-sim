from pathlib import Path

from src.models.assumptions import WaselParams
from src.models.state import DriverCohortState
from src.drivers.cohort_model import update_driver_cohorts


def test_driver_cohort_starts_with_seed():
    params = WaselParams.from_yaml(Path("assumptions/base_case.yaml"))
    state = update_driver_cohorts(DriverCohortState(), params, 1)
    assert state.m0_drivers > 0
    assert state.total_active == state.m0_drivers
