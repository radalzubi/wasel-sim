from src.models.assumptions import WaselParams
from src.models.state import DriverCohortState, OperationsState, RiderState


def compute_matching(
    drivers: DriverCohortState,
    riders: RiderState,
    params: WaselParams,
    market_ride_cap: float | None = None,
) -> OperationsState:
    supply_capacity = (
        drivers.total_active
        * params.avg_trips_per_driver_per_day_assumed
        * params.operating_days_per_month
    )
    rider_supported_demand = (
        riders.total_riders
        * params.avg_rides_per_rider_per_month
        * (1.0 + params.rider_demand_tolerance)
    )
    if market_ride_cap is None:
        demand_cap = rider_supported_demand
    else:
        demand_cap = min(market_ride_cap, rider_supported_demand)
    actual_rides = min(supply_capacity, demand_cap)
    constrained_demand_served_ratio = actual_rides / demand_cap if demand_cap > 0 else 0.0
    actual_tpd = (
        actual_rides / (drivers.total_active * params.operating_days_per_month)
        if drivers.total_active > 0
        else 0.0
    )
    utilization_ratio = (
        actual_tpd / params.avg_trips_per_driver_per_day_assumed
        if params.avg_trips_per_driver_per_day_assumed > 0
        else 0.0
    )
    actual_driver_gross = actual_tpd * params.avg_fare_per_trip * params.operating_days_per_month
    actual_driver_net_before_subscription = actual_driver_gross - params.total_driver_opex
    if drivers.total_active <= 0:
        income_churn_amplifier = 1.0
    elif utilization_ratio < params.churn_pressure_utilization_floor:
        shortfall_pct = (
            params.churn_pressure_utilization_floor - utilization_ratio
        ) / params.churn_pressure_utilization_floor
        income_churn_amplifier = min(
            params.churn_pressure_max_multiplier,
            1.0 + shortfall_pct * (params.churn_pressure_max_multiplier - 1.0),
        )
    else:
        income_churn_amplifier = 1.0
    return OperationsState(
        actual_rides=actual_rides,
        supply_capacity=supply_capacity,
        rider_supported_demand=rider_supported_demand,
        constrained_demand_rides=demand_cap,
        market_ride_cap=market_ride_cap or demand_cap,
        constrained_demand_served_ratio=constrained_demand_served_ratio,
        actual_trips_per_driver_per_day=actual_tpd,
        utilization_ratio=utilization_ratio,
        income_churn_amplifier=income_churn_amplifier,
    )
