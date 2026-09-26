"""Simplified blended taxes, explicitly not a jurisdictional tax opinion."""


def cash_tax(*, ebitda: float, tax_depreciation: float, interest: float,
             interest_carry: float, nol: float, rate: float, interest_limit: float,
             nol_limit: float) -> dict[str, float]:
    deductible = min(interest+interest_carry, max(0.0, ebitda)*interest_limit)
    taxable = ebitda-tax_depreciation-deductible
    used = min(nol, max(0.0, taxable)*nol_limit)
    tax = max(0.0, taxable-used)*rate
    return dict(deductible=deductible,interest_carry=interest_carry+interest-deductible,
                taxable=taxable,nol_used=used,nol=nol+max(0.0,-taxable)-used,cash_tax=tax)
