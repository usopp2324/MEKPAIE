from decimal import Decimal

from app.services.payroll_calculator import PayrollRulesMorocco
from app.views.payroll import sanitize_payroll_record_data


SALARIES = ("3000", "3102.27", "5000", "6000", "8000", "10000", "15000", "20000")


def test_employer_bases_and_amo_are_correct():
    calculator = PayrollRulesMorocco()
    for value in SALARIES:
        salary = Decimal(value)
        result = calculator.calculate_employer_contributions(salary)
        capped = min(salary, Decimal("6000.00"))
        assert result["amo_employeur"] == (salary * Decimal("0.0411")).quantize(Decimal("0.01"))
        assert result["prestations_court_terme_employeur"] == (capped * Decimal("0.0105")).quantize(Decimal("0.01"))
        assert result["prestations_long_terme_employeur"] == (capped * Decimal("0.0793")).quantize(Decimal("0.01"))


def test_required_3102_27_example():
    result = PayrollRulesMorocco().calculate_complete_payroll(
        Decimal("3000.00"), overtime_amount=Decimal("102.27")
    )
    assert result["gross_salary"] == Decimal("3102.27")
    assert result["amo_employer"] == Decimal("127.50")
    assert result["cnss_employee_short_term"] == Decimal("16.13")
    assert result["cnss_employee_long_term"] == Decimal("122.85")


def test_professional_expenses_are_not_salary_withholdings():
    result = PayrollRulesMorocco().calculate_complete_payroll(Decimal("3000"))
    assert result["professional_expenses"] == Decimal("1050.00")
    assert result["total_deductions"] == Decimal("202.20")
    assert result["net_salary"] == Decimal("2797.80")


def test_ir_is_progressive_and_monthly_annualized():
    calculator = PayrollRulesMorocco()
    assert calculator.calculate_ir_annual(Decimal("40000")) == Decimal("0.00")
    assert calculator.calculate_ir_annual(Decimal("60000")) == Decimal("2000.00")
    assert calculator.calculate_ir_monthly(Decimal("5000")) == Decimal("166.67")


def test_paid_holiday_rules_use_normal_and_increased_rates():
    from app.services.simplified_payroll_calculator import SimplifiedPayrollCalculator

    calculator = SimplifiedPayrollCalculator()

    normal_result = calculator.calculate_payroll(
        hours_or_days_worked=20,
        rate_per_unit=100,
        categorie="Horaire",
        holiday_paid_days=2,
        holiday_unpaid_days=1,
        employee_worked_holiday_day=True,
        all_days_worked_without_absence=True,
    )
    assert normal_result["regular_base_salary"] == Decimal("2000.00")
    assert normal_result["base_salary"] == Decimal("4800.00")
    assert normal_result["holiday_paid_amount"] == Decimal("2800.00")

    worked_result = calculator.calculate_payroll(
        hours_or_days_worked=20,
        rate_per_unit=100,
        categorie="Horaire",
        holiday_paid_days=2,
        holiday_unpaid_days=1,
        all_days_worked_without_absence=False,
    )
    assert worked_result["regular_base_salary"] == Decimal("2000.00")
    assert worked_result["base_salary"] == Decimal("4400.00")
    assert worked_result["holiday_paid_amount"] == Decimal("2400.00")

    daily_result = calculator.calculate_payroll(
        hours_or_days_worked=10,
        rate_per_unit=200,
        categorie="Par jours",
        holiday_paid_days=1,
        holiday_unpaid_days=1,
        all_days_worked_without_absence=True,
    )
    assert daily_result["holiday_paid_amount"] == Decimal("500.00")
    assert daily_result["holiday_days_in_month"] == Decimal("2.00")

    blocked_result = calculator.calculate_payroll(
        hours_or_days_worked=20,
        rate_per_unit=100,
        categorie="Horaire",
        holiday_days_in_month=2,
        employee_worked_holiday_day=True,
        all_days_worked_without_absence=False,
    )
    assert blocked_result["regular_base_salary"] == Decimal("2000.00")
    assert blocked_result["base_salary"] == Decimal("3600.00")
    assert blocked_result["holiday_paid_amount"] == Decimal("1600.00")


def test_leave_balance_is_preserved_in_payroll_result():
    from app.services.simplified_payroll_calculator import SimplifiedPayrollCalculator

    result = SimplifiedPayrollCalculator().calculate_payroll(
        hours_or_days_worked=20,
        rate_per_unit=100,
        categorie="Horaire",
        leave_balance=12.5,
    )

    assert result["leave_balance"] == Decimal("12.50")


def test_monthly_base_salary_is_converted_to_hourly_rate():
    from app.services.simplified_payroll_calculator import hourly_rate_from_base_salary

    assert hourly_rate_from_base_salary(Decimal("6000.00")) == Decimal("28.85")


