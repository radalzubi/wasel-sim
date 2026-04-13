from __future__ import annotations

from src.models.assumptions import WaselParams


def expected_discount_pressure(params: WaselParams) -> float:
    weighted_pressure = 0.0
    total_share = 0.0
    for competitor in params.competitors.values():
        share = competitor.market_share_initial
        weighted_pressure += share * competitor.price_war_probability * competitor.max_discount_to_riders_pct
        total_share += share
    if total_share <= 0:
        return 0.0
    return weighted_pressure / total_share


def competition_intensity(month: int, params: WaselParams) -> float:
    if month >= params.competition_pressure_months:
        return 0.0
    remaining = params.competition_pressure_months - month + 1
    return max(0.0, remaining / params.competition_pressure_months)


def rider_acquisition_pressure_multiplier(month: int, params: WaselParams) -> float:
    pressure = expected_discount_pressure(params)
    return 1.0 + pressure * params.competition_cac_weight * competition_intensity(month, params)


def organic_growth_penalty_multiplier(month: int, params: WaselParams) -> float:
    pressure = expected_discount_pressure(params)
    penalty = pressure * params.competition_organic_growth_penalty_weight * competition_intensity(month, params)
    return max(0.80, 1.0 - penalty)


def share_cap_penalty_multiplier(month: int, params: WaselParams) -> float:
    pressure = expected_discount_pressure(params)
    penalty = pressure * params.competition_share_penalty_weight * competition_intensity(month, params)
    return max(0.85, 1.0 - penalty)
