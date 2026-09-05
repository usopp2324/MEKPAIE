"""
UI Widgets and custom components for MEKPAIE.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTableWidget, QTableWidgetItem, QDialog, QFormLayout, QDateEdit,
    QComboBox, QSpinBox, QDoubleSpinBox, QMessageBox, QFileDialog,
    QDateEdit, QScrollArea
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QFont


class StatCard(QWidget):
    """Professional stat card widget."""
    
    def __init__(self, title: str, value: str, subtitle: str = "", icon_path: str = ""):
        super().__init__()
        self.title_label = None
        self.value_label = None
        self.subtitle_label = None
        self.init_ui(title, value, subtitle, icon_path)
    
    def init_ui(self, title: str, value: str, subtitle: str, icon_path: str):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # Title
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Normal))
        self.title_label.setStyleSheet("color: #64748b; font-weight: bold;")
        layout.addWidget(self.title_label)
        
        # Value
        self.value_label = QLabel(value)
        self.value_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        self.value_label.setStyleSheet("color: #102a43;")
        layout.addWidget(self.value_label)
        
        # Subtitle
        if subtitle:
            self.subtitle_label = QLabel(subtitle)
            self.subtitle_label.setFont(QFont("Segoe UI", 9))
            self.subtitle_label.setStyleSheet("color: #829ab1;")
            layout.addWidget(self.subtitle_label)
        
        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #d8e0e8;
            }
        """)
        self.setMinimumHeight(120)
    
    def set_value(self, value: str):
        """Update the card value."""
        if self.value_label:
            self.value_label.setText(value)
    
    def set_subtitle(self, subtitle: str):
        """Update the card subtitle."""
        if self.subtitle_label:
            self.subtitle_label.setText(subtitle)
        elif subtitle:
            # Create subtitle label if it doesn't exist
            self.subtitle_label = QLabel(subtitle)
            self.subtitle_label.setFont(QFont("Arial", 9))
            self.subtitle_label.setStyleSheet("color: #95a5a6;")
            self.layout().addWidget(self.subtitle_label)


class DataTable(QTableWidget):
    """Professional data table widget."""
    
    def __init__(self, columns: list):
        super().__init__()
        self.columns = columns
        self.init_ui()
    
    def init_ui(self):
        self.setColumnCount(len(self.columns))
        self.setHorizontalHeaderLabels(self.columns)
        self.horizontalHeader().setStretchLastSection(True)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True)
        self.setStyleSheet("""
            QTableWidget {
                background-color: white;
                gridline-color: #e5eaf0;
                border: 1px solid #d8e0e8;
            }
            QHeaderView::section {
                background-color: #102a43;
                color: white;
                padding: 5px;
                border: none;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #00a896;
                color: white;
            }
        """)


class FormDialog(QDialog):
    """Base form dialog for data entry."""
    
    def __init__(self, parent=None, title="Form", width=600, height=400):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setGeometry(100, 100, width, height)
        self.form_layout = QFormLayout()
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Scroll area for form
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_widget.setLayout(self.form_layout)
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        main_layout.addWidget(scroll)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Enregistrer")
        save_btn.setMinimumWidth(100)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        save_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setMinimumWidth(100)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 8px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
    
    def add_field(self, label: str, widget: QWidget):
        """Add a field to the form."""
        self.form_layout.addRow(label + ":", widget)
    
    def get_form_data(self) -> dict:
        """Override to return form data."""
        return {}


class StyledButton(QPushButton):
    """Styled button widget."""
    
    def __init__(self, text: str, color: str = "primary", parent=None):
        super().__init__(text, parent)
        self.set_style(color)
    
    def set_style(self, color: str):
        colors = {
            "primary": ("#00a896", "#008f80"),
            "success": ("#2f9e66", "#247a4e"),
            "danger": ("#d95d5d", "#b74343"),
            "warning": ("#e5a52f", "#bd8220"),
            "secondary": ("#607d94", "#486276"),
        }
        
        bg_color, hover_color = colors.get(color, colors["primary"])
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {hover_color};
            }}
        """)


class SectionLabel(QLabel):
    """Section header label."""
    
    def __init__(self, text: str):
        super().__init__(text)
        self.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.setStyleSheet("color: #2c3e50; margin-top: 10px; margin-bottom: 5px;")


class ConfirmDialog(QMessageBox):
    """Confirmation dialog."""
    
    def __init__(self, parent=None, title="Confirmation", message=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setText(message)
        # Avoid platform notification sounds while keeping the confirmation dialog.
        self.setIcon(QMessageBox.Icon.NoIcon)
        self.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        self.setDefaultButton(QMessageBox.StandardButton.No)


class InfoDialog(QMessageBox):
    """Information dialog."""
    
    def __init__(self, parent=None, title="Information", message=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setText(message)
        self.setIcon(QMessageBox.Icon.NoIcon)
        self.setStandardButtons(QMessageBox.StandardButton.Ok)


class ErrorDialog(QMessageBox):
    """Error dialog."""
    
    def __init__(self, parent=None, title="Erreur", message=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setText(message)
        self.setIcon(QMessageBox.Icon.NoIcon)
        self.setStandardButtons(QMessageBox.StandardButton.Ok)

