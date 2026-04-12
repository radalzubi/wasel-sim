from __future__ import annotations

import math

from src.models.assumptions import WaselParams


def seasonal_factor(month: int, params: WaselParams) -> float:
    idx = (month - 1) % 12
    return params.seasonality_factors[idx]


def market_rides_for_month(month: int, params: WaselParams) -> float:
    growth = (1 + params.market_growth_rate_annual / 12) ** (month - 1)
    return params.base_monthly_rides_jordan * growth * seasonal_factor(month, params)


def driver_supply_quality_index(active_drivers: float, params: WaselParams) -> float:
    return min(active_drivers / params.threshold_drivers_for_reliability, 1.0)


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
    return _interpolate_market_share_ceiling(month, params) * quality


def wasel_addressable_rides(month: int, active_drivers: float, params: WaselParams) -> float:
    return market_rides_for_month(month, params) * wasel_market_share_cap(month, active_drivers, params)
