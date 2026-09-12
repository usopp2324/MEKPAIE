"""
Settings and backup view for MEKPAIE.
"""
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QFormLayout, QFileDialog, QMessageBox, QLineEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from app.widgets import StyledButton, InfoDialog, ConfirmDialog, ErrorDialog
from app.services.backup_service import BackupService
from app.database import DB_FILE, get_session
from app.models import Settings as SettingsModel
from app.paths import PDF_DIR


class Settings(QWidget):
    """Settings and backup view."""
    
    def __init__(self):
        super().__init__()
        self.backup_service = BackupService()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Paramètres et maintenance")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        
        # Backup section
        backup_group = QGroupBox("Gestion des sauvegardes")
        backup_layout = QVBoxLayout()
        
        backup_info = QLabel(
            "Sauvegardez régulièrement votre base de données pour éviter la perte de données."
        )
        backup_info.setStyleSheet("color: #7f8c8d;")
        backup_layout.addWidget(backup_info)
        
        # Backup buttons
        button_layout = QHBoxLayout()
        
        create_backup_btn = StyledButton("Créer une sauvegarde", "success")
        create_backup_btn.clicked.connect(self.create_backup)
        
        restore_backup_btn = StyledButton("Restaurer une sauvegarde", "primary")
        restore_backup_btn.clicked.connect(self.restore_backup)
        
        button_layout.addWidget(create_backup_btn)
        button_layout.addWidget(restore_backup_btn)
        button_layout.addStretch()
        
        backup_layout.addLayout(button_layout)
        
        # Backup list
        self.backup_info_label = QLabel()
        self.backup_info_label.setStyleSheet("color: #7f8c8d; padding: 10px;")
        self.update_backup_list()
        backup_layout.addWidget(self.backup_info_label)
        
        backup_group.setLayout(backup_layout)
        layout.addWidget(backup_group)
        
        # Database section
        db_group = QGroupBox("Base de données")
        db_layout = QFormLayout()
        
        db_path = DB_FILE
        db_path_label = QLabel(f"Chemin: {db_path}")
        db_path_label.setStyleSheet("color: #2c3e50; font-family: monospace;")
        db_layout.addRow("Emplacement:", db_path_label)
        
        db_group.setLayout(db_layout)
        layout.addWidget(db_group)

        # Payslip output section
        pdf_group = QGroupBox("Emplacement des bulletins")
        pdf_layout = QFormLayout()

        pdf_path_layout = QHBoxLayout()
        self.pdf_path_edit = QLineEdit()
        self.pdf_path_edit.setReadOnly(True)
        self.pdf_path_edit.setToolTip("Dossier dans lequel les nouveaux bulletins PDF seront enregistrés")
        choose_pdf_path_btn = StyledButton("Choisir...", "primary")
        choose_pdf_path_btn.clicked.connect(self.choose_pdf_directory)
        pdf_path_layout.addWidget(self.pdf_path_edit, 1)
        pdf_path_layout.addWidget(choose_pdf_path_btn)
        pdf_layout.addRow("Dossier des PDF:", pdf_path_layout)

        pdf_info = QLabel("Les prochains bulletins seront enregistrés dans ce dossier.")
        pdf_info.setStyleSheet("color: #7f8c8d;")
        pdf_layout.addRow("", pdf_info)
        pdf_group.setLayout(pdf_layout)
        layout.addWidget(pdf_group)
        self.load_pdf_directory()
        
        # About section
        about_group = QGroupBox("À propos")
        about_layout = QFormLayout()
        
        about_text = QLabel("MEKPAIE v1.0.0 (Beta) \n\n Made By USOPP \n\n 2026")
        about_text.setStyleSheet("color: #7f8c8d;")
        about_layout.addRow(about_text)
        
        about_group.setLayout(about_layout)
        layout.addWidget(about_group)
        
        layout.addStretch()
        
        self.setLayout(layout)

    def load_pdf_directory(self):
        """Load the configured payslip directory, or show the default path."""
        path = PDF_DIR
        try:
            session = get_session()
            setting = session.query(SettingsModel).filter(
                SettingsModel.key == "pdf_directory"
            ).first()
            if setting and setting.value:
                path = Path(setting.value)
            session.close()
        except Exception:
            pass
        self.pdf_path_edit.setText(str(path))

    def choose_pdf_directory(self):
        """Choose and save the folder used for generated payslip PDFs."""
        selected_path = QFileDialog.getExistingDirectory(
            self,
            "Choisir le dossier des bulletins",
            self.pdf_path_edit.text() or str(PDF_DIR),
        )
        if not selected_path:
            return

        try:
            path = Path(selected_path)
            path.mkdir(parents=True, exist_ok=True)
            session = get_session()
            setting = session.query(SettingsModel).filter(
                SettingsModel.key == "pdf_directory"
            ).first()
            if setting:
                setting.value = str(path)
            else:
                session.add(SettingsModel(key="pdf_directory", value=str(path)))
            session.commit()
            session.close()
            self.pdf_path_edit.setText(str(path))
            InfoDialog(self, message=f"Dossier des bulletins enregistré:\n{path}").exec()
        except Exception as error:
            ErrorDialog(self, message=f"Impossible d'enregistrer ce dossier: {error}").exec()
    
    def create_backup(self):
        """Create a backup."""
        try:
            backup_path = self.backup_service.create_backup()
            self.update_backup_list()
            InfoDialog(
                self,
                title="Sauvegarde réussie",
                message=f"Sauvegarde créée avec succès:\n{backup_path}"
            ).exec()
        except Exception as e:
            ErrorDialog(self, message=f"Erreur: {str(e)}").exec()
    
    def restore_backup(self):
        """Restore from a backup."""
        try:
            backups = self.backup_service.list_backups()
            
            if not backups:
                ErrorDialog(self, message="Aucune sauvegarde trouvée").exec()
                return
            
            # Let user select backup file
            backup_path, _ = QFileDialog.getOpenFileName(
                self,
                "Sélectionner une sauvegarde",
                str(self.backup_service.backup_dir),
                "Database Files (*.db)"
            )
            
            if backup_path:
                # Confirm restore
                dialog = ConfirmDialog(
                    self,
                    message="Êtes-vous sûr? Cette action remplacera la base de données actuelle."
                )
                
                if dialog.exec() == QMessageBox.StandardButton.Yes:
                    self.backup_service.restore_backup(Path(backup_path))
                    self.update_backup_list()
                    InfoDialog(
                        self,
                        title="Restauration réussie",
                        message="Base de données restaurée avec succès"
                    ).exec()
        except Exception as e:
            ErrorDialog(self, message=f"Erreur: {str(e)}").exec()
    
    def update_backup_list(self):
        """Update backup list display."""
        try:
            backups = self.backup_service.list_backups()
            
            if not backups:
                self.backup_info_label.setText("Aucune sauvegarde disponible")
            else:
                text = "Sauvegardes disponibles:\n\n"
                for backup in backups[:5]:  # Show last 5
                    from datetime import datetime
                    mtime = datetime.fromtimestamp(backup.stat().st_mtime)
                    size_mb = backup.stat().st_size / (1024 * 1024)
                    text += f"• {backup.name}\n  {mtime.strftime('%d/%m/%Y %H:%M')} ({size_mb:.2f} MB)\n"
                
                self.backup_info_label.setText(text)
        except Exception as e:
            self.backup_info_label.setText(f"Erreur: {str(e)}")
