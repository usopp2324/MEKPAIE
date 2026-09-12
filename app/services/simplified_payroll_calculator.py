"""Simplified Moroccan payroll calculations for Morocco."""
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

CENT = Decimal("0.01")

# Default premium rates per day used when the employee record does not override them.
DEFAULT_SALARY_PREMIUM_PER_DAY = Decimal("8.00")
DEFAULT_WAGE_PREMIUM_PER_DAY = Decimal("22.80")
DEFAULT_TRANSPORT_PREMIUM_PER_DAY = Decimal("19.00")

# Contribution rates
CNSS_RATE = Decimal("0.0448")  # 4.48%
AMO_RATE = Decimal("0.0226")   # 2.26%

# Hours per day for conversion
HOURS_PER_DAY = Decimal("8")
HOURS_PER_MONTH = Decimal("208")  # 26 working days x 8 hours
WORKING_DAYS_PER_MONTH = Decimal("26")


def hourly_rate_from_base_salary(base_salary: Any) -> Decimal:
    """Convert a monthly base salary into an hourly rate using the business rule: /26/8."""
    base = money(base_salary)
    return money(base / WORKING_DAYS_PER_MONTH / HOURS_PER_DAY)


def money(value: Any) -> Decimal:
    """Convert a value to Decimal without floating-point artifacts."""
    return Decimal(str(value or 0)).quantize(CENT, rounding=ROUND_HALF_UP)


def years_of_service(hire_date: Any) -> int:
    """Return the number of completed years since hire date."""
    if not hire_date:
        return 0
    try:
        if hasattr(hire_date, "date"):
            hire_date = hire_date.date()
        if isinstance(hire_date, str):
            hire_date = date.fromisoformat(hire_date)
        if not isinstance(hire_date, date):
            return 0
        delta_days = (date.today() - hire_date).days
        if delta_days < 0:
            return 0
        return delta_days // 365
    except Exception:
        return 0


def seniority_percentage_for_years(years: int) -> Decimal:
    """Return the seniority increment percentage based on completed years of service."""
    if years < 2:
        return Decimal("0.00")
    if years < 5:
        return Decimal("0.05")
    if years < 12:
        return Decimal("0.10")
    if years < 20:
        return Decimal("0.15")
    if years < 25:
        return Decimal("0.20")
    return Decimal("0.25")


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
        absence_hours: Any = 0,
        absence_days: Any = None,
        salary_premium_per_day: Any = None,
        wage_premium_per_day: Any = None,
        transport_premium_per_day: Any = None,
        hire_date: Any = None,
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

        # Keep direct hourly-rate callers working while converting employee monthly
        # salaries before calculating hours worked x hourly rate.
        should_convert_to_hourly_rate = (
            rate > 0
            and category_name in {"horaire", "mensuel"}
            and rate >= Decimal("1000")
        )
        if should_convert_to_hourly_rate:
            rate = hourly_rate_from_base_salary(rate)

        holiday_days = money(holiday_days_in_month)
        paid_holiday_days = money(holiday_paid_days)
        worked_holiday_days = money(holiday_unpaid_days)
        absence_hours_count = money(absence_hours)
        if absence_days is not None:
            absence_hours_count = money(absence_days) * HOURS_PER_DAY
        absence_days_count = money(absence_hours_count / HOURS_PER_DAY)

        if category_name == "par jours":
            total_worked_days = hours_or_days
            real_days_worked = max(Decimal("0.00"), total_worked_days - absence_days_count)
            days_worked = real_days_worked
            base_salary = real_days_worked * rate
            daily_rate = rate
        else:
            days_worked = hours_or_days / HOURS_PER_DAY
            base_salary = hours_or_days * rate
            daily_rate = rate * HOURS_PER_DAY

        salary_premium_value = money(salary_premium_per_day) if salary_premium_per_day is not None else DEFAULT_SALARY_PREMIUM_PER_DAY
        wage_premium_value = money(wage_premium_per_day) if wage_premium_per_day is not None else DEFAULT_WAGE_PREMIUM_PER_DAY
        transport_premium_value = money(transport_premium_per_day) if transport_premium_per_day is not None else DEFAULT_TRANSPORT_PREMIUM_PER_DAY

        # Calculate premiums (not added to salary, just tracked)
        salary_premium = days_worked * salary_premium_value
        wage_premium = days_worked * wage_premium_value
        transport_premium = days_worked * transport_premium_value if include_transport_premium else Decimal("0.00")

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

        if category_name == "mensuel" and hours_or_days <= Decimal("31"):
            total_hours_worked = hours_or_days * HOURS_PER_DAY
        else:
            total_hours_worked = hours_or_days

        real_hours_worked = max(Decimal("0.00"), total_hours_worked - absence_hours_count)
        days_worked = real_hours_worked / HOURS_PER_DAY
        base_salary = real_hours_worked * rate

        regular_base_salary = money(base_salary)
        hourly_rate = money(regular_base_salary / max(real_hours_worked, Decimal("1.00")))
        seniority_years = years_of_service(hire_date)
        seniority_percentage = seniority_percentage_for_years(seniority_years)
        seniority_bonus_amount = money(regular_base_salary * seniority_percentage)
        effective_base_salary = money(regular_base_salary + money(holiday_paid_amount) + seniority_bonus_amount)

        if category_name == "horaire":
            overtime_hourly_rate = money(regular_base_salary / max(real_hours_worked, Decimal("1.00")))
        elif category_name == "par jours":
            overtime_hourly_rate = money(regular_base_salary / max(days_worked, Decimal("1.00")) / HOURS_PER_DAY)
        else:
            overtime_hourly_rate = money(regular_base_salary / max(real_hours_worked, Decimal("1.00")))
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
            "hourly_rate": hourly_rate,
            "base_salary": effective_base_salary,
            "days_worked": money(days_worked),
            "real_hours_worked": money(real_hours_worked),
            "salary_premium": money(salary_premium),
            "wage_premium": money(wage_premium),
            "transport_premium": money(transport_premium),
            "holiday_days_in_month": holiday_days,
            "holiday_paid_days": paid_holiday_days,
            "holiday_unpaid_days": worked_holiday_days,
            "employee_worked_holiday_day": bool(employee_worked_holiday_day),
            "all_days_worked_without_absence": bool(all_days_worked_without_absence),
            "absence_hours": absence_hours_count,
            "absence_days": absence_days_count,
            "holiday_paid_amount": money(holiday_paid_amount),
            "overtime_hours_25": overtime_25_hours,
            "overtime_hours_50": overtime_50_hours,
            "overtime_amount_25": overtime_amount_25,
            "overtime_amount_50": overtime_amount_50,
            "overtime_amount": overtime_amount,
            "leave_balance": money(leave_balance),
            "seniority_years": Decimal(seniority_years),
            "seniority_percentage": seniority_percentage,
            "seniority_bonus_amount": seniority_bonus_amount,
            "cnss_employee": cnss,
            "amo_employee": amo,
            "total_deductions": total_deductions,
            "net_taxable_salary": net_taxable_salary,
        }