def test_absence_days_reduce_worked_hours_before_salary_is_calculated():
    from app.services.simplified_payroll_calculator import SimplifiedPayrollCalculator

    result = SimplifiedPayrollCalculator().calculate_payroll(
        hours_or_days_worked=40,
        rate_per_unit=100,
        categorie="Horaire",
        absence_days=2,
    )

    assert result["absence_days"] == Decimal("2")
    assert result["real_hours_worked"] == Decimal("24.00")
    assert result["regular_base_salary"] == Decimal("2400.00")
    assert result["base_salary"] == Decimal("2400.00")


def test_hourly_category_still_uses_monthly_base_salary_conversion():
    from app.services.simplified_payroll_calculator import SimplifiedPayrollCalculator

    result = SimplifiedPayrollCalculator().calculate_payroll(
        hours_or_days_worked=176,
        rate_per_unit=3700,
        categorie="Horaire",
        absence_hours=8,
    )

    assert result["real_hours_worked"] == Decimal("168.00")
    assert result["regular_base_salary"] == Decimal("2988.72")
    assert result["base_salary"] == Decimal("2988.72")


def test_hourly_category_uses_hours_times_hourly_rate_for_short_month():
    from app.services.simplified_payroll_calculator import SimplifiedPayrollCalculator

    result = SimplifiedPayrollCalculator().calculate_payroll(
        hours_or_days_worked=40,
        rate_per_unit=3700,
        categorie="Horaire",
    )

    assert result["hourly_rate"] == Decimal("17.79")
    assert result["regular_base_salary"] == Decimal("711.60")


def test_monthly_category_converts_worked_days_to_hours_for_base_salary():
    from app.services.simplified_payroll_calculator import SimplifiedPayrollCalculator

    result = SimplifiedPayrollCalculator().calculate_payroll(
        hours_or_days_worked=26,
        rate_per_unit=3700,
        categorie="Mensuel",
    )

    assert result["real_hours_worked"] == Decimal("208.00")
    assert result["regular_base_salary"] == Decimal("3700.00")


def test_seniority_bonus_is_added_to_payroll_for_8_years_of_service():
    from datetime import date, timedelta
    from app.services.simplified_payroll_calculator import SimplifiedPayrollCalculator

    hire_date = date.today() - timedelta(days=8 * 365)
    result = SimplifiedPayrollCalculator().calculate_payroll(
        hours_or_days_worked=176,
        rate_per_unit=6000,
        categorie="Horaire",
        hire_date=hire_date,
    )

    assert result["seniority_years"] == 8
    assert result["seniority_percentage"] == Decimal("0.10")
    assert result["seniority_bonus_amount"] == Decimal("508.00")


def test_overtime_hours_are_paid_at_25_and_50_percent():
    from app.services.simplified_payroll_calculator import SimplifiedPayrollCalculator

    result = SimplifiedPayrollCalculator().calculate_payroll(
        hours_or_days_worked=160,
        rate_per_unit=100,
        categorie="Horaire",
        overtime_hours_25=4,
        overtime_hours_50=2,
    )

    assert result["overtime_amount_25"] == Decimal("500.00")
    assert result["overtime_amount_50"] == Decimal("300.00")
    assert result["overtime_amount"] == Decimal("800.00")
    assert result["base_salary"] == Decimal("16800.00")


def test_pdf_earnings_total_uses_regular_base_and_holiday_separately():
    from app.services.pdf_generator import PDFPayslipGenerator

    table = PDFPayslipGenerator()._create_earnings_section({
        "hours_or_days_worked": 21,
        "holiday_days_in_month": 1,
        "holiday_paid_amount": 152.80,
        "regular_base_salary": 3208.80,
        "base_salary": 3361.60,
        "rate_per_unit": 152.80,
    })[0]

    assert table._cellvalues[5][2] == "3208.80"
    assert table._cellvalues[6][2] == "3361.60"


def test_sanitize_payroll_record_data_removes_calculation_only_fields():
    payroll_data = {
        "regular_base_salary": Decimal("3208.80"),
        "base_salary": Decimal("3361.60"),
        "days_worked": Decimal("21.00"),
        "holiday_paid_amount": Decimal("152.80"),
        "employee_worked_holiday_day": True,
        "all_days_worked_without_absence": False,
        "year": 2026,
        "month": 9,
    }

    sanitized = sanitize_payroll_record_data(payroll_data)

    assert "regular_base_salary" not in sanitized
    assert "days_worked" not in sanitized
    assert "employee_worked_holiday_day" not in sanitized
    assert sanitized["base_salary"] == 3361.6
    assert sanitized["year"] == 2026
