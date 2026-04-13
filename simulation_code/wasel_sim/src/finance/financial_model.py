import math

from src.drivers.cohort_model import compute_boycott_multiplier
from src.models.assumptions import WaselParams
from src.models.state import DriverCohortState, FinancialState, OperationsState, RiderState
from src.riders.rider_model import get_rider_marketing_spend


def _tier_driver_count(drivers: DriverCohortState, params: WaselParams, tier_name: str) -> float:
    return drivers.m2p_total * params.tiers[tier_name].driver_mix


def compute_driver_subscription_revenue(drivers: DriverCohortState, params: WaselParams) -> float:
    return (
        drivers.m1_drivers * params.m1_fee
        + _tier_driver_count(drivers, params, "starter") * params.tiers["starter"].monthly_fee
        + _tier_driver_count(drivers, params, "core") * params.tiers["core"].monthly_fee
        + _tier_driver_count(drivers, params, "pro") * params.tiers["pro"].monthly_fee
    )


def compute_cogs(
    drivers: DriverCohortState,
    ops: OperationsState,
    driver_sub_rev: float,
    params: WaselParams,
) -> float:
    digital_rev = driver_sub_rev * params.payment_processing_digital_fraction
    payment_processing = digital_rev * params.payment_processing_rate
    insurance = drivers.m2p_total * params.blended_insurance_per_driver
    cloud = (
        params.cloud_base_monthly * (1 + 0.05 * math.log(max(1.0, drivers.total_active / 100)))
        if drivers.total_active > 0
        else params.cloud_base_monthly
    )
    maps = params.maps_base_monthly * max(1.0, ops.actual_rides / 58500)
    sms = params.sms_base_monthly * max(1.0, drivers.total_active / 250)
    onboarding = drivers.new_drivers_this_month * params.driver_onboarding_cost
    return payment_processing + insurance + cloud + maps + sms + onboarding


def compute_opex(
    drivers: DriverCohortState,
    month: int,
    rider_marketing_spend: float,
    params: WaselParams,
) -> tuple[float, float, float, float]:
    team = params.monthly_team_overhead
    regulatory_license_expense = (
        params.monthly_regulatory
        + params.annual_compliance_audit / 12.0
    )
    legal = params.monthly_legal
    support = params.support_base_monthly * max(1.0, math.log(max(1.0, drivers.total_active / 250 + 1)))
    boycott_multiplier = compute_boycott_multiplier(params, month)
    effective_driver_cac = params.driver_cac_marketing / min(max(boycott_multiplier, 1.0), 1.25)
    driver_mktg = drivers.new_drivers_this_month * effective_driver_cac
    variance = params.opex_variance_monthly.get(month, 0.0)
    total = (
        team
        + regulatory_license_expense
        + legal
        + support
        + driver_mktg
        + rider_marketing_spend
        + variance
    )
    return total, driver_mktg, rider_marketing_spend, regulatory_license_expense


def compute_license_cash_payment(month: int, params: WaselParams) -> float:
    if month < params.license_payment_start_month:
        return 0.0
    if (month - params.license_payment_start_month) % 12 == 0:
        return params.annual_ltrc_license
    return 0.0


def compute_financials(
    month: int,
    drivers: DriverCohortState,
    riders: RiderState,
    ops: OperationsState,
    prev_cash: float,
    prev_cum_ni: float,
    params: WaselParams,
) -> FinancialState:
    driver_rev = compute_driver_subscription_revenue(drivers, params)
    total_rev = driver_rev
    total_cogs = compute_cogs(drivers, ops, driver_rev, params)
    gross_profit = total_rev - total_cogs
    gross_margin = gross_profit / total_rev if total_rev > 0 else 0.0
    rider_mktg = get_rider_marketing_spend(params, month)
    total_opex, driver_mktg, rider_mktg, regulatory_license_expense = compute_opex(
        drivers,
        month,
        rider_mktg,
        params,
    )
    license_cash_payment = compute_license_cash_payment(month, params)
    contribution_margin = gross_profit - driver_mktg - rider_mktg
    ebitda = gross_profit - total_opex
    net_income = ebitda - params.monthly_da
    cash_balance = prev_cash + net_income - license_cash_payment
    cumulative_net_income = prev_cum_ni + net_income
    return FinancialState(
        driver_sub_revenue=driver_rev,
        total_revenue=total_rev,
        total_cogs=total_cogs,
        gross_profit=gross_profit,
        gross_margin=gross_margin,
        driver_marketing_cost=driver_mktg,
        rider_marketing_cost=rider_mktg,
        regulatory_license_expense=regulatory_license_expense,
        license_cash_payment=license_cash_payment,
        contribution_margin=contribution_margin,
        total_opex=total_opex,
        ebitda=ebitda,
        net_income=net_income,
        cash_balance=cash_balance,
        cumulative_net_income=cumulative_net_income,
    )
