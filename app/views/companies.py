"""
Company management view for MEKPAIE.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTableWidget, QTableWidgetItem, QFormLayout, QDialog, QMessageBox,
    QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from app.widgets import StyledButton, FormDialog, DataTable, ConfirmDialog, ErrorDialog, InfoDialog
from app.database import get_session
from app.models import Company
from pathlib import Path
import shutil
from app.paths import LOGO_DIR


class CompanyDialog(FormDialog):
    """Dialog for adding/editing companies."""
    
    def __init__(self, parent=None, company=None):
        self.company = company
        super().__init__(parent, "Gestion d'entreprise" if company else "Ajouter une entreprise", 700, 550)
        if company:
            self.load_data()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        self.form_layout = QFormLayout()
        
        self.name = QLineEdit()
        self.ice = QLineEdit()
        self.fiscal_id = QLineEdit()
        self.cnss = QLineEdit()
        self.address = QLineEdit()
        self.city = QLineEdit()
        self.phone = QLineEdit()
        self.email = QLineEdit()
        self.sector = QLineEdit()
        self.responsible = QLineEdit()
        self.logo_path = QLineEdit()
        
        self.form_layout.addRow("Raison sociale:", self.name)
        self.form_layout.addRow("ICE:", self.ice)
        self.form_layout.addRow("Identifiant fiscal:", self.fiscal_id)
        self.form_layout.addRow("CNSS:", self.cnss)
        self.form_layout.addRow("Adresse:", self.address)
        self.form_layout.addRow("Ville:", self.city)
        self.form_layout.addRow("Téléphone:", self.phone)
        self.form_layout.addRow("Email:", self.email)
        self.form_layout.addRow("Secteur d'activité:", self.sector)
        self.form_layout.addRow("Responsable:", self.responsible)
        self.form_layout.addRow("Logo:", self.logo_path)
        
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
        
        logo_btn = StyledButton("Parcourir", "secondary")
        logo_btn.clicked.connect(self.browse_logo)
        
        save_btn = StyledButton("Enregistrer", "success")
        cancel_btn = StyledButton("Annuler", "secondary")
        
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(logo_btn)
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
    
    def browse_logo(self):
        """Browse for company logo."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner un logo",
            "",
            "Images PNG (*.png)"
        )
        if file_path:
            source = Path(file_path)
            if source.suffix.lower() != ".png":
                ErrorDialog(self, message="Le logo doit être au format PNG.").exec()
                return

            logo_dir = LOGO_DIR
            logo_dir.mkdir(parents=True, exist_ok=True)
            destination = logo_dir / source.name
            try:
                shutil.copy2(source, destination)
                self.logo_path.setText(str(destination))
            except OSError as error:
                ErrorDialog(self, message=f"Impossible d'enregistrer le logo: {error}").exec()
    
    def load_data(self):
        """Load company data into form."""
        if self.company:
            self.name.setText(self.company.name or "")
            self.ice.setText(self.company.ice or "")
            self.fiscal_id.setText(self.company.fiscal_id or "")
            self.cnss.setText(self.company.cnss or "")
            self.address.setText(self.company.address or "")
            self.city.setText(self.company.city or "")
            self.phone.setText(self.company.phone or "")
            self.email.setText(self.company.email or "")
            self.sector.setText(self.company.sector or "")
            self.responsible.setText(self.company.responsible or "")
            self.logo_path.setText(self.company.logo_path or "")
    
    def get_form_data(self) -> dict:
        """Get form data as dictionary."""
        return {
            "name": self.name.text(),
            "ice": self.ice.text(),
            "fiscal_id": self.fiscal_id.text(),
            "cnss": self.cnss.text(),
            "address": self.address.text(),
            "city": self.city.text(),
            "phone": self.phone.text(),
            "email": self.email.text(),
            "sector": self.sector.text(),
            "responsible": self.responsible.text(),
            "logo_path": self.logo_path.text(),
        }


