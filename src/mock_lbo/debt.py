"""Non-circular financing waterfall. All amounts in USD millions."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Waterfall:
    senior: float
    junior: float
    revolver: float
    lease: float
    draw: float
    revolver_pay: float
    senior_pay: float
    amort: float
    lease_pay: float
    cash: float
    liquidity_gap: float


def waterfall(*, cash: float, fcf: float, minimum: float, senior: float, junior: float,
              revolver: float, lease: float, senior_original: float, capacity: float,
              amort_rate: float, lease_annual: float, sweep: float) -> Waterfall:
    """Use period-end revolver funding; retain a deficit instead of inventing equity."""
    amort = min(senior, senior_original * amort_rate / 4)
    lease_pay = min(lease, lease_annual / 4)
    available = cash + fcf - amort - lease_pay
    draw = min(max(0.0, minimum - available), max(0.0, capacity - revolver))
    excess = max(0.0, available + draw - minimum)
    revolver_pay = min(revolver, excess)
    senior_pay = min(max(0.0, senior - amort), max(0.0, excess - revolver_pay) * sweep)
    ending_cash = available + draw - revolver_pay - senior_pay
    return Waterfall(senior - amort - senior_pay, junior, revolver + draw - revolver_pay,
                     lease - lease_pay, draw, revolver_pay, senior_pay, amort, lease_pay,
                     ending_cash, max(0.0, minimum - ending_cash))
