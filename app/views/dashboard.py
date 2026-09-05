"""
Dashboard view for MEKPAIE.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGridLayout, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from app.widgets import StatCard, StyledButton
from app.database import get_session
from app.models import Company, Employee, Payroll
from datetime import datetime, date


class Dashboard(QWidget):
    """Dashboard view showing overview statistics."""
    
    add_employee_clicked = pyqtSignal()
    calculate_payroll_clicked = pyqtSignal()
    generate_payslip_clicked = pyqtSignal()
    add_company_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.refresh_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Tableau de bord")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        
        # Stats cards
        stats_layout = QGridLayout()
        stats_layout.setSpacing(15)
        
        self.card_employees = StatCard("Employés actifs", "0", "")
        self.card_gross = StatCard("Salaire brut total", "0 DH", "Mois courant")
        self.card_deductions = StatCard("Total retenues", "0 DH", "")
        self.card_net = StatCard("Net à payer", "0 DH", "")
        
        stats_layout.addWidget(self.card_employees, 0, 0)
        stats_layout.addWidget(self.card_gross, 0, 1)
        stats_layout.addWidget(self.card_deductions, 0, 2)
        stats_layout.addWidget(self.card_net, 0, 3)
        
        layout.addLayout(stats_layout)
        
        # Quick actions
        actions_label = QLabel("Actions rapides")
        actions_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        actions_label.setStyleSheet("color: #2c3e50;")
        layout.addWidget(actions_label)
        
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(10)
        
        add_emp_btn = StyledButton("+ Ajouter employé", "success")
        add_emp_btn.clicked.connect(self.add_employee_clicked.emit)
        
        calc_payroll_btn = StyledButton("+ Calculer paie", "primary")
        calc_payroll_btn.clicked.connect(self.calculate_payroll_clicked.emit)
        
        gen_slip_btn = StyledButton("+ Générer fiche", "primary")
        gen_slip_btn.clicked.connect(self.generate_payslip_clicked.emit)
        
        add_company_btn = StyledButton("+ Ajouter entreprise", "secondary")
        add_company_btn.clicked.connect(self.add_company_clicked.emit)
        
        actions_layout.addWidget(add_emp_btn)
        actions_layout.addWidget(calc_payroll_btn)
        actions_layout.addWidget(gen_slip_btn)
        actions_layout.addWidget(add_company_btn)
        actions_layout.addStretch()
        
        layout.addLayout(actions_layout)
        
        # Recent activity section (placeholder)
        recent_label = QLabel("Activité récente")
        recent_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        recent_label.setStyleSheet("color: #2c3e50;")
        layout.addWidget(recent_label)
        
        self.recent_text = QLabel("Aucune activité récente")
        self.recent_text.setStyleSheet("color: #7f8c8d; padding: 20px;")
        layout.addWidget(self.recent_text)
        
        layout.addStretch()
        
        self.setLayout(layout)
    
    def refresh_data(self):
        """Refresh dashboard statistics."""
        try:
            session = get_session()
            
            # Count active employees
            active_employees = session.query(Employee).filter(
                Employee.status == "Actif"
            ).count()
            
            # Get current month payrolls
            now = datetime.now()
            current_payrolls = session.query(Payroll).filter(
                Payroll.year == now.year,
                Payroll.month == now.month
            ).all()
            
            # Calculate totals
            total_gross = sum(p.base_salary for p in current_payrolls) if current_payrolls else 0
            total_deductions = sum(p.total_deductions for p in current_payrolls) if current_payrolls else 0
            total_net = sum(p.net_taxable_salary for p in current_payrolls) if current_payrolls else 0
            
            # Update stat cards
            self.card_employees.set_value(str(active_employees))
            self.card_gross.set_value(f"{total_gross:,.2f} DH")
            self.card_deductions.set_value(f"{total_deductions:,.2f} DH")
            self.card_net.set_value(f"{total_net:,.2f} DH")
            
            session.close()
        except Exception as e:
            print(f"Erreur lors du rafraîchissement: {e}")
