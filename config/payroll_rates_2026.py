"""Configurable Moroccan payroll parameters for the 2026 calculation model.

Amounts are in Moroccan dirhams and rates are Decimal fractions.
The professional-expense cap is intentionally unset until the applicable
regulatory source is confirmed for the employee category.
"""
from decimal import Decimal

CNSS_CEILING = Decimal("6000.00")

CNSS_EMPLOYEE_SHORT_TERM = Decimal("0.0052")
CNSS_EMPLOYEE_LONG_TERM = Decimal("0.0396")
AMO_EMPLOYEE = Decimal("0.0226")

CNSS_EMPLOYER_FAMILY = Decimal("0.0640")
CNSS_EMPLOYER_SHORT_TERM = Decimal("0.0105")
CNSS_EMPLOYER_LONG_TERM = Decimal("0.0793")
AMO_EMPLOYER = Decimal("0.0411")
TRAINING_TAX_EMPLOYER = Decimal("0.0160")

PROFESSIONAL_EXPENSE_RATE_2026 = Decimal("0.35")
PROFESSIONAL_EXPENSE_ANNUAL_CAP_2026 = None
# Compatibility aliases used by the calculator and settings UI.
FRAIS_PROFESSIONNELS_RATE = PROFESSIONAL_EXPENSE_RATE_2026
FRAIS_PROFESSIONNELS_MONTHLY_CAP = None
FAMILY_DEDUCTION_ANNUAL_PER_DEPENDENT = Decimal("360.00")

IR_ANNUAL_BRACKETS = (
    (Decimal("0.00"), Decimal("40000.00"), Decimal("0.00")),
    (Decimal("40000.00"), Decimal("60000.00"), Decimal("0.10")),
    (Decimal("60000.00"), Decimal("80000.00"), Decimal("0.20")),
    (Decimal("80000.00"), Decimal("100000.00"), Decimal("0.30")),
    (Decimal("100000.00"), Decimal("180000.00"), Decimal("0.34")),
    (Decimal("180000.00"), None, Decimal("0.37")),
)
