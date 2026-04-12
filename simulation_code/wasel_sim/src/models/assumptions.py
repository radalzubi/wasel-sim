from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Dict, List

import yaml


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


@dataclass
class TierConfig:
    monthly_fee: float
    driver_mix: float
    trip_cap: int
    monthly_gross_revenue: float


@dataclass
class CompetitorConfig:
    market_share_initial: float
    commission_rate: float
    avg_fare: float
    driver_count: int
    price_war_probability: float
    max_discount_to_riders_pct: float


@dataclass
class WaselParams:
    base_monthly_rides_jordan: int
    market_growth_rate_annual: float
    threshold_drivers_for_reliability: int
    wasel_max_market_share: float
    wasel_max_market_share_year3: float
    wasel_max_market_share_year5: float
    operating_days_per_month: int
    seasonality_factors: List[float]
    seed_month1: int
    monthly_growth_rate: float
    max_drivers_phase1: int
    max_tam_unlicensed: int
    avg_trips_per_driver_per_day_assumed: float
    avg_fare_per_trip: float
    fuel_cost_per_month: float
    maintenance_cost_per_month: float
    data_misc_per_month: float
    total_driver_opex: float
    driver_cac_marketing: float
    driver_onboarding_cost: float
    driver_total_cac: float
    boycott_multiplier_initial: float
    boycott_multiplier_decay_month: int
    m0_fee: float
    m0_m1_churn: float
    m1_fee: float
    m1_m2_churn: float
    m2_m6_monthly_churn: float
    m6_plus_monthly_churn: float
    early_to_mature_months: int
    tiers: Dict[str, TierConfig]
    blended_fee: float
    payment_processing_digital_fraction: float
    payment_processing_rate: float
    blended_insurance_per_driver: float
    cloud_allocated_per_driver: float
    monthly_team_overhead: float
    monthly_regulatory: float
    monthly_legal: float
    cloud_base_monthly: float
    support_base_monthly: float
    maps_base_monthly: float
    sms_base_monthly: float
    monthly_da: float
    rider_monthly_marketing_spend: List[float]
    initial_waitlist_riders: float
    rider_cac_base: float
    organic_growth_rate: float
    avg_rides_per_rider_per_month: float
    rider_demand_tolerance: float
    early_rider_churn_rate: float
    steady_rider_churn_rate: float
    churn_stabilize_month: int
    standard_free_mix: float
    go_paid_mix: float
    pass_paid_mix: float
    go_monthly_fee: float
    pass_monthly_fee: float
    opex_variance_monthly: Dict[int, float]
    annual_ltrc_license: float
    license_payment_start_month: int
    seed_capital: float
    total_prelaunch_capex: float
    recommended_raise: float
    competitors: Dict[str, CompetitorConfig]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def copy_with(self, **updates: Any) -> "WaselParams":
        return replace(self, **updates)

    @classmethod
    def from_yaml(cls, path: Path, override_path: Path | None = None) -> "WaselParams":
        with open(path, "r", encoding="utf-8") as handle:
            raw = yaml.safe_load(handle)
        if override_path:
            with open(override_path, "r", encoding="utf-8") as handle:
                override = yaml.safe_load(handle) or {}
            raw = _deep_merge(raw, override)
        return cls.from_dict(raw)

    @classmethod
    def from_dict(cls, raw: Dict[str, Any]) -> "WaselParams":
        tiers = {
            name: TierConfig(**config)
            for name, config in raw["tiers"].items()
            if name in {"starter", "core", "pro"}
        }
        competitors = {
            name: CompetitorConfig(**config)
            for name, config in raw["competitors"].items()
        }
        params = cls(
            base_monthly_rides_jordan=raw["market"]["base_monthly_rides_jordan"],
            market_growth_rate_annual=raw["market"]["market_growth_rate_annual"],
            threshold_drivers_for_reliability=raw["market"]["threshold_drivers_for_reliability"],
            wasel_max_market_share=raw["market"]["wasel_max_market_share"],
            wasel_max_market_share_year3=raw["market"].get(
                "wasel_max_market_share_year3",
                raw["market"]["wasel_max_market_share"],
            ),
            wasel_max_market_share_year5=raw["market"].get(
                "wasel_max_market_share_year5",
                raw["market"].get("wasel_max_market_share_year3", raw["market"]["wasel_max_market_share"]),
            ),
            operating_days_per_month=raw["market"]["operating_days_per_month"],
            seasonality_factors=raw["seasonality"]["factors"],
            seed_month1=raw["drivers"]["seed_month1"],
            monthly_growth_rate=raw["drivers"]["monthly_growth_rate"],
            max_drivers_phase1=raw["drivers"]["max_drivers_phase1"],
            max_tam_unlicensed=raw["drivers"]["max_tam_unlicensed"],
            avg_trips_per_driver_per_day_assumed=raw["drivers"]["avg_trips_per_driver_per_day_assumed"],
            avg_fare_per_trip=raw["drivers"]["avg_fare_per_trip"],
            fuel_cost_per_month=raw["drivers"]["fuel_cost_per_month"],
            maintenance_cost_per_month=raw["drivers"]["maintenance_cost_per_month"],
            data_misc_per_month=raw["drivers"]["data_misc_per_month"],
            total_driver_opex=raw["drivers"]["total_driver_opex"],
            driver_cac_marketing=raw["drivers"]["driver_cac_marketing"],
            driver_onboarding_cost=raw["drivers"]["driver_onboarding_cost"],
            driver_total_cac=raw["drivers"]["driver_total_cac"],
            boycott_multiplier_initial=raw["drivers"]["boycott_multiplier_initial"],
            boycott_multiplier_decay_month=raw["drivers"]["boycott_multiplier_decay_month"],
            m0_fee=raw["onboarding"]["m0_fee"],
            m0_m1_churn=raw["onboarding"]["m0_m1_churn"],
            m1_fee=raw["onboarding"]["m1_fee"],
            m1_m2_churn=raw["onboarding"]["m1_m2_churn"],
            m2_m6_monthly_churn=raw["onboarding"]["m2_m6_monthly_churn"],
            m6_plus_monthly_churn=raw["onboarding"]["m6_plus_monthly_churn"],
            early_to_mature_months=raw["onboarding"]["early_to_mature_months"],
            tiers=tiers,
            blended_fee=raw["tiers"]["blended_fee"],
            payment_processing_digital_fraction=raw["platform_costs_per_driver"]["payment_processing_digital_fraction"],
            payment_processing_rate=raw["platform_costs_per_driver"]["payment_processing_rate"],
            blended_insurance_per_driver=raw["platform_costs_per_driver"]["blended_insurance_per_driver"],
            cloud_allocated_per_driver=raw["platform_costs_per_driver"]["cloud_allocated_per_driver"],
            monthly_team_overhead=raw["fixed_opex"]["monthly_team_overhead"],
            monthly_regulatory=raw["fixed_opex"]["monthly_regulatory"],
            monthly_legal=raw["fixed_opex"]["monthly_legal"],
            cloud_base_monthly=raw["fixed_opex"]["cloud_base_monthly"],
            support_base_monthly=raw["fixed_opex"]["support_base_monthly"],
            maps_base_monthly=raw["fixed_opex"]["maps_base_monthly"],
            sms_base_monthly=raw["fixed_opex"]["sms_base_monthly"],
            monthly_da=raw["fixed_opex"]["monthly_da"],
            rider_monthly_marketing_spend=raw["riders"]["monthly_marketing_spend"],
            initial_waitlist_riders=raw["riders"].get("initial_waitlist_riders", 0.0),
            rider_cac_base=raw["riders"]["rider_cac_base"],
            organic_growth_rate=raw["riders"]["organic_growth_rate"],
            avg_rides_per_rider_per_month=raw["riders"]["avg_rides_per_rider_per_month"],
            rider_demand_tolerance=raw["riders"].get("rider_demand_tolerance", 0.0),
            early_rider_churn_rate=raw["riders"]["early_rider_churn_rate"],
            steady_rider_churn_rate=raw["riders"]["steady_rider_churn_rate"],
            churn_stabilize_month=raw["riders"]["churn_stabilize_month"],
            standard_free_mix=raw["riders"]["standard_free_mix"],
            go_paid_mix=raw["riders"]["go_paid_mix"],
            pass_paid_mix=raw["riders"]["pass_paid_mix"],
            go_monthly_fee=raw["riders"]["go_monthly_fee"],
            pass_monthly_fee=raw["riders"]["pass_monthly_fee"],
            opex_variance_monthly={int(k): float(v) for k, v in raw["opex_variance"]["monthly_schedule"].items()},
            annual_ltrc_license=raw["regulatory"]["annual_ltrc_license"],
            license_payment_start_month=raw["regulatory"].get("license_payment_start_month", 1),
            seed_capital=raw["seed_capital"],
            total_prelaunch_capex=raw["prelaunch_capex"]["total"],
            recommended_raise=raw["recommended_raise"],
            competitors=competitors,
            metadata=raw.get("metadata", {}),
        )
        params.validate()
        return params

    def validate(self) -> None:
        if not 0.05 <= self.monthly_growth_rate <= 0.60:
            raise ValueError(f"monthly_growth_rate out of range: {self.monthly_growth_rate}")
        if self.seed_month1 <= 0:
            raise ValueError("seed_month1 must be positive")
        if not (
            0 < self.wasel_max_market_share <= self.wasel_max_market_share_year3 <= self.wasel_max_market_share_year5 <= 1
        ):
            raise ValueError("market share ramp must be positive, non-decreasing, and <= 1")
        if self.initial_waitlist_riders < 0:
            raise ValueError("initial_waitlist_riders cannot be negative")
        if not 0.0 <= self.rider_demand_tolerance <= 0.50:
            raise ValueError("rider_demand_tolerance must be between 0 and 0.50")
        if len(self.seasonality_factors) != 12:
            raise ValueError("seasonality_factors must have 12 monthly values")
