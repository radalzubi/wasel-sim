from __future__ import annotations

from src.models.assumptions import WaselParams


def expected_price_war_probability(params: WaselParams) -> float:
    incumbents = ["uber", "careem"]
    probabilities = [
        params.competitors[name].price_war_probability
        for name in incumbents
        if name in params.competitors
    ]
    return max(probabilities) if probabilities else 0.0


def rider_acquisition_pressure_multiplier(params: WaselParams) -> float:
    probability = expected_price_war_probability(params)
    return 1.0 + probability * 0.2
