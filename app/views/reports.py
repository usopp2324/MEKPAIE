"""
Reports view for MEKPAIE.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QFont


class Reports(QWidget):
    """Reports view (placeholder)."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("Rapports et analyses")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        
        message = QLabel("Fonctionnalité en développement...\n\nVous pourrez générer des rapports:\n- Paie par mois\n- Totaux brut, net, retenues\n- Cotisations employeur\n- Statistiques d'effectifs")
        message.setStyleSheet("color: #7f8c8d; padding: 20px;")
        layout.addWidget(message)
        
        layout.addStretch()
        
        self.setLayout(layout)
