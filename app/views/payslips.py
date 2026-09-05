"""
Payslips history view for MEKPAIE.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTableWidget, QTableWidgetItem, QComboBox, QSpinBox, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl
from app.widgets import StyledButton, DataTable, ConfirmDialog, ErrorDialog, InfoDialog
from app.database import get_session
from app.models import Payroll, Employee, Payslip
from pathlib import Path
from datetime import datetime


class Payslips(QWidget):
    """Payslips history view."""
    
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
        title = QLabel("Historique des fiches de paie")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Search
        self.search = QLineEdit()
        self.search.setPlaceholderText("Rechercher par employé...")
        self.search.setMinimumWidth(250)
        self.search.textChanged.connect(self.filter_table)
        header_layout.addWidget(self.search)
        
        layout.addLayout(header_layout)
        
        # Filters
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Mois:"))
        self.month_filter = QComboBox()
        self.month_filter.addItems(["Tous"] + [
            "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
            "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
        ])
        self.month_filter.currentIndexChanged.connect(self.filter_table)
        filter_layout.addWidget(self.month_filter)
        
        filter_layout.addWidget(QLabel("Année:"))
        self.year_filter = QSpinBox()
        self.year_filter.setMinimum(2000)
        self.year_filter.setMaximum(2100)
        self.year_filter.setValue(datetime.now().year)
        self.year_filter.valueChanged.connect(self.filter_table)
        filter_layout.addWidget(self.year_filter)
        
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        # Table
        self.table = DataTable([
            "Date", "Employé", "Période", "Brut", "Retenues",
            "Net", "Généré", "Statut", "Actions"
        ])
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.table)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        self.view_btn = StyledButton("Voir détails", "primary")
        self.view_btn.clicked.connect(self.view_payroll)
        self.view_btn.setEnabled(False)
        
        self.open_pdf_btn = StyledButton("Ouvrir PDF", "primary")
        self.open_pdf_btn.clicked.connect(self.open_pdf)
        self.open_pdf_btn.setEnabled(False)
        
        self.print_btn = StyledButton("Imprimer", "primary")
        self.print_btn.clicked.connect(self.print_payslip)
        self.print_btn.setEnabled(False)
        
        self.delete_btn = StyledButton("Supprimer", "danger")
        self.delete_btn.clicked.connect(self.delete_payslip)
        self.delete_btn.setEnabled(False)
        
        action_layout.addWidget(self.view_btn)
        action_layout.addWidget(self.open_pdf_btn)
        action_layout.addWidget(self.print_btn)
        action_layout.addWidget(self.delete_btn)
        action_layout.addStretch()
        
        layout.addLayout(action_layout)
        
        self.setLayout(layout)
    
    def refresh_table(self):
        """Refresh payslips table."""
        try:
            session = get_session()
            payrolls = session.query(Payroll).all()
            
            self.table.setRowCount(len(payrolls))
            self.all_payrolls = payrolls
            
            for row, payroll in enumerate(payrolls):
                emp = payroll.employee
                month_names = ["", "Jan", "Fév", "Mar", "Avr", "Mai", "Jun",
                              "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"]
                
                self.table.setItem(row, 0, QTableWidgetItem(payroll.created_at.strftime("%d/%m/%Y")))
                self.table.setItem(row, 1, QTableWidgetItem(f"{emp.first_name} {emp.last_name}"))
                self.table.setItem(row, 2, QTableWidgetItem(f"{month_names[payroll.month]} {payroll.year}"))
                self.table.setItem(row, 3, QTableWidgetItem(f"{payroll.base_salary:,.2f}"))
                self.table.setItem(row, 4, QTableWidgetItem(f"{payroll.total_deductions:,.2f}"))
                self.table.setItem(row, 5, QTableWidgetItem(f"{payroll.net_taxable_salary:,.2f}"))
                
                pdf_status = "✓" if payroll.payslip and payroll.payslip.pdf_path else "✗"
                self.table.setItem(row, 6, QTableWidgetItem(pdf_status))
                self.table.setItem(row, 7, QTableWidgetItem(payroll.status))
                
                action_btn = QPushButton("...")
                self.table.setCellWidget(row, 8, action_btn)
            
            session.close()
        except Exception as e:
            ErrorDialog(self, message=f"Erreur: {str(e)}").exec()
    
    def filter_table(self):
        """Filter table by search and filters."""
        search_text = self.search.text().lower()
        month_filter = self.month_filter.currentIndex()
        year_filter = self.year_filter.value()
        
        for row in range(self.table.rowCount()):
            # Check search text
            show = False
            for col in range(8):
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    show = True
                    break
            
            # Check month filter
            if show and month_filter > 0:
                payroll = self.all_payrolls[row]
                show = payroll.month == month_filter
            
            # Check year filter
            if show:
                payroll = self.all_payrolls[row]
                show = payroll.year == year_filter
            
            self.table.setRowHidden(row, not show)
    
    def on_selection_changed(self):
        """Handle row selection."""
        rows = self.table.selectedIndexes()
        enabled = len(rows) > 0
        self.view_btn.setEnabled(enabled)
        self.open_pdf_btn.setEnabled(enabled)
        self.print_btn.setEnabled(enabled)
        self.delete_btn.setEnabled(enabled)
    
    def get_selected_payroll(self):
        """Get selected payroll."""
        rows = self.table.selectedIndexes()
        if rows:
            row = rows[0].row()
            return self.all_payrolls[row]
        return None
    
    def view_payroll(self):
        """View payroll details."""
        payroll = self.get_selected_payroll()
        if payroll:
            month_names = ["", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
                          "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
            
            emp = payroll.employee
            text = f"""
            BULLETIN DE PAIE
            
            Employé: {emp.first_name} {emp.last_name}
            Période: {month_names[payroll.month]} {payroll.year}
            
            ═══════════════════════════════════
            SALAIRE DE BASE
            ═══════════════════════════════════
            Salaire de base:        {payroll.base_salary:>10,.2f} DH
            
            ═══════════════════════════════════
            PRIMES (Non incluses dans le salaire)
            ═══════════════════════════════════
            Prime de salaire:       {payroll.salary_premium:>10,.2f} DH
            Prime de salaire:       {payroll.wage_premium:>10,.2f} DH
            Prime de transport:     {payroll.transport_premium:>10,.2f} DH
            
            ═══════════════════════════════════
            DÉDUCTIONS
            ═══════════════════════════════════
            CNSS (4.48%):           {payroll.cnss_employee:>10,.2f} DH
            AMO (2.26%):            {payroll.amo_employee:>10,.2f} DH
            ───────────────────────────────────
            TOTAL DÉDUCTIONS:       {payroll.total_deductions:>10,.2f} DH
            
            ═══════════════════════════════════
            NET IMPOSABLE:          {payroll.net_taxable_salary:>10,.2f} DH
            ═══════════════════════════════════
            """
            
            InfoDialog(self, title="Détails de la paie", message=text).exec()
    
    def open_pdf(self):
        """Open PDF payslip."""
        payroll = self.get_selected_payroll()
        if payroll and payroll.payslip and payroll.payslip.pdf_path:
            pdf_path = Path(payroll.payslip.pdf_path)
            if pdf_path.exists():
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(pdf_path)))
            else:
                ErrorDialog(self, message="Fichier PDF non trouvé").exec()
        else:
            ErrorDialog(self, message="Aucun PDF généré pour cette paie").exec()
    
    def print_payslip(self):
        """Print payslip."""
        payroll = self.get_selected_payroll()
        if payroll:
            InfoDialog(self, message="Fonctionnalité d'impression en développement").exec()
    
    def delete_payslip(self):
        """Delete payslip."""
        payroll = self.get_selected_payroll()
        if payroll:
            emp = payroll.employee
            dialog = ConfirmDialog(
                self,
                message=f"Êtes-vous sûr de vouloir supprimer la paie de {emp.first_name} {emp.last_name}?"
            )
            if dialog.exec() == QMessageBox.StandardButton.Yes:
                try:
                    session = get_session()
                    payroll_db = session.query(Payroll).get(payroll.id)
                    session.delete(payroll_db)
                    session.commit()
                    session.close()
                    
                    InfoDialog(self, message="Paie supprimée avec succès").exec()
                    self.refresh_table()
                except Exception as e:
                    ErrorDialog(self, message=f"Erreur: {str(e)}").exec()
