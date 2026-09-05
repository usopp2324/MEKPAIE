# MEKPAIE - Gestion de Paie Professionnelle au Maroc

Professional payroll management application for Morocco, built with Python and PyQt6.

## Features

- 🏢 **Company Management** - Manage multiple companies with complete details
- 👥 **Employee Management** - Employee records with personal and professional information
- 💰 **Payroll Calculation** - Automatic Moroccan payroll calculations based on official rules
- 📄 **Professional PDF Payslips** - Generate beautiful, print-ready payslips
- 💾 **Database Backup & Restore** - Automated backup management
- 📊 **Payroll History** - Complete history of all payroll calculations
- 🔒 **Offline Operation** - Works completely offline with local SQLite database

## Technology Stack

- **Python 3.12+**
- **PyQt6** - Modern desktop GUI
- **SQLAlchemy** - Database ORM
- **SQLite** - Local database
- **ReportLab** - PDF generation

## Installation

### Windows Setup

1. **Install Python 3.12+**
   - Download from https://www.python.org/
   - Make sure to check "Add Python to PATH" during installation

2. **Create a virtual environment**
   ```powershell
   python -m venv venv
   venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```powershell
   python main.py
   ```

## Usage

### Quick Start

1. **Launch the application**
   ```
   python main.py
   ```

2. **Add a company** via the Companies tab
   - Enter company information (name, ICE, CNSS, etc.)
   - Optionally upload company logo

3. **Add employees** via the Employees tab
   - Fill in personal and professional information
   - Set base salary

4. **Calculate payroll**
   - Go to Paie tab
   - Select employee and month
   - Enter payroll elements (overtime, bonus, etc.)
   - Click "Calculer"

5. **Generate PDF**
   - After calculation, click "Générer PDF"
   - PDF is saved to `Documents\MEKPAIE\Bulletins\`

### Data Locations

- **Database**: `Documents\MEKPAIE\data\MEKPAIE.db`
- **PDF Payslips**: `Documents\MEKPAIE\Bulletins\`
- **Backups**: `Documents\MEKPAIE\Backups\`

### Create Backup

1. Go to Paramètres → Gestion des sauvegardes
2. Click "Créer une sauvegarde"
3. Backup is automatically saved in the Backups folder

### Restore Backup

1. Go to Paramètres → Gestion des sauvegardes
2. Click "Restaurer une sauvegarde"
3. Select backup file
4. Confirm restoration

## Building as Standalone EXE

### Using PyInstaller

1. Install PyInstaller
   ```
   pip install pyinstaller
   ```

2. Build executable
   ```powershell
   pyinstaller --noconfirm --windowed --name MEKPAIE main.py
   ```

3. Executable location: `dist\MEKPAIE\MEKPAIE.exe`

## Moroccan Payroll Rules (2026)

The application implements official Moroccan payroll calculations:

- **CNSS Employee**: 4.36%
- **CNSS Employer**: 8.33%
- **AMO Employee**: 2%
- **AMO Employer**: 8%
- **Professional Expenses**: 10% of gross salary
- **Income Tax (IR)**: Progressive brackets from 0% to 38%
- **Family Deduction**: 360 DH per dependent per year

All rules can be updated in `app/services/payroll_calculator.py`

## Project Structure

```
MEKPAIE/
├── main.py
├── requirements.txt
│
├── app/
│   ├── __init__.py
│   ├── database.py
│   ├── models/
│   │   └── __init__.py (Company, Employee, Payroll, etc.)
│   │
│   ├── services/
│   │   ├── payroll_calculator.py (Moroccan rules)
│   │   ├── pdf_generator.py (ReportLab)
│   │   └── backup_service.py
│   │
│   ├── views/
│   │   ├── main_window.py
│   │   ├── dashboard.py
│   │   ├── employees.py
│   │   ├── companies.py
│   │   ├── payroll.py
│   │   ├── payslips.py
│   │   ├── reports.py
│   │   └── settings.py
│   │
│   └── widgets/
│       ├── __init__.py (UI components)
│       └── sidebar.py
│
└── README.md
```

## Features Details

### Dashboard
- Overview statistics (employees, gross total, deductions, net total)
- Quick actions for common tasks
- Recent activity

### Employee Management
- Add/Edit/Delete employees
- Search and filter by name, matricule, etc.
- Detailed employee information
- Support for personal, professional, and social data

### Company Management
- Add/Edit/Delete companies
- Company logo management
- Multiple company support

### Payroll Calculation
- Automatic calculation based on Moroccan rules
- Support for overtime, bonuses, allowances
- Deduction calculations
- Tax calculations
- Employer contribution calculations

### PDF Generation
- Professional A4 payslips
- Company logo on payslips
- Complete payroll breakdown
- Ready-to-print format
- Stored in structured directory

### Payslip History
- View all calculated payslips
- Filter by month, year, employee
- View details of any payslip
- Open PDF files
- Delete payslips

## Error Handling

The application includes comprehensive error handling:
- Input validation for all forms
- Friendly error messages in French
- Confirmation dialogs for destructive actions
- Database integrity checks

## Security

- Passwords stored with bcrypt hashing (for future login feature)
- SQLite database with foreign key constraints
- Transaction-based operations for data integrity

## Future Enhancements

- [ ] User login system with roles
- [ ] Advanced reporting with Excel export
- [ ] Email integration for payslip distribution
- [ ] Arabic language support
- [ ] Multi-language interface
- [ ] Employee leave management
- [ ] Attendance tracking
- [ ] Bonus calculation templates

## Troubleshooting

### Database Issues
- Delete `Documents\MEKPAIE\data\MEKPAIE.db` to reset
- Use backup restore function

### Missing Dependencies
- Reinstall requirements: `pip install -r requirements.txt`

### PDF Generation Issues
- Ensure ReportLab is installed
- Check available disk space
- Verify PDF folder permissions

## Support

For issues or questions, check the error messages which are displayed in French.

## License

This application is provided for professional use in Morocco.

## Version

MEKPAIE v1.0.0

---

**Gestion de paie professionnelle au Maroc**
