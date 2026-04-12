from src.models.assumptions import WaselParams
from src.models.state import RiderState


def get_rider_marketing_spend(params: WaselParams, month: int) -> float:
    if month <= len(params.rider_monthly_marketing_spend):
        return params.rider_monthly_marketing_spend[month - 1]
    return params.rider_monthly_marketing_spend[-1]


def update_rider_base(
    prev: RiderState,
    params: WaselParams,
    month: int,
    boycott_multiplier: float = 1.0,
) -> RiderState:
    marketing_spend = get_rider_marketing_spend(params, month)
    effective_cac = params.rider_cac_base / min(boycott_multiplier, 1.25)
    marketing_riders = marketing_spend / effective_cac if effective_cac else 0.0
    organic_riders = prev.total_riders * params.organic_growth_rate
    churn_rate = (
        params.early_rider_churn_rate
        if month <= params.churn_stabilize_month
        else params.steady_rider_churn_rate
    )
    churned = prev.total_riders * churn_rate
    total = max(0.0, prev.total_riders + marketing_riders + organic_riders - churned)
    return RiderState(
        total_riders=total,
        new_riders_this_month=marketing_riders + organic_riders,
        churned_riders_this_month=churned,
    )
