"""
Sidebar navigation widget for MEKPAIE.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy, QFrame
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
        self.setObjectName("sidebar")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 12)
        layout.setSpacing(0)
        
        # Header
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(18, 22, 18, 22)
        header_layout.setSpacing(5)
        
        app_name = QLabel("MEKPAIE")
        app_name.setFont(QFont("Segoe UI", 17, QFont.Weight.Bold))
        app_name.setStyleSheet("color: #ffffff; letter-spacing: 2px;")
        header_layout.addWidget(app_name)
        
        subtitle = QLabel("Gestion de paie")
        subtitle.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        subtitle.setStyleSheet("color: #8fa7ba; letter-spacing: 0.5px;")
        header_layout.addWidget(subtitle)

        header_rule = QFrame()
        header_rule.setFrameShape(QFrame.Shape.HLine)
        header_rule.setStyleSheet("color: #2d4356;")
        header_layout.addWidget(header_rule)
        
        header_widget = QWidget()
        header_widget.setLayout(header_layout)
        header_widget.setStyleSheet("background-color: #101b27; border-bottom: 1px solid #2a4053;")
        
        layout.addWidget(header_widget)
        
        # Navigation buttons
        nav_layout = QVBoxLayout()
        nav_layout.setContentsMargins(12, 16, 12, 16)
        nav_layout.setSpacing(4)

        nav_label = QLabel("ESPACE DE TRAVAIL")
        nav_label.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        nav_label.setStyleSheet("color: #7892a6; letter-spacing: 1px; padding: 0 10px 5px 10px;")
        nav_layout.addWidget(nav_label)
        
        self.dashboard_btn = self._create_nav_button("01   Tableau de bord", self.dashboard_clicked)
        self.employees_btn = self._create_nav_button("02   Employés", self.employees_clicked)
        self.companies_btn = self._create_nav_button("03   Entreprises", self.companies_clicked)
        self.payroll_btn = self._create_nav_button("04   Paie", self.payroll_clicked)
        self.payslips_btn = self._create_nav_button("05   Fiches de paie", self.payslips_clicked)
        self.reports_btn = self._create_nav_button("06   Rapports", self.reports_clicked)
        
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
        separator.setStyleSheet("background-color: #2b4255; min-height: 1px;")
        separator.setMaximumHeight(1)
        layout.addWidget(separator)
        
        # Settings section
        settings_layout = QVBoxLayout()
        settings_layout.setContentsMargins(12, 16, 12, 8)
        settings_layout.setSpacing(4)

        settings_label = QLabel("ADMINISTRATION")
        settings_label.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        settings_label.setStyleSheet("color: #7892a6; letter-spacing: 1px; padding: 0 10px 5px 10px;")
        settings_layout.addWidget(settings_label)
        
        self.settings_btn = self._create_nav_button("07   Paramètres", self.settings_clicked)
        self.backup_btn = self._create_nav_button("08   Sauvegarde", self.backup_clicked)
        
        settings_layout.addWidget(self.settings_btn)
        settings_layout.addWidget(self.backup_btn)
        
        settings_widget = QWidget()
        settings_widget.setLayout(settings_layout)
        layout.addWidget(settings_widget)

        status = QLabel("MODE LOCAL  |  2026")
        status.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        status.setStyleSheet("color: #6f899d; padding: 12px 18px 0 18px; letter-spacing: 0.6px;")
        layout.addWidget(status)
        
        # Spacer to push everything up
        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addSpacerItem(spacer)
        
        self.setLayout(layout)
        self.setStyleSheet("background-color: #162636;")
        self.setMinimumWidth(250)
        self.setMaximumWidth(250)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
    
    def _create_nav_button(self, text: str, signal):
        """Create a navigation button."""
        btn = QPushButton(text)
        btn.setFont(QFont("Arial", 10))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(signal)
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #c9d7e2;
                border: none;
                border-left: 3px solid transparent;
                border-radius: 5px;
                padding: 13px 12px;
                text-align: left;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #213a4e;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #29485e;
            }
        """)
        btn.setMinimumHeight(46)
        return btn
    
    def set_active_button(self, button):
        """Highlight the active navigation button."""
        # Reset all buttons
        for btn in [self.dashboard_btn, self.employees_btn, self.companies_btn,
                    self.payroll_btn, self.payslips_btn, self.reports_btn,
                    self.settings_btn, self.backup_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #c9d7e2;
                    border: none;
                    border-left: 3px solid transparent;
                    border-radius: 5px;
                    padding: 13px 12px;
                    text-align: left;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #213a4e;
                    color: #ffffff;
                }
                QPushButton:pressed {
                    background-color: #29485e;
                }
            """)
        
        # Highlight active button
        button.setStyleSheet("""
            QPushButton {
                background-color: #00a896;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 13px 12px;
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
