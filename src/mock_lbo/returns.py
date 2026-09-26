"""Dated cash-flow returns without a market-data or solver dependency."""
from datetime import date


def xnpv(rate: float, flows: list[float], dates: list[date]) -> float:
    if rate <= -1 or len(flows) != len(dates) or not flows:
        raise ValueError("Invalid discount rate or cash-flow series")
    return sum(c / (1 + rate) ** ((d - dates[0]).days / 365) for c, d in zip(flows, dates, strict=True))


def xirr(flows: list[float], dates: list[date]) -> float | None:
    """Bisection for conventional flows only; do not assert uniqueness otherwise."""
    if len(flows) != len(dates) or len(flows) < 2 or dates != sorted(dates):
        raise ValueError("Mismatched or unordered cash flows")
    if flows[0] >= 0 or any(v < 0 for v in flows[1:]):
        raise ValueError("Only one initial contribution is supported")
    if max(flows[1:]) <= 0 or dates[-1] <= dates[0]:
        return None
    low, high = -0.999999999, 1.0
    while xnpv(high, flows, dates) > 0:
        high = high * 2 + 1
        if high > 1e9:
            raise ValueError("No bracketed return")
    for _ in range(200):
        mid = (low + high) / 2
        if xnpv(mid, flows, dates) > 0:
            low = mid
        else:
            high = mid
    return (low + high) / 2
