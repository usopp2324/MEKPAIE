"""
Employee management view for MEKPAIE.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTableWidget, QTableWidgetItem, QDateEdit, QComboBox, QSpinBox,
    QDoubleSpinBox, QFormLayout, QDialog, QMessageBox, QCheckBox
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from app.widgets import StyledButton, FormDialog, DataTable, ConfirmDialog, ErrorDialog, InfoDialog
from app.database import get_session
from app.models import Employee, Company
from datetime import datetime


class EmployeeDialog(FormDialog):
    """Dialog for adding/editing employees."""
    
    def __init__(self, parent=None, employee=None, company_id=None):
        self.employee = employee
        self.company_id = company_id
        super().__init__(parent, "Gestion d'employé" if employee else "Ajouter un employé", 700, 650)
        if employee:
            self.load_data()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Tabs/Sections
        self.form_layout = QFormLayout()
        
        # Personal info
        personal_label = QLabel("Informations personnelles")
        personal_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.form_layout.addRow(personal_label)
        
        self.matricule = QLineEdit()
        self.first_name = QLineEdit()
        self.last_name = QLineEdit()
        self.cin = QLineEdit()
        self.birth_date = QDateEdit()
        self.birth_date.setDate(QDate.currentDate())
        self.gender = QComboBox()
        self.gender.addItems(["Masculin", "Féminin"])
        self.marital_status = QComboBox()
        self.marital_status.addItems(["Célibataire", "Marié(e)", "Divorcé(e)", "Veuf(ve)"])
        self.children_count = QSpinBox()
        
        self.form_layout.addRow("Matricule:", self.matricule)
        self.form_layout.addRow("Nom:", self.last_name)
        self.form_layout.addRow("Prénom:", self.first_name)
        self.form_layout.addRow("CIN:", self.cin)
        self.form_layout.addRow("Date de naissance:", self.birth_date)
        self.form_layout.addRow("Sexe:", self.gender)
        self.form_layout.addRow("Situation familiale:", self.marital_status)
        self.form_layout.addRow("Nombre d'enfants:", self.children_count)
        
        # Professional info
        prof_label = QLabel("Informations professionnelles")
        prof_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.form_layout.addRow(prof_label)
        
        self.hire_date = QDateEdit()
        self.hire_date.setDate(QDate.currentDate())
        self.position = QLineEdit()
        self.department = QLineEdit()
        self.contract_type = QComboBox()
        self.contract_type.addItems(["CDI", "CDD", "Stage", "Freelance"])
        self.categorie = QComboBox()
        self.categorie.addItems(["Horaire", "Par jours", "Mensuel", "À la tâche"])
        self.transport_premium_enabled = QCheckBox("Autoriser la prime de transport")
        self.status = QComboBox()
        self.status.addItems(["Actif", "Inactif", "Congé", "Suspendu"])
        self.base_salary = QDoubleSpinBox()
        self.base_salary.setMinimum(0)
        self.base_salary.setMaximum(999999)
        self.base_salary.setSingleStep(100)
        self.payment_method = QComboBox()
        self.payment_method.addItems(["Virement", "Chèque", "Espèces"])
        
        self.form_layout.addRow("Date d'embauche:", self.hire_date)
        self.form_layout.addRow("Fonction:", self.position)
        self.form_layout.addRow("Département:", self.department)
        self.form_layout.addRow("Type de contrat:", self.contract_type)
        self.form_layout.addRow("Catégorie:", self.categorie)
        self.form_layout.addRow("Prime de transport:", self.transport_premium_enabled)
        self.form_layout.addRow("Statut:", self.status)
        self.form_layout.addRow("Salaire  par heure:", self.base_salary)
        self.form_layout.addRow("Mode de paiement:", self.payment_method)
        
        # Social info
        social_label = QLabel("Informations sociales")
        social_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.form_layout.addRow(social_label)
        
        self.cnss = QLineEdit()
        self.amo = QLineEdit()
        
        self.form_layout.addRow("Numéro CNSS:", self.cnss)
        self.form_layout.addRow("AMO:", self.amo)
        
        # Scroll area
        from PyQt6.QtWidgets import QScrollArea
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_widget.setLayout(self.form_layout)
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        main_layout.addWidget(scroll)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = StyledButton("Enregistrer", "success")
        cancel_btn = StyledButton("Annuler", "secondary")
        
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
    
    def load_data(self):
        """Load employee data into form."""
        if self.employee:
            self.matricule.setText(self.employee.matricule or "")
            self.first_name.setText(self.employee.first_name or "")
            self.last_name.setText(self.employee.last_name or "")
            self.cin.setText(self.employee.cin or "")
            self.birth_date.setDate(self.employee.birth_date or QDate.currentDate())
            self.gender.setCurrentText(self.employee.gender or "Masculin")
            self.marital_status.setCurrentText(self.employee.marital_status or "Célibataire")
            self.children_count.setValue(self.employee.children_count or 0)
            self.hire_date.setDate(self.employee.hire_date or QDate.currentDate())
            self.position.setText(self.employee.position or "")
            self.department.setText(self.employee.department or "")
            self.contract_type.setCurrentText(self.employee.contract_type or "CDI")
            self.categorie.setCurrentText(self.employee.categorie or "Mensuel")
            self.transport_premium_enabled.setChecked(bool(self.employee.transport_premium_enabled))
            self.status.setCurrentText(self.employee.status or "Actif")
            self.base_salary.setValue(self.employee.base_salary or 0)
            self.payment_method.setCurrentText(self.employee.payment_method or "Virement")
            self.cnss.setText(self.employee.cnss or "")
            self.amo.setText(self.employee.amo or "")
    
    def get_form_data(self) -> dict:
        """Get form data as dictionary."""
        return {
            "matricule": self.matricule.text(),
            "first_name": self.first_name.text(),
            "last_name": self.last_name.text(),
            "cin": self.cin.text(),
            "birth_date": self.birth_date.date().toPyDate() if self.birth_date.date() else None,
            "gender": self.gender.currentText(),
            "marital_status": self.marital_status.currentText(),
            "children_count": self.children_count.value(),
            "hire_date": self.hire_date.date().toPyDate() if self.hire_date.date() else None,
            "position": self.position.text(),
            "department": self.department.text(),
            "contract_type": self.contract_type.currentText(),
            "categorie": self.categorie.currentText(),
            "transport_premium_enabled": self.transport_premium_enabled.isChecked(),
            "status": self.status.currentText(),
            "base_salary": self.base_salary.value(),
            "payment_method": self.payment_method.currentText(),
            "cnss": self.cnss.text(),
            "amo": self.amo.text(),
        }


class Employees(QWidget):
    """Employee management view."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.refresh_table()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Gestion des employés")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Search
        self.search = QLineEdit()
        self.search.setPlaceholderText("Rechercher par nom, matricule...")
        self.search.setMinimumWidth(250)
        self.search.textChanged.connect(self.filter_table)
        header_layout.addWidget(self.search)
        
        # Buttons
        add_btn = StyledButton("+ Ajouter", "success")
        add_btn.clicked.connect(self.add_employee)
        header_layout.addWidget(add_btn)
        
        layout.addLayout(header_layout)
        
        # Table
        self.table = DataTable([
            "Matricule", "Nom", "Prénom", "CIN", "CNSS",
            "Fonction", "Département", "Salaire", "Statut", "Actions"
        ])
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.table)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        self.edit_btn = StyledButton("Modifier", "primary")
        self.edit_btn.clicked.connect(self.edit_employee)
        self.edit_btn.setEnabled(False)
        
        self.delete_btn = StyledButton("Supprimer", "danger")
        self.delete_btn.clicked.connect(self.delete_employee)
        self.delete_btn.setEnabled(False)
        
        self.payroll_btn = StyledButton("Calculer paie", "primary")
        self.payroll_btn.clicked.connect(self.calculate_payroll)
        self.payroll_btn.setEnabled(False)
        
        action_layout.addWidget(self.edit_btn)
        action_layout.addWidget(self.delete_btn)
        action_layout.addWidget(self.payroll_btn)
        action_layout.addStretch()
        
        layout.addLayout(action_layout)
        
        self.setLayout(layout)
    
    def refresh_table(self):
        """Refresh employee table."""
        try:
            session = get_session()
            employees = session.query(Employee).all()
            
            self.table.setRowCount(len(employees))
            self.all_employees = employees
            
            for row, emp in enumerate(employees):
                self.table.setItem(row, 0, QTableWidgetItem(emp.matricule or ""))
                self.table.setItem(row, 1, QTableWidgetItem(emp.last_name or ""))
                self.table.setItem(row, 2, QTableWidgetItem(emp.first_name or ""))
                self.table.setItem(row, 3, QTableWidgetItem(emp.cin or ""))
                self.table.setItem(row, 4, QTableWidgetItem(emp.cnss or ""))
                self.table.setItem(row, 5, QTableWidgetItem(emp.position or ""))
                self.table.setItem(row, 6, QTableWidgetItem(emp.department or ""))
                self.table.setItem(row, 7, QTableWidgetItem(f"{emp.base_salary:.2f}"))
                self.table.setItem(row, 8, QTableWidgetItem(emp.status or ""))
                
                # Action button
                action_btn = QPushButton("...")
                self.table.setCellWidget(row, 9, action_btn)
            
            session.close()
        except Exception as e:
            ErrorDialog(self, message=f"Erreur: {str(e)}").exec()
    
    def filter_table(self):
        """Filter table by search text."""
        search_text = self.search.text().lower()
        
        for row in range(self.table.rowCount()):
            show = False
            for col in range(self.table.columnCount() - 1):
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    show = True
                    break
            self.table.setRowHidden(row, not show)
    
    def on_selection_changed(self):
        """Handle row selection."""
        rows = self.table.selectedIndexes()
        enabled = len(rows) > 0
        self.edit_btn.setEnabled(enabled)
        self.delete_btn.setEnabled(enabled)
        self.payroll_btn.setEnabled(enabled)
    
    def get_selected_employee(self):
        """Get selected employee."""
        rows = self.table.selectedIndexes()
        if rows:
            row = rows[0].row()
            return self.all_employees[row]
        return None
    
    def add_employee(self):
        """Add new employee."""
        dialog = EmployeeDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                session = get_session()
                data = dialog.get_form_data()
                
                # Check if matricule already exists
                existing = session.query(Employee).filter(
                    Employee.matricule == data['matricule']
                ).first()
                if existing:
                    ErrorDialog(self, message="Ce matricule existe déjà").exec()
                    session.close()
                    return
                
                company = session.query(Company).order_by(Company.id).first()
                if not company:
                    session.close()
                    ErrorDialog(
                        self,
                        message="Veuillez d'abord ajouter une entreprise dans l'onglet Entreprises."
                    ).exec()
                    return

                emp = Employee(company_id=company.id, **data)
                session.add(emp)
                session.commit()
                session.close()
                
                InfoDialog(self, message="Employé ajouté avec succès").exec()
                self.refresh_table()
            except Exception as e:
                ErrorDialog(self, message=f"Erreur: {str(e)}").exec()
    
    def edit_employee(self):
        """Edit selected employee."""
        emp = self.get_selected_employee()
        if emp:
            dialog = EmployeeDialog(self, emp)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                try:
                    session = get_session()
                    emp_db = session.query(Employee).get(emp.id)
                    data = dialog.get_form_data()
                    
                    for key, value in data.items():
                        setattr(emp_db, key, value)
                    
                    session.commit()
                    session.close()
                    
                    InfoDialog(self, message="Employé modifié avec succès").exec()
                    self.refresh_table()
                except Exception as e:
                    ErrorDialog(self, message=f"Erreur: {str(e)}").exec()
    
    def delete_employee(self):
        """Delete selected employee."""
        emp = self.get_selected_employee()
        if emp:
            dialog = ConfirmDialog(
                self,
                message=f"Êtes-vous sûr de vouloir supprimer {emp.first_name} {emp.last_name}?"
            )
            if dialog.exec() == QMessageBox.StandardButton.Yes:
                try:
                    session = get_session()
                    emp_db = session.query(Employee).get(emp.id)
                    session.delete(emp_db)
                    session.commit()
                    session.close()
                    
                    InfoDialog(self, message="Employé supprimé avec succès").exec()
                    self.refresh_table()
                except Exception as e:
                    ErrorDialog(self, message=f"Erreur: {str(e)}").exec()
    
    def calculate_payroll(self):
        """Calculate payroll for selected employee."""
        emp = self.get_selected_employee()
        if emp:
            # This will be handled by the main window
            pass
