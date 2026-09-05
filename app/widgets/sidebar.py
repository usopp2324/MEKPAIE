"""
Sidebar navigation widget for MEKPAIE.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon


class Sidebar(QWidget):
    """Professional sidebar navigation widget."""
    
    # Signals for navigation
    dashboard_clicked = pyqtSignal()
    employees_clicked = pyqtSignal()
    companies_clicked = pyqtSignal()
    payroll_clicked = pyqtSignal()
    payslips_clicked = pyqtSignal()
    reports_clicked = pyqtSignal()
    settings_clicked = pyqtSignal()
    backup_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(15, 20, 15, 20)
        
        app_name = QLabel("MEKPAIE")
        app_name.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        app_name.setStyleSheet("color: #ffffff; letter-spacing: 1px;")
        header_layout.addWidget(app_name)
        
        subtitle = QLabel("Gestion de paie")
        subtitle.setFont(QFont("Segoe UI", 9))
        subtitle.setStyleSheet("color: #91a4b7;")
        header_layout.addWidget(subtitle)
        
        header_widget = QWidget()
        header_widget.setLayout(header_layout)
        header_widget.setStyleSheet("background-color: #111b26; border-bottom: 1px solid #263746;")
        
        layout.addWidget(header_widget)
        
        # Navigation buttons
        nav_layout = QVBoxLayout()
        nav_layout.setContentsMargins(0, 10, 0, 10)
        nav_layout.setSpacing(5)
        
        self.dashboard_btn = self._create_nav_button(" Tableau de bord", self.dashboard_clicked)
        self.employees_btn = self._create_nav_button(" Employés", self.employees_clicked)
        self.companies_btn = self._create_nav_button(" Entreprises", self.companies_clicked)
        self.payroll_btn = self._create_nav_button(" Paie", self.payroll_clicked)
        self.payslips_btn = self._create_nav_button(" Fiches de paie", self.payslips_clicked)
        self.reports_btn = self._create_nav_button(" Rapports", self.reports_clicked)
        
        nav_layout.addWidget(self.dashboard_btn)
        nav_layout.addWidget(self.employees_btn)
        nav_layout.addWidget(self.companies_btn)
        nav_layout.addWidget(self.payroll_btn)
        nav_layout.addWidget(self.payslips_btn)
        nav_layout.addWidget(self.reports_btn)
        
        nav_widget = QWidget()
        nav_widget.setLayout(nav_layout)
        layout.addWidget(nav_widget)
        
        # Separator
        separator = QWidget()
        separator.setStyleSheet("background-color: #2a3a49; min-height: 1px;")
        separator.setMaximumHeight(1)
        layout.addWidget(separator)
        
        # Settings section
        settings_layout = QVBoxLayout()
        settings_layout.setContentsMargins(0, 10, 0, 10)
        settings_layout.setSpacing(5)
        
        self.settings_btn = self._create_nav_button(" Paramètres", self.settings_clicked)
        self.backup_btn = self._create_nav_button(" Sauvegarde", self.backup_clicked)
        
        settings_layout.addWidget(self.settings_btn)
        settings_layout.addWidget(self.backup_btn)
        
        settings_widget = QWidget()
        settings_widget.setLayout(settings_layout)
        layout.addWidget(settings_widget)
        
        # Spacer to push everything up
        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer)
        
        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget {
                background-color: #34495e;
            }
        """)
        self.setMinimumWidth(220)
        self.setMaximumWidth(220)
    
    def _create_nav_button(self, text: str, signal):
        """Create a navigation button."""
        btn = QPushButton(text)
        btn.setFont(QFont("Arial", 10))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(signal)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #1b2a38;
                color: #dce6ee;
                border: none;
                border-left: 4px solid transparent;
                padding: 12px 15px;
                text-align: left;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #263b4d;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #304a5f;
            }
        """)
        btn.setMinimumHeight(45)
        return btn
    
    def set_active_button(self, button):
        """Highlight the active navigation button."""
        # Reset all buttons
        for btn in [self.dashboard_btn, self.employees_btn, self.companies_btn,
                    self.payroll_btn, self.payslips_btn, self.reports_btn,
                    self.settings_btn, self.backup_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1b2a38;
                    color: #dce6ee;
                    border: none;
                    border-left: 4px solid transparent;
                    padding: 12px 15px;
                    text-align: left;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #263b4d;
                    color: #ffffff;
                }
                QPushButton:pressed {
                    background-color: #304a5f;
                }
            """)
        
        # Highlight active button
        button.setStyleSheet("""
            QPushButton {
                background-color: #00a896;
                color: white;
                border: none;
                padding: 12px 15px;
                text-align: left;
                font-weight: bold;
                border-left: 4px solid #f4b942;
            }
            QPushButton:hover {
                background-color: #008f80;
            }
            QPushButton:pressed {
                background-color: #008f80;
            }
        """)
