from __future__ import annotations

import math

from src.competitors.competitor_model import share_cap_penalty_multiplier
from src.models.assumptions import WaselParams


def seasonal_factor(month: int, params: WaselParams) -> float:
    idx = (month - 1) % 12
    return params.seasonality_factors[idx]


def market_rides_for_month(month: int, params: WaselParams) -> float:
    growth = (1 + params.market_growth_rate_annual / 12) ** (month - 1)
    return params.base_monthly_rides_jordan * growth * seasonal_factor(month, params)


def driver_supply_quality_index(active_drivers: float, params: WaselParams) -> float:
    if active_drivers <= 0:
        return 0.0
    raw_quality = min(active_drivers / params.threshold_drivers_for_reliability, 1.0)
    return params.driver_liquidity_floor + (1.0 - params.driver_liquidity_floor) * raw_quality


def launch_reachable_share(month: int, params: WaselParams) -> float:
    if month <= 12:
        return params.launch_reachable_share_year1
    if month <= 36:
        span = 36 - 12
        progress = (month - 12) / span
        return params.launch_reachable_share_year1 + (
            params.launch_reachable_share_year3 - params.launch_reachable_share_year1
        ) * progress
    if month <= 60:
        span = 60 - 36
        progress = (month - 36) / span
        return params.launch_reachable_share_year3 + (
            params.launch_reachable_share_year5 - params.launch_reachable_share_year3
        ) * progress
    return params.launch_reachable_share_year5


def _interpolate_market_share_ceiling(month: int, params: WaselParams) -> float:
    if month <= 12:
        return params.wasel_max_market_share
    if month <= 36:
        span = 36 - 12
        progress = (month - 12) / span
        return params.wasel_max_market_share + (
            params.wasel_max_market_share_year3 - params.wasel_max_market_share
        ) * progress
    if month <= 60:
        span = 60 - 36
        progress = (month - 36) / span
        return params.wasel_max_market_share_year3 + (
            params.wasel_max_market_share_year5 - params.wasel_max_market_share_year3
        ) * progress
    return params.wasel_max_market_share_year5


def wasel_market_share_cap(month: int, active_drivers: float, params: WaselParams) -> float:
    quality = driver_supply_quality_index(active_drivers, params)
    penalty = share_cap_penalty_multiplier(month, params)
    return _interpolate_market_share_ceiling(month, params) * quality * penalty


def wasel_addressable_rides(month: int, active_drivers: float, params: WaselParams) -> float:
    return (
        market_rides_for_month(month, params)
        * launch_reachable_share(month, params)
        * wasel_market_share_cap(month, active_drivers, params)
    )
