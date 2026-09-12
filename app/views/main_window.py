"""
Main application window for MEKPAIE.
"""
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QGraphicsOpacityEffect
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
from app.widgets.sidebar import Sidebar
from app.views.dashboard import Dashboard
from app.views.employees import Employees
from app.views.companies import Companies
from app.views.payroll import Payroll
from app.views.payslips import Payslips
from app.views.reports import Reports
from app.views.settings import Settings


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        """Initialize main window."""
        super().__init__()
        
        self.setWindowTitle("MEKPAIE - Gestion de paie professionnelle au Maroc")
        self.setGeometry(0, 0, 1400, 900)
        
        # Center window on screen
        screen = self.screen()
        if screen:
            screen_geometry = screen.geometry()
            x = (screen_geometry.width() - 1400) // 2
            y = (screen_geometry.height() - 900) // 2
            self.move(x, y)
        
        self.init_ui()
        self.apply_global_style()
        self._view_animation = None
    
    def init_ui(self):
        """Initialize UI."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = Sidebar()
        self.sidebar.dashboard_clicked.connect(self.show_dashboard)
        self.sidebar.employees_clicked.connect(self.show_employees)
        self.sidebar.companies_clicked.connect(self.show_companies)
        self.sidebar.payroll_clicked.connect(self.show_payroll)
        self.sidebar.payslips_clicked.connect(self.show_payslips)
        self.sidebar.reports_clicked.connect(self.show_reports)
        self.sidebar.settings_clicked.connect(self.show_settings)
        self.sidebar.backup_clicked.connect(self.show_backup)
        
        main_layout.addWidget(self.sidebar)
        
        # Content area - use a single stacked widget to hold all views
        self.content_stack = QStackedWidget()
        
        # Initialize views
        self.dashboard_view = Dashboard()
        self.employees_view = Employees()
        self.companies_view = Companies()
        self.payroll_view = Payroll()
        self.payslips_view = Payslips()
        self.reports_view = Reports()
        self.settings_view = Settings()
        
        # Add views to stack
        self.content_stack.addWidget(self.dashboard_view)
        self.content_stack.addWidget(self.employees_view)
        self.content_stack.addWidget(self.companies_view)
        self.content_stack.addWidget(self.payroll_view)
        self.content_stack.addWidget(self.payslips_view)
        self.content_stack.addWidget(self.reports_view)
        self.content_stack.addWidget(self.settings_view)
        
        self.content_stack.setStyleSheet("background-color: #f5f5f5;")
        
        main_layout.addWidget(self.content_stack, 1)
        
        central_widget.setLayout(main_layout)
        
        # Show dashboard by default
        self.show_dashboard()
    
    def show_dashboard(self):
        """Show dashboard view."""
        self._switch_view(self.dashboard_view)
        self.dashboard_view.refresh_data()
        self.sidebar.set_active_button(self.sidebar.dashboard_btn)
    
    def show_employees(self):
        """Show employees view."""
        self._switch_view(self.employees_view)
        self.employees_view.refresh_table()
        self.sidebar.set_active_button(self.sidebar.employees_btn)
    
    def show_companies(self):
        """Show companies view."""
        self._switch_view(self.companies_view)
        self.companies_view.refresh_table()
        self.sidebar.set_active_button(self.sidebar.companies_btn)
    
    def show_payroll(self):
        """Show payroll view."""
        self._switch_view(self.payroll_view)
        self.payroll_view.load_companies()
        self.sidebar.set_active_button(self.sidebar.payroll_btn)
    
    def show_payslips(self):
        """Show payslips view."""
        self._switch_view(self.payslips_view)
        self.payslips_view.refresh_table()
        self.sidebar.set_active_button(self.sidebar.payslips_btn)
    
    def show_reports(self):
        """Show reports view."""
        self._switch_view(self.reports_view)
        self.sidebar.set_active_button(self.sidebar.reports_btn)
    
    def show_settings(self):
        """Show settings view."""
        self._switch_view(self.settings_view)
        self.sidebar.set_active_button(self.sidebar.settings_btn)
    
    def show_backup(self):
        """Show backup view (settings)."""
        self.show_settings()
        self.sidebar.set_active_button(self.sidebar.backup_btn)

    def _switch_view(self, view):
        """Switch views with a subtle fade-in transition."""
        self.content_stack.setCurrentWidget(view)
        effect = QGraphicsOpacityEffect(view)
        view.setGraphicsEffect(effect)
        animation = QPropertyAnimation(effect, b"opacity", self)
        animation.setDuration(180)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.finished.connect(lambda: view.setGraphicsEffect(None))
        self._view_animation = animation
        animation.start()
    
    def apply_global_style(self):
        """Apply global stylesheet."""
        style = """
            QMainWindow, QWidget {
                background-color: #f6f8fb;
                color: #1f2937;
                font-family: "Segoe UI";
                font-size: 10pt;
            }
            QWidget#sidebar {
                background-color: #162636;
            }
            QMenuBar {
                background-color: #ffffff;
                border-bottom: 1px solid #d8e0e8;
            }
            QMenuBar::item:selected {
                background-color: #e7f5f3;
            }
            QMenu {
                background-color: #ffffff;
                color: #1f2937;
                border: 1px solid #d8e0e8;
            }
            QMenu::item:selected {
                background-color: #00a896;
                color: white;
            }
        """
        self.setStyleSheet(style)

