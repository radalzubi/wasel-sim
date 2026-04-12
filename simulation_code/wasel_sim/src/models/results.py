from dataclasses import dataclass
from typing import Dict


@dataclass
class SummaryMetrics:
    year1_net_income: float
    year2_net_income: float
    year3_net_income: float
    year5_cumulative_net_income: float
    end_of_year1_cash: float
    end_of_year2_cash: float
    break_even_month: int

    def as_dict(self) -> Dict[str, float]:
        return self.__dict__.copy()
