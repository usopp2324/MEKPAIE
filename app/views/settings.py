"""
Settings and backup view for MEKPAIE.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QFormLayout, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from app.widgets import StyledButton, InfoDialog, ConfirmDialog, ErrorDialog
from app.services.backup_service import BackupService
from app.database import DB_FILE


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
        
        # About section
        about_group = QGroupBox("À propos")
        about_layout = QFormLayout()
        
        about_text = QLabel("MEKPAIE v1.0.0\n\nGestion de paie professionnelle au Maroc\n\n© 2026")
        about_text.setStyleSheet("color: #7f8c8d;")
        about_layout.addRow(about_text)
        
        about_group.setLayout(about_layout)
        layout.addWidget(about_group)
        
        layout.addStretch()
        
        self.setLayout(layout)
    
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
