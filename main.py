"""
MEKPAIE - Professional Payroll Management for Morocco
Main entry point of the application
"""
import sys
from pathlib import Path

# Add app directory to path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir.parent))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from app.database import init_db
from app.views.main_window import MainWindow


def main():
    """Main application entry point."""
    # Initialize database
    print("Initializing database...")
    init_db()
    print("Database ready")
    
    # Create application
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
