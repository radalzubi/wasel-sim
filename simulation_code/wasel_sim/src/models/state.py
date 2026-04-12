from dataclasses import dataclass


@dataclass
class DriverCohortState:
    m0_drivers: float = 0.0
    m1_drivers: float = 0.0
    m2p_early_drivers: float = 0.0
    m2p_mature_drivers: float = 0.0
    new_drivers_this_month: float = 0.0
    churned_this_month: float = 0.0

    @property
    def total_active(self) -> float:
        return self.m0_drivers + self.m1_drivers + self.m2p_early_drivers + self.m2p_mature_drivers

    @property
    def m2p_total(self) -> float:
        return self.m2p_early_drivers + self.m2p_mature_drivers

    @property
    def starter_drivers(self) -> float:
        return self.m2p_total * 0.45

    @property
    def core_drivers(self) -> float:
        return self.m2p_total * 0.35

    @property
    def pro_drivers(self) -> float:
        return self.m2p_total * 0.20


@dataclass
class RiderState:
    total_riders: float = 0.0
    new_riders_this_month: float = 0.0
    churned_riders_this_month: float = 0.0

    @property
    def go_subscribers(self) -> float:
        return self.total_riders * 0.10

    @property
    def pass_subscribers(self) -> float:
        return self.total_riders * 0.05


@dataclass
class OperationsState:
    actual_rides: float = 0.0
    supply_capacity: float = 0.0
    demand_rides: float = 0.0
    market_ride_cap: float = 0.0
    fulfillment_rate: float = 0.0
    actual_trips_per_driver_per_day: float = 0.0
    utilization_ratio: float = 0.0
    income_churn_amplifier: float = 1.0


@dataclass
class FinancialState:
    driver_sub_revenue: float = 0.0
    rider_sub_revenue: float = 0.0
    total_revenue: float = 0.0
    total_cogs: float = 0.0
    gross_profit: float = 0.0
    gross_margin: float = 0.0
    driver_marketing_cost: float = 0.0
    rider_marketing_cost: float = 0.0
    license_cash_payment: float = 0.0
    contribution_margin: float = 0.0
    total_opex: float = 0.0
    ebitda: float = 0.0
    net_income: float = 0.0
    cash_balance: float = 0.0
    cumulative_net_income: float = 0.0