class Companies(QWidget):
    """Company management view."""
    
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
        title = QLabel("Gestion des entreprises")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Search
        self.search = QLineEdit()
        self.search.setPlaceholderText("Rechercher par nom, ICE...")
        self.search.setMinimumWidth(250)
        self.search.textChanged.connect(self.filter_table)
        header_layout.addWidget(self.search)
        
        # Buttons
        add_btn = StyledButton("+ Ajouter", "success")
        add_btn.clicked.connect(self.add_company)
        header_layout.addWidget(add_btn)
        
        layout.addLayout(header_layout)
        
        # Table
        self.table = DataTable([
            "Raison sociale", "ICE", "IF", "CNSS",
            "Adresse", "Ville", "Téléphone", "Email", "Actions"
        ])
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.table)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        self.edit_btn = StyledButton("Modifier", "primary")
        self.edit_btn.clicked.connect(self.edit_company)
        self.edit_btn.setEnabled(False)
        
        self.delete_btn = StyledButton("Supprimer", "danger")
        self.delete_btn.clicked.connect(self.delete_company)
        self.delete_btn.setEnabled(False)
        
        action_layout.addWidget(self.edit_btn)
        action_layout.addWidget(self.delete_btn)
        action_layout.addStretch()
        
        layout.addLayout(action_layout)
        
        self.setLayout(layout)
    
    def refresh_table(self):
        """Refresh company table."""
        try:
            session = get_session()
            companies = session.query(Company).all()
            
            self.table.setRowCount(len(companies))
            self.all_companies = companies
            
            for row, company in enumerate(companies):
                self.table.setItem(row, 0, QTableWidgetItem(company.name or ""))
                self.table.setItem(row, 1, QTableWidgetItem(company.ice or ""))
                self.table.setItem(row, 2, QTableWidgetItem(company.fiscal_id or ""))
                self.table.setItem(row, 3, QTableWidgetItem(company.cnss or ""))
                self.table.setItem(row, 4, QTableWidgetItem(company.address or ""))
                self.table.setItem(row, 5, QTableWidgetItem(company.city or ""))
                self.table.setItem(row, 6, QTableWidgetItem(company.phone or ""))
                self.table.setItem(row, 7, QTableWidgetItem(company.email or ""))
                
                action_btn = QPushButton("...")
                self.table.setCellWidget(row, 8, action_btn)
            
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
    
    def get_selected_company(self):
        """Get selected company."""
        rows = self.table.selectedIndexes()
        if rows:
            row = rows[0].row()
            return self.all_companies[row]
        return None
    
    def add_company(self):
        """Add new company."""
        dialog = CompanyDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                session = get_session()
                data = dialog.get_form_data()
                
                # Check if company already exists
                existing = session.query(Company).filter(
                    Company.name == data['name']
                ).first()
                if existing:
                    ErrorDialog(self, message="Cette entreprise existe déjà").exec()
                    session.close()
                    return
                
                company = Company(**data)
                session.add(company)
                session.commit()
                session.close()
                
                InfoDialog(self, message="Entreprise ajoutée avec succès").exec()
                self.refresh_table()
            except Exception as e:
                ErrorDialog(self, message=f"Erreur: {str(e)}").exec()
    
    def edit_company(self):
        """Edit selected company."""
        company = self.get_selected_company()
        if company:
            dialog = CompanyDialog(self, company)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                try:
                    session = get_session()
                    company_db = session.query(Company).get(company.id)
                    data = dialog.get_form_data()

                    existing = session.query(Company).filter(
                        Company.name == data["name"], Company.id != company.id
                    ).first()
                    if existing:
                        session.close()
                        ErrorDialog(self, message="Cette entreprise existe déjà").exec()
                        return

                    if not data["name"].strip():
                        session.close()
                        ErrorDialog(self, message="La raison sociale est obligatoire").exec()
                        return
                    
                    for key, value in data.items():
                        setattr(company_db, key, value)
                    
                    session.commit()
                    session.close()
                    
                    InfoDialog(self, message="Entreprise modifiée avec succès").exec()
                    self.refresh_table()
                except Exception as e:
                    ErrorDialog(self, message=f"Erreur: {str(e)}").exec()
    
    def delete_company(self):
        """Delete selected company."""
        company = self.get_selected_company()
        if company:
            dialog = ConfirmDialog(
                self,
                message=f"Êtes-vous sûr de vouloir supprimer {company.name}?\nCela supprimera également tous les employés associés."
            )
            if dialog.exec() == QMessageBox.StandardButton.Yes:
                try:
                    session = get_session()
                    company_db = session.query(Company).get(company.id)
                    session.delete(company_db)
                    session.commit()
                    session.close()
                    
                    InfoDialog(self, message="Entreprise supprimée avec succès").exec()
                    self.refresh_table()
                except Exception as e:
                    ErrorDialog(self, message=f"Erreur: {str(e)}").exec()
