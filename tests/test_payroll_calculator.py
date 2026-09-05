from decimal import Decimal

from app.services.payroll_calculator import PayrollRulesMorocco


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
