"""
Driver cohort model for Wasel simulation.
"""

from src.models.assumptions import WaselParams
from src.models.state import DriverCohortState


def compute_boycott_multiplier(params: WaselParams, month: int) -> float:
    if month <= params.boycott_multiplier_decay_month:
        return params.boycott_multiplier_initial
    decay_months = month - params.boycott_multiplier_decay_month
    decay_rate = (params.boycott_multiplier_initial - 1.0) / 12.0
    return max(1.0, params.boycott_multiplier_initial - decay_rate * decay_months)


def compute_new_drivers(
    prev_state: DriverCohortState,
    params: WaselParams,
    month: int,
    recruitment_throttle: float = 1.0,
) -> float:
    # Boycott (Uber Flytrex controversy) lowers driver CAC, captured in financial_model via
    # driver_cac_marketing.  It should NOT inflate the raw acquisition count — doing so caused
    # 1.25× over-recruitment that compounded through the entire driver pool.
    if month == 1:
        raw = float(params.seed_month1)
    else:
        raw = prev_state.total_active * params.monthly_growth_rate
        raw *= recruitment_throttle
    remaining_tam = max(0.0, params.max_tam_unlicensed - prev_state.total_active)
    raw = min(raw, remaining_tam)
    remaining_regulatory_cap = max(0.0, params.max_drivers_phase1 - prev_state.total_active)
    raw = min(raw, remaining_regulatory_cap)
    return raw


def update_driver_cohorts(
    prev: DriverCohortState,
    params: WaselParams,
    month: int,
    income_churn_amplifier: float = 1.0,
    recruitment_throttle: float = 1.0,
) -> DriverCohortState:
    new_drivers = compute_new_drivers(prev, params, month, recruitment_throttle=recruitment_throttle)
    m0_to_m1 = prev.m0_drivers * (1 - params.m0_m1_churn)
    effective_m1_m2 = min(0.99, params.m1_m2_churn * income_churn_amplifier)
    m1_to_m2p = prev.m1_drivers * (1 - effective_m1_m2)
    effective_early_churn = min(0.99, params.m2_m6_monthly_churn * income_churn_amplifier)
    early_retained = prev.m2p_early_drivers * (1 - effective_early_churn)
    graduation_rate = 1.0 / params.early_to_mature_months
    graduating = early_retained * graduation_rate
    new_m2p_early = early_retained - graduating + m1_to_m2p
    effective_mature_churn = min(0.99, params.m6_plus_monthly_churn * income_churn_amplifier)
    mature_retained = prev.m2p_mature_drivers * (1 - effective_mature_churn)
    new_m2p_mature = mature_retained + graduating
    churned = (
        prev.m0_drivers * params.m0_m1_churn
        + prev.m1_drivers * effective_m1_m2
        + prev.m2p_early_drivers * effective_early_churn
        + prev.m2p_mature_drivers * effective_mature_churn
    )
    return DriverCohortState(
        m0_drivers=new_drivers,
        m1_drivers=m0_to_m1,
        m2p_early_drivers=new_m2p_early,
        m2p_mature_drivers=new_m2p_mature,
        new_drivers_this_month=new_drivers,
        churned_this_month=churned,
    )
