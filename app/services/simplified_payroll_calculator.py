"""Simplified Moroccan payroll calculations for Morocco."""
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

CENT = Decimal("0.01")

# Premium rates per day
SALARY_PREMIUM_PER_DAY = Decimal("8.00")
WAGE_PREMIUM_PER_DAY = Decimal("22.80")
TRANSPORT_PREMIUM_PER_DAY = Decimal("19.00")

# Contribution rates
CNSS_RATE = Decimal("0.0448")  # 4.48%
AMO_RATE = Decimal("0.0226")   # 2.26%

# Hours per day for conversion
HOURS_PER_DAY = Decimal("8")
HOURS_PER_MONTH = Decimal("176")


def money(value: Any) -> Decimal:
    """Convert a value to Decimal without floating-point artifacts."""
    return Decimal(str(value or 0)).quantize(CENT, rounding=ROUND_HALF_UP)


class SimplifiedPayrollCalculator:
    """Calculate payroll using simplified rules for Morocco."""
    
    def __init__(self, year: int = 2026):
        self.year = year
    
    def calculate_payroll(
        self,
        hours_or_days_worked: Any,
        rate_per_unit: Any,
        categorie: str = "Mensuel",
        include_transport_premium: bool = True,
        holiday_days_in_month: Any = 0,
        holiday_paid_days: Any = 0,
        holiday_unpaid_days: Any = 0,
        employee_worked_holiday_day: bool = False,
        all_days_worked_without_absence: bool = False,
        leave_balance: Any = 0,
        overtime_hours_25: Any = 0,
        overtime_hours_50: Any = 0,
    ) -> dict[str, Decimal]:
        """
        Calculate simplified payroll.

        Args:
            hours_or_days_worked: Number of hours or days worked
            rate_per_unit: Salary rate per hour/day/month
            categorie: Employee category (Horaire, Par jours, Mensuel, À la tâche)
            holiday_days_in_month: Number of paid holiday days in the month
            holiday_paid_days: Number of holidays that were not worked and are paid
            holiday_unpaid_days: Number of paid holidays that were worked
            employee_worked_holiday_day: True if the employee worked on a holiday day
            all_days_worked_without_absence: True only when the employee had no absences

        Returns:
            Dictionary with calculated payroll values
        """

        hours_or_days = money(hours_or_days_worked)
        rate = money(rate_per_unit)
        category_name = (categorie or "").lower()

        # If the employee is hourly, the entered rate is per hour and the working
        # quantity is already in hours. We still convert hours to days only for the
        # premium calculation, not for the base salary itself.
        if category_name == "horaire":
            days_worked = hours_or_days / HOURS_PER_DAY
            base_salary = hours_or_days * rate
            daily_rate = rate * HOURS_PER_DAY
        else:
            days_worked = hours_or_days
            base_salary = days_worked * rate
            daily_rate = rate

        # Calculate premiums (not added to salary, just tracked)
        salary_premium = days_worked * SALARY_PREMIUM_PER_DAY
        wage_premium = days_worked * WAGE_PREMIUM_PER_DAY
        transport_premium = days_worked * TRANSPORT_PREMIUM_PER_DAY if include_transport_premium else Decimal("0.00")

        holiday_days = money(holiday_days_in_month)
        paid_holiday_days = money(holiday_paid_days)
        worked_holiday_days = money(holiday_unpaid_days)

        # Keep supporting callers that only provide the former total and worked flag.
        if paid_holiday_days == 0 and worked_holiday_days == 0 and holiday_days > 0:
            if employee_worked_holiday_day:
                worked_holiday_days = holiday_days
            else:
                paid_holiday_days = holiday_days

        holiday_days = paid_holiday_days + worked_holiday_days
        holiday_paid_amount = (paid_holiday_days * daily_rate) + (
            worked_holiday_days * daily_rate * (
                Decimal("1.5") if all_days_worked_without_absence else Decimal("1")
            )
        )

        regular_base_salary = money(base_salary)
        effective_base_salary = regular_base_salary + money(holiday_paid_amount)

        if category_name == "horaire":
            overtime_hourly_rate = rate
        elif category_name == "par jours":
            overtime_hourly_rate = rate / HOURS_PER_DAY
        else:
            overtime_hourly_rate = rate / HOURS_PER_DAY
        overtime_25_hours = money(overtime_hours_25)
        overtime_50_hours = money(overtime_hours_50)
        overtime_amount_25 = money(overtime_25_hours * overtime_hourly_rate * Decimal("1.25"))
        overtime_amount_50 = money(overtime_50_hours * overtime_hourly_rate * Decimal("1.50"))
        overtime_amount = money(overtime_amount_25 + overtime_amount_50)
        effective_base_salary = money(effective_base_salary + overtime_amount)

        # Calculate contributions on the full salary, including overtime.
        cnss = money(effective_base_salary * CNSS_RATE)

        amo = money(effective_base_salary * AMO_RATE)

        # Total deductions
        total_deductions = money(cnss + amo)

        # Net taxable salary includes the paid holiday amount in the salary total
        net_taxable_salary = money(effective_base_salary - total_deductions)

        return {
            "regular_base_salary": regular_base_salary,
            "base_salary": effective_base_salary,
            "days_worked": money(days_worked),
            "salary_premium": money(salary_premium),
            "wage_premium": money(wage_premium),
            "transport_premium": money(transport_premium),
            "holiday_days_in_month": holiday_days,
            "holiday_paid_days": paid_holiday_days,
            "holiday_unpaid_days": worked_holiday_days,
            "employee_worked_holiday_day": bool(employee_worked_holiday_day),
            "all_days_worked_without_absence": bool(all_days_worked_without_absence),
            "holiday_paid_amount": money(holiday_paid_amount),
            "overtime_hours_25": overtime_25_hours,
            "overtime_hours_50": overtime_50_hours,
            "overtime_amount_25": overtime_amount_25,
            "overtime_amount_50": overtime_amount_50,
            "overtime_amount": overtime_amount,
            "leave_balance": money(leave_balance),
            "cnss_employee": cnss,
            "amo_employee": amo,
            "total_deductions": total_deductions,
            "net_taxable_salary": net_taxable_salary,
        }
