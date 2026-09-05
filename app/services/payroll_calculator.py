"""Decimal-based Moroccan payroll calculations for the configured year."""
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from config import payroll_rates_2026 as rates

CENT = Decimal("0.01")


def money(value: Any) -> Decimal:
    """Convert a value without importing binary floating-point artifacts."""
    return Decimal(str(value or 0)).quantize(CENT, rounding=ROUND_HALF_UP)


class PayrollRulesMorocco:
    """Calculate payroll using centralized, configurable Decimal parameters."""

    def __init__(self, year: int = 2026):
        self.year = year
        if year != 2026:
            raise ValueError("Seuls les paramètres configurés pour 2026 sont disponibles.")

    @staticmethod
    def calculate_employee_social_contributions(gross_salary: Any) -> dict[str, Decimal]:
        gross = money(gross_salary)
        capped_base = min(gross, rates.CNSS_CEILING)
        short_term = money(capped_base * rates.CNSS_EMPLOYEE_SHORT_TERM)
        long_term = money(capped_base * rates.CNSS_EMPLOYEE_LONG_TERM)
        amo = money(gross * rates.AMO_EMPLOYEE)
        return {
            "base_court_terme": capped_base,
            "cotisation_court_terme": short_term,
            "base_long_terme": capped_base,
            "cotisation_long_terme": long_term,
            "base_amo": gross,
            "amo_salarie": amo,
            "total_cotisations_salariales": money(short_term + long_term + amo),
        }

    @staticmethod
    def calculate_employer_contributions(gross_salary: Any) -> dict[str, Decimal]:
        gross = money(gross_salary)
        capped_base = min(gross, rates.CNSS_CEILING)
        family = money(gross * rates.CNSS_EMPLOYER_FAMILY)
        short_term = money(capped_base * rates.CNSS_EMPLOYER_SHORT_TERM)
        long_term = money(capped_base * rates.CNSS_EMPLOYER_LONG_TERM)
        amo = money(gross * rates.AMO_EMPLOYER)
        training = money(gross * rates.TRAINING_TAX_EMPLOYER)
        total = money(family + short_term + long_term + amo + training)
        return {
            "allocations_familiales": family,
            "base_court_terme_employeur": capped_base,
            "prestations_court_terme_employeur": short_term,
            "base_long_terme_employeur": capped_base,
            "prestations_long_terme_employeur": long_term,
            "base_amo_employeur": gross,
            "amo_employeur": amo,
            "taxe_formation_professionnelle": training,
            "total_charges_patronales": total,
        }

    @staticmethod
    def calculate_ir_annual(taxable_income: Any) -> Decimal:
        income = max(money(taxable_income), Decimal("0.00"))
        tax = Decimal("0.00")
        for lower, upper, rate in rates.IR_ANNUAL_BRACKETS:
            if income <= lower:
                continue
            taxable_in_bracket = income - lower if upper is None else min(income, upper) - lower
            if taxable_in_bracket > 0:
                tax += taxable_in_bracket * rate
            if upper is not None and income <= upper:
                break
        return money(tax)

    @classmethod
    def calculate_ir_monthly(cls, monthly_taxable_income: Any) -> Decimal:
        annualized = money(monthly_taxable_income) * Decimal("12")
        return money(cls.calculate_ir_annual(annualized) / Decimal("12"))

    @staticmethod
    def calculate_taxable_income(gross_salary: Any, social_contributions: Any,
                                 professional_expenses: Any,
                                 other_tax_deductions: Any = 0) -> dict[str, Decimal]:
        gross = money(gross_salary)
        social = money(social_contributions)
        professional = money(professional_expenses)
        other = money(other_tax_deductions)
        before_professional = money(max(Decimal("0.00"), gross - social))
        taxable = money(max(Decimal("0.00"), before_professional - professional - other))
        return {
            "gross_salary_imposable": gross,
            "social_contributions_deductible": social,
            "income_before_professional_expenses": before_professional,
            "professional_expenses": professional,
            "other_tax_deductions": other,
            "taxable_income": taxable,
        }

    def calculate_gross_salary(self, base_salary: Any, normal_hours: Any = 0,
                               overtime_hours: Any = 0, overtime_amount: Any = None,
                               bonus: Any = 0,
                               allowances: Any = 0, benefits: Any = 0,
                               absence_days: int = 0) -> dict[str, Decimal]:
        base = money(base_salary)
        absence_deduction = money(Decimal(str(absence_days)) * base / Decimal("22"))
        adjusted_base = money(base - absence_deduction)
        calculated_overtime = (money(overtime_amount) if overtime_amount is not None else
                       money(Decimal(str(overtime_hours)) * base / Decimal("176") * Decimal("1.5")))
        gross = money(adjusted_base + calculated_overtime + money(bonus) + money(allowances) + money(benefits))
        return {
            "base_salary": adjusted_base,
            "overtime_amount": calculated_overtime,
            "bonus": money(bonus),
            "allowances": money(allowances),
            "benefits": money(benefits),
            "gross_salary": gross,
        }

    def calculate_complete_payroll(self, base_salary: Any, children_count: int = 0,
                                   dependents_count: int = 0, overtime_hours: Any = 0,
                                   overtime_amount: Any = None,
                                   bonus: Any = 0, allowances: Any = 0, benefits: Any = 0,
                                   absence_days: int = 0, other_deductions: Any = 0,
                                   other_employer_costs: Any = 0) -> dict[str, Any]:
        earnings = self.calculate_gross_salary(base_salary, overtime_hours=overtime_hours,
                            overtime_amount=overtime_amount,
                                                bonus=bonus, allowances=allowances,
                                                benefits=benefits, absence_days=absence_days)
        gross = earnings["gross_salary"]
        employee = self.calculate_employee_social_contributions(gross)
        employer = self.calculate_employer_contributions(gross)
        professional = money(gross * rates.PROFESSIONAL_EXPENSE_RATE_2026)
        if rates.PROFESSIONAL_EXPENSE_ANNUAL_CAP_2026 is not None:
            professional = min(professional, money(rates.PROFESSIONAL_EXPENSE_ANNUAL_CAP_2026 / 12))
        total_dependents = max(0, int(dependents_count or children_count))
        family_monthly = money(rates.FAMILY_DEDUCTION_ANNUAL_PER_DEPENDENT * total_dependents / 12)
        taxable_detail = self.calculate_taxable_income(
            gross, employee["total_cotisations_salariales"], professional, family_monthly
        )
        taxable_after_family = taxable_detail["taxable_income"]
        ir_brut = self.calculate_ir_monthly(taxable_after_family)
        ir = ir_brut
        other = money(other_deductions)
        total_deductions = money(employee["total_cotisations_salariales"] + ir + other)
        net = money(max(Decimal("0.00"), gross - total_deductions))
        other_employer = money(other_employer_costs)
        total_employer_charges = money(employer["total_charges_patronales"] + other_employer)
        debug = [
            {"name": "CNSS court terme salarié", "base": employee["base_court_terme"], "rate": rates.CNSS_EMPLOYEE_SHORT_TERM, "result": employee["cotisation_court_terme"]},
            {"name": "CNSS long terme salarié", "base": employee["base_long_terme"], "rate": rates.CNSS_EMPLOYEE_LONG_TERM, "result": employee["cotisation_long_terme"]},
            {"name": "AMO salarié", "base": employee["base_amo"], "rate": rates.AMO_EMPLOYEE, "result": employee["amo_salarie"]},
            {"name": "AMO employeur", "base": employer["base_amo_employeur"], "rate": rates.AMO_EMPLOYER, "result": employer["amo_employeur"]},
        ]
        return {
            **earnings,
            "cnss_employee_short_term": employee["cotisation_court_terme"],
            "cnss_employee_long_term": employee["cotisation_long_terme"],
            "cnss_employee": employee["total_cotisations_salariales"],
            "amo_employee": employee["amo_salarie"],
            "professional_expenses": professional,
            "gross_salary_imposable": taxable_detail["gross_salary_imposable"],
            "social_contributions_deductible": taxable_detail["social_contributions_deductible"],
            "income_before_professional_expenses": taxable_detail["income_before_professional_expenses"],
            "other_tax_deductions": taxable_detail["other_tax_deductions"],
            "taxable_income": taxable_after_family,
            "family_deduction": family_monthly,
            "ir_brut": ir_brut,
            "ir": ir,
            "other_deductions": other,
            "total_deductions": total_deductions,
            "net_salary": net,
            "allocations_familiales": employer["allocations_familiales"],
            "cnss_employer_short_term": employer["prestations_court_terme_employeur"],
            "cnss_employer_long_term": employer["prestations_long_terme_employeur"],
            "amo_employer": employer["amo_employeur"],
            "taxe_formation_professionnelle": employer["taxe_formation_professionnelle"],
            "cnss_employer": money(employer["allocations_familiales"] + employer["prestations_court_terme_employeur"] + employer["prestations_long_terme_employeur"]),
            "other_employer_costs": other_employer,
            "total_employer_charges": total_employer_charges,
            "total_employer_cost": money(gross + total_employer_charges),
            "debug": debug,
        }
