"""
Payroll calculation view for MEKPAIE.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QComboBox, QSpinBox, QDoubleSpinBox, QFormLayout, QMessageBox, QGroupBox, QCheckBox
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from app.widgets import StyledButton, FormDialog, ErrorDialog, InfoDialog
from app.database import get_session
from app.models import Company, Employee, Payroll as PayrollModel
from app.services.simplified_payroll_calculator import SimplifiedPayrollCalculator
from datetime import datetime


class PayrollResultDialog(QMessageBox):
    """Dialog showing simplified payroll calculation results."""
    
    def __init__(self, parent=None, payroll_data=None, employee=None, month=None, year=None):
        super().__init__(parent)
        self.payroll_data = payroll_data
        self.employee = employee
        self.month = month
        self.year = year
        self.setWindowTitle("Résultat de calcul de paie")
        self.set_content()
    
    def set_content(self):
        """Set the content of the dialog."""
        if not self.payroll_data:
            self.setText("Erreur: données de paie manquantes")
            return
        
        month_name = ["", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
                      "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"][self.month]
        
        holiday_amount = self.payroll_data.get('holiday_paid_amount', 0)
        holiday_label = ""
        if holiday_amount:
            holiday_label = f"\nFérié payé:             {holiday_amount:>10,.2f} DH"
        overtime_label = ""
        overtime_amount = self.payroll_data.get('overtime_amount', 0)
        if overtime_amount:
            overtime_label = (
                f"\nHeures sup. 25%: {self.payroll_data.get('overtime_hours_25', 0):>6,.2f} h"
                f" = {self.payroll_data.get('overtime_amount_25', 0):>10,.2f} DH"
                f"\nHeures sup. 50%: {self.payroll_data.get('overtime_hours_50', 0):>6,.2f} h"
                f" = {self.payroll_data.get('overtime_amount_50', 0):>10,.2f} DH"
            )

        text = f"""
        BULLETIN DE PAIE
        
        Employé: {self.employee.first_name} {self.employee.last_name}
        Période: {month_name} {self.year}
        
        ═══════════════════════════════════
        SALAIRE DE BASE
        ═══════════════════════════════════
        Jours travaillés:       {self.payroll_data['days_worked']:>10,.2f}
        Salaire de base:        {self.payroll_data['base_salary']:>10,.2f} DH
        {holiday_label}
        {overtime_label}
        
        ═══════════════════════════════════
        PRIMES (Non incluses dans le salaire)
        ═══════════════════════════════════
        Prime de salaire:       {self.payroll_data['salary_premium']:>10,.2f} DH
        Prime de salaire:       {self.payroll_data['wage_premium']:>10,.2f} DH
        Prime de transport:     {self.payroll_data['transport_premium']:>10,.2f} DH
        
        ═══════════════════════════════════
        DÉDUCTIONS
        ═══════════════════════════════════
        CNSS (4.48%):           {self.payroll_data['cnss_employee']:>10,.2f} DH
        AMO (2.26%):            {self.payroll_data['amo_employee']:>10,.2f} DH
        ───────────────────────────────────
        TOTAL DÉDUCTIONS:       {self.payroll_data['total_deductions']:>10,.2f} DH
        
        ═══════════════════════════════════
        NET IMPOSABLE:          {self.payroll_data['net_taxable_salary']:>10,.2f} DH
        ═══════════════════════════════════
        """
        
        self.setText(text)
        self.setFont(QFont("Courier New", 9))


class Payroll(QWidget):
    """Payroll calculation view."""
    
    def __init__(self):
        super().__init__()
        self.current_payroll_data = None
        self.current_employee_category = "Mensuel"
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Calcul de paie")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        
        # Selection section
        selection_group = QGroupBox("Sélection")
        selection_layout = QFormLayout()
        
        self.company_combo = QComboBox()
        self.employee_combo = QComboBox()
        self.month_spin = QSpinBox()
        self.month_spin.setMinimum(1)
        self.month_spin.setMaximum(12)
        self.month_spin.setValue(datetime.now().month)
        self.year_spin = QSpinBox()
        self.year_spin.setMinimum(2000)
        self.year_spin.setMaximum(2100)
        self.year_spin.setValue(datetime.now().year)
        
        self.company_combo.currentIndexChanged.connect(self.on_company_changed)
        self.employee_combo.currentIndexChanged.connect(self.on_employee_changed)
        
        selection_layout.addRow("Entreprise:", self.company_combo)
        selection_layout.addRow("Employé:", self.employee_combo)
        selection_layout.addRow("Mois:", self.month_spin)
        selection_layout.addRow("Année:", self.year_spin)
        
        selection_group.setLayout(selection_layout)
        layout.addWidget(selection_group)
        
        # Payroll input section
        input_group = QGroupBox("Éléments de paie")
        input_layout = QFormLayout()
        
        self.hours_or_days_worked = QDoubleSpinBox()
        self.hours_or_days_worked.setMinimum(0)
        self.hours_or_days_worked.setMaximum(999)
        self.hours_or_days_worked.setSingleStep(0.5)

        self.holiday_days_in_month = QSpinBox()
        self.holiday_days_in_month.setMinimum(0)
        self.holiday_days_in_month.setMaximum(31)

        self.holiday_paid_days = QSpinBox()
        self.holiday_paid_days.setMinimum(0)
        self.holiday_paid_days.setMaximum(31)

        self.holiday_unpaid_days = QSpinBox()
        self.holiday_unpaid_days.setMinimum(0)
        self.holiday_unpaid_days.setMaximum(31)

        self.overtime_hours_25 = QDoubleSpinBox()
        self.overtime_hours_25.setMinimum(0)
        self.overtime_hours_25.setMaximum(999)
        self.overtime_hours_25.setSingleStep(0.5)

        self.overtime_hours_50 = QDoubleSpinBox()
        self.overtime_hours_50.setMinimum(0)
        self.overtime_hours_50.setMaximum(999)
        self.overtime_hours_50.setSingleStep(0.5)

        self.leave_balance = QDoubleSpinBox()
        self.leave_balance.setMinimum(0)
        self.leave_balance.setMaximum(365)
        self.leave_balance.setSingleStep(0.5)

        self.absence_justified = QLineEdit()
        self.absence_authorized = QLineEdit()
        self.absence_at = QLineEdit()
        self.absence_sickness = QLineEdit()

        self.employee_worked_holiday_day = QCheckBox("L’employé a travaillé un jour férié")
        self.all_days_worked_without_absence = QCheckBox("Tous les jours travaillés sans absence")

        self.hours_label = QLabel("Heures travaillées:")

        input_layout.addRow(self.hours_label, self.hours_or_days_worked)
        input_layout.addRow("Jours fériés chômés payés:", self.holiday_paid_days)
        input_layout.addRow("Jours fériés non chômés payés:", self.holiday_unpaid_days)
        input_layout.addRow("Heures supplémentaires à 25%:", self.overtime_hours_25)
        input_layout.addRow("Heures supplémentaires à 50%:", self.overtime_hours_50)
        input_layout.addRow("Solde congés (jours):", self.leave_balance)
        input_layout.addRow("Absence justifiée:", self.absence_justified)
        input_layout.addRow("Absence autorisée:", self.absence_authorized)
        input_layout.addRow("AT:", self.absence_at)
        input_layout.addRow("Maladie:", self.absence_sickness)
        input_layout.addRow("", self.employee_worked_holiday_day)
        input_layout.addRow("", self.all_days_worked_without_absence)

        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        calculate_btn = StyledButton("Calculer", "success")
        calculate_btn.clicked.connect(self.calculate_payroll)
        
        save_btn = StyledButton("Enregistrer", "primary")
        save_btn.clicked.connect(self.save_payroll)
        
        pdf_btn = StyledButton("Générer PDF", "primary")
        pdf_btn.clicked.connect(self.generate_pdf)
        
        clear_btn = StyledButton("Réinitialiser", "secondary")
        clear_btn.clicked.connect(self.clear_form)
        
        button_layout.addWidget(calculate_btn)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(pdf_btn)
        button_layout.addWidget(clear_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        self.setLayout(layout)
        self.load_companies()
    
    def load_companies(self):
        """Load companies into combo box."""
        try:
            session = get_session()
            companies = session.query(Company).all()
            self.companies = companies
            
            self.company_combo.blockSignals(True)
            self.company_combo.clear()
            for company in companies:
                self.company_combo.addItem(company.name, company.id)
            self.company_combo.blockSignals(False)
            
            if companies:
                self.on_company_changed()
            
            session.close()
        except Exception as e:
            ErrorDialog(self, message=f"Erreur: {str(e)}").exec()
    
    def on_company_changed(self):
        """Load employees for selected company."""
        try:
            company_id = self.company_combo.currentData()
            if not company_id:
                return
            
            session = get_session()
            employees = session.query(Employee).filter(
                Employee.company_id == company_id
            ).all()
            
            self.employee_combo.blockSignals(True)
            self.employee_combo.clear()
            for emp in employees:
                self.employee_combo.addItem(
                    f"{emp.first_name} {emp.last_name}",
                    emp.id
                )
            self.employee_combo.blockSignals(False)
            
            if employees:
                self.on_employee_changed()
            
            session.close()
        except Exception as e:
            ErrorDialog(self, message=f"Erreur: {str(e)}").exec()
    
    def on_employee_changed(self):
        """Load employee category when employee is selected."""
        try:
            emp_id = self.employee_combo.currentData()
            if not emp_id:
                return
            
            session = get_session()
            emp = session.query(Employee).get(emp_id)
            if emp:
                # Store employee categorie for later use
                self.current_employee_category = emp.categorie or "Mensuel"
                category = (emp.categorie or "Mensuel").lower()
                if category == "horaire":
                    self.hours_label.setText("Heures travaillées:")
                elif category == "par jours":
                    self.hours_label.setText("Jours travaillés:")
                else:
                    self.hours_label.setText("Heures/Jours travaillés:")
            
            session.close()
        except Exception as e:
            ErrorDialog(self, message=f"Erreur: {str(e)}").exec()

    def _add_absence_data(self, payroll_data):
        """Copy optional absence entries while preserving blank fields."""
        payroll_data['absence_justified'] = self.absence_justified.text().strip()
        payroll_data['absence_authorized'] = self.absence_authorized.text().strip()
        payroll_data['absence_at'] = self.absence_at.text().strip()
        payroll_data['absence_sickness'] = self.absence_sickness.text().strip()
    
    def calculate_payroll(self):
        """Calculate payroll using simplified rules."""
        try:
            emp_id = self.employee_combo.currentData()
            if not emp_id:
                ErrorDialog(self, message="Veuillez sélectionner un employé").exec()
                return
            
            if self.hours_or_days_worked.value() == 0:
                ErrorDialog(self, message="Veuillez remplir les heures/jours travaillés").exec()
                return
            
            session = get_session()
            emp = session.query(Employee).get(emp_id)
            
            if not emp:
                ErrorDialog(self, message="Employé non trouvé").exec()
                session.close()
                return

            if not emp.base_salary:
                ErrorDialog(self, message="Veuillez renseigner le salaire par heure dans la fiche employé").exec()
                session.close()
                return
            
            # Create calculator
            calculator = SimplifiedPayrollCalculator(self.year_spin.value())
            
            # Calculate payroll
            self.current_payroll_data = calculator.calculate_payroll(
                hours_or_days_worked=self.hours_or_days_worked.value(),
                rate_per_unit=emp.base_salary,
                categorie=emp.categorie or "Mensuel",
                include_transport_premium=bool(emp.transport_premium_enabled),
                holiday_days_in_month=self.holiday_days_in_month.value(),
                holiday_paid_days=self.holiday_paid_days.value(),
                holiday_unpaid_days=self.holiday_unpaid_days.value(),
                employee_worked_holiday_day=self.employee_worked_holiday_day.isChecked(),
                all_days_worked_without_absence=self.all_days_worked_without_absence.isChecked(),
                leave_balance=self.leave_balance.value(),
                overtime_hours_25=self.overtime_hours_25.value(),
                overtime_hours_50=self.overtime_hours_50.value(),
            )
            self.current_payroll_data["holiday_paid_days"] = float(self.holiday_paid_days.value())
            self.current_payroll_data["holiday_unpaid_days"] = float(self.holiday_unpaid_days.value())
            self._add_absence_data(self.current_payroll_data)
            
            session.close()
            
            # Show result
            result_dialog = PayrollResultDialog(
                self,
                self.current_payroll_data,
                emp,
                self.month_spin.value(),
                self.year_spin.value()
            )
            result_dialog.exec()
            
        except Exception as e:
            ErrorDialog(self, message=f"Erreur: {str(e)}").exec()
    
    def save_payroll(self):
        """Save payroll calculation to database."""
        try:
            if not self.current_payroll_data:
                ErrorDialog(self, message="Veuillez d'abord calculer la paie").exec()
                return
            
            emp_id = self.employee_combo.currentData()
            company_id = self.company_combo.currentData()
            
            session = get_session()
            
            # Convert Decimal values to float and keep the holiday booleans as native bools.
            payroll_data = {
                key: float(value) for key, value in self.current_payroll_data.items()
                if key not in ['days_worked', 'regular_base_salary', 'employee_worked_holiday_day', 'all_days_worked_without_absence',
                               'absence_justified', 'absence_authorized', 'absence_at', 'absence_sickness']
            }
            payroll_data['employee_worked_holiday_day'] = bool(self.employee_worked_holiday_day.isChecked())
            payroll_data['all_days_worked_without_absence'] = bool(self.all_days_worked_without_absence.isChecked())
            payroll_data['holiday_paid_days'] = float(self.holiday_paid_days.value())
            payroll_data['holiday_unpaid_days'] = float(self.holiday_unpaid_days.value())
            payroll_data['leave_balance'] = float(self.leave_balance.value())
            self._add_absence_data(payroll_data)

            # Check if payroll already exists
            existing = session.query(PayrollModel).filter(
                PayrollModel.employee_id == emp_id,
                PayrollModel.company_id == company_id,
                PayrollModel.year == self.year_spin.value(),
                PayrollModel.month == self.month_spin.value()
            ).first()
            
            if existing:
                # Update existing
                for key, value in payroll_data.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
            else:
                # Create new
                payroll_data.update({
                    'company_id': company_id,
                    'employee_id': emp_id,
                    'year': self.year_spin.value(),
                    'month': self.month_spin.value(),
                    'hours_or_days_worked': self.hours_or_days_worked.value(),
                    'rate_per_unit': emp.base_salary,
                    'status': 'Finalisé',
                })
                payroll = PayrollModel(**payroll_data)
                session.add(payroll)
            
            session.commit()
            session.close()
            
            InfoDialog(self, message="Paie enregistrée avec succès").exec()
        except Exception as e:
            ErrorDialog(self, message=f"Erreur: {str(e)}").exec()
    
    def generate_pdf(self):
        """Generate PDF payslip."""
        try:
            if not self.current_payroll_data:
                ErrorDialog(self, message="Veuillez d'abord calculer la paie").exec()
                return
            
            emp_id = self.employee_combo.currentData()
            company_id = self.company_combo.currentData()
            
            session = get_session()
            
            emp = session.query(Employee).get(emp_id)
            company = session.query(Company).get(company_id)
            
            if not emp or not company:
                ErrorDialog(self, message="Données manquantes").exec()
                session.close()
                return
            
            # Convert Decimal to float for PDF generation
            payroll_data = {
                key: float(value) for key, value in self.current_payroll_data.items()
                if key not in ['days_worked', 'regular_base_salary', 'employee_worked_holiday_day', 'all_days_worked_without_absence',
                               'absence_justified', 'absence_authorized', 'absence_at', 'absence_sickness']
            }
            payroll_data['hours_or_days_worked'] = float(self.hours_or_days_worked.value())
            payroll_data['rate_per_unit'] = float(emp.base_salary or 0)
            payroll_data['holiday_days_in_month'] = float(self.holiday_days_in_month.value())
            payroll_data['holiday_paid_amount'] = float(self.current_payroll_data.get('holiday_paid_amount', 0))
            payroll_data['holiday_paid_days'] = float(self.holiday_paid_days.value())
            payroll_data['holiday_unpaid_days'] = float(self.holiday_unpaid_days.value())
            payroll_data['leave_balance'] = float(self.leave_balance.value())
            self._add_absence_data(payroll_data)
            payroll_data['employee_worked_holiday_day'] = bool(self.employee_worked_holiday_day.isChecked())
            payroll_data['all_days_worked_without_absence'] = bool(self.all_days_worked_without_absence.isChecked())
            
            # Save payroll first
            existing = session.query(PayrollModel).filter(
                PayrollModel.employee_id == emp_id,
                PayrollModel.company_id == company_id,
                PayrollModel.year == self.year_spin.value(),
                PayrollModel.month == self.month_spin.value()
            ).first()
            
            if not existing:
                payroll_data.update({
                    'company_id': company_id,
                    'employee_id': emp_id,
                    'year': self.year_spin.value(),
                    'month': self.month_spin.value(),
                    'hours_or_days_worked': self.hours_or_days_worked.value(),
                    'rate_per_unit': emp.base_salary,
                    'status': 'Finalisé',
                })
                payroll = PayrollModel(**payroll_data)
                session.add(payroll)
                session.commit()
                existing = payroll
            
            session.close()
            
            # Generate PDF
            from app.services.pdf_generator import PDFPayslipGenerator
            
            generator = PDFPayslipGenerator()
            
            company_info = {
                'name': company.name,
                'address': company.address,
                'phone': company.phone,
                'email': company.email,
                'ice': company.ice,
                'fiscal_id': company.fiscal_id,
                'cnss': company.cnss,
                'logo_path': company.logo_path,
            }
            
            employee_info = {
                'first_name': emp.first_name,
                'last_name': emp.last_name,
                'matricule': emp.matricule,
                'cin': emp.cin,
                'cnss': emp.cnss,
                'position': emp.position,
                'hire_date': emp.hire_date.strftime("%d/%m/%Y") if emp.hire_date else "",
                'categorie': emp.categorie or "Mensuel",
                'transport_premium_enabled': bool(emp.transport_premium_enabled),
                'marital_status': emp.marital_status or "Non spécifié",
                'children_count': emp.children_count or 0,
            }
            
            pdf_path = generator.generate_payslip(
                company_info,
                employee_info,
                payroll_data,
                self.month_spin.value(),
                self.year_spin.value()
            )
            
            InfoDialog(self, message=f"PDF généré avec succès:\n{pdf_path}").exec()
            
        except Exception as e:
            ErrorDialog(self, message=f"Erreur: {str(e)}").exec()
    
    def clear_form(self):
        """Clear the form."""
        self.hours_or_days_worked.setValue(0)
        self.holiday_days_in_month.setValue(0)
        self.holiday_paid_days.setValue(0)
        self.holiday_unpaid_days.setValue(0)
        self.overtime_hours_25.setValue(0)
        self.overtime_hours_50.setValue(0)
        self.leave_balance.setValue(0)
        self.absence_justified.clear()
        self.absence_authorized.clear()
        self.absence_at.clear()
        self.absence_sickness.clear()
        self.employee_worked_holiday_day.setChecked(False)
        self.all_days_worked_without_absence.setChecked(False)
        self.current_payroll_data = None
