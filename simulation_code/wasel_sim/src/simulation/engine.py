import pandas as pd

from src.drivers.cohort_model import compute_boycott_multiplier, update_driver_cohorts
from src.market.jordan_market import wasel_addressable_rides
from src.finance.financial_model import compute_financials
from src.models.assumptions import WaselParams
from src.models.state import DriverCohortState, RiderState
from src.operations.matching import compute_matching
from src.riders.rider_model import update_rider_base


def run_simulation(params: WaselParams, n_months: int = 60) -> pd.DataFrame:
    drivers = DriverCohortState()
    riders = RiderState(total_riders=params.initial_waitlist_riders)
    prev_cash = params.seed_capital - params.total_prelaunch_capex
    prev_cum_ni = 0.0
    records = []

    for month in range(1, n_months + 1):
        boycott = compute_boycott_multiplier(params, month)
        market_cap_pre = wasel_addressable_rides(month, drivers.total_active, params)
        ops_pre = compute_matching(drivers, riders, params, market_ride_cap=market_cap_pre)

        # Riders are computed first so the driver balance constraint can reference this month's
        # rider base (Hamdi Tabaa's guidance: no side should far outpace the other).
        riders_new = update_rider_base(riders, params, month, boycott_multiplier=boycott)

        if month == 1:
            recruitment_throttle = 1.0
        else:
            recruitment_throttle = ops_pre.utilization_ratio / params.recruitment_target_utilization
            recruitment_throttle = max(
                params.recruitment_floor_multiplier,
                min(1.0, recruitment_throttle),
            )

        drivers_new = update_driver_cohorts(
            drivers,
            params,
            month,
            income_churn_amplifier=ops_pre.income_churn_amplifier,
            recruitment_throttle=recruitment_throttle,
        )
        market_cap_post = wasel_addressable_rides(month, drivers_new.total_active, params)
        ops = compute_matching(drivers_new, riders_new, params, market_ride_cap=market_cap_post)
        fin = compute_financials(month, drivers_new, riders_new, ops, prev_cash, prev_cum_ni, params)
        records.append(
            {
                "month": month,
                "market_ride_cap": market_cap_post,
                "boycott_multiplier": boycott,
                "m0_drivers": drivers_new.m0_drivers,
                "m1_drivers": drivers_new.m1_drivers,
                "m2p_early_drivers": drivers_new.m2p_early_drivers,
                "m2p_mature_drivers": drivers_new.m2p_mature_drivers,
                "total_active_drivers": drivers_new.total_active,
                "m2p_total": drivers_new.m2p_total,
                "new_drivers": drivers_new.new_drivers_this_month,
                "churned_drivers": drivers_new.churned_this_month,
                "total_riders": riders_new.total_riders,
                "new_riders": riders_new.new_riders_this_month,
                "churned_riders": riders_new.churned_riders_this_month,
                "actual_rides": ops.actual_rides,
                "supply_capacity": ops.supply_capacity,
                "rider_supported_demand": ops.rider_supported_demand,
                "constrained_demand_rides": ops.constrained_demand_rides,
                "constrained_demand_served_ratio": ops.constrained_demand_served_ratio,
                "actual_trips_per_driver_per_day": ops.actual_trips_per_driver_per_day,
                "utilization_ratio": ops.utilization_ratio,
                "income_churn_amplifier": ops.income_churn_amplifier,
                "driver_sub_revenue": fin.driver_sub_revenue,
                "total_revenue": fin.total_revenue,
                "total_cogs": fin.total_cogs,
                "gross_profit": fin.gross_profit,
                "gross_margin": fin.gross_margin,
                "driver_marketing": fin.driver_marketing_cost,
                "rider_marketing": fin.rider_marketing_cost,
                "regulatory_license_expense": fin.regulatory_license_expense,
                "license_cash_payment": fin.license_cash_payment,
                "contribution_margin": fin.contribution_margin,
                "total_opex": fin.total_opex,
                "ebitda": fin.ebitda,
                "net_income": fin.net_income,
                "cash_balance": fin.cash_balance,
                "cumulative_net_income": fin.cumulative_net_income,
            }
        )
        drivers = drivers_new
        riders = riders_new
        prev_cash = fin.cash_balance
        prev_cum_ni = fin.cumulative_net_income

    return pd.DataFrame(records)
