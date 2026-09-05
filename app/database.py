"""
Database configuration and setup using SQLAlchemy ORM.
"""
from pathlib import Path
from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from app.paths import DATA_DIR

# Base class for all models
Base = declarative_base()

# Database path
DB_PATH = DATA_DIR
DB_PATH.mkdir(parents=True, exist_ok=True)
DB_FILE = DB_PATH / "MEKPAIE.db"

# Create database engine
def get_engine():
    """Create and return database engine."""
    engine = create_engine(
        f"sqlite:///{DB_FILE}",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    
    # Enable foreign keys for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    
    return engine

# Create session factory
engine = get_engine()
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

def _ensure_employee_columns():
    """Add any missing employee columns to an existing SQLite database."""
    try:
        inspector = inspect(engine)
        if 'employees' not in inspector.get_table_names():
            return

        columns = {col['name'] for col in inspector.get_columns('employees')}
        if 'transport_premium_enabled' not in columns:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE employees ADD COLUMN transport_premium_enabled BOOLEAN DEFAULT 0"))
    except Exception:
        # Ignore migration errors so startup can still proceed if the database is being rebuilt.
        pass


def _ensure_payroll_columns():
    """Add missing payroll columns introduced by newer rules (holiday days, checkboxes, etc.)."""
    try:
        inspector = inspect(engine)
        if 'payrolls' not in inspector.get_table_names():
            return

        columns = {col['name'] for col in inspector.get_columns('payrolls')}
        migrations = {
            'holiday_days_in_month': 'FLOAT DEFAULT 0.0',
            'employee_worked_holiday_day': 'BOOLEAN DEFAULT 0',
            'all_days_worked_without_absence': 'BOOLEAN DEFAULT 0',
            'holiday_paid_amount': 'FLOAT DEFAULT 0.0',
            'holiday_paid_days': 'FLOAT DEFAULT 0.0',
            'holiday_unpaid_days': 'FLOAT DEFAULT 0.0',
            'leave_balance': 'FLOAT DEFAULT 0.0',
            'absence_justified': 'VARCHAR(255)',
            'absence_authorized': 'VARCHAR(255)',
            'absence_at': 'VARCHAR(255)',
            'absence_sickness': 'VARCHAR(255)',
            'overtime_hours_25': 'FLOAT DEFAULT 0.0',
            'overtime_hours_50': 'FLOAT DEFAULT 0.0',
            'overtime_amount_25': 'FLOAT DEFAULT 0.0',
            'overtime_amount_50': 'FLOAT DEFAULT 0.0',
            'overtime_amount': 'FLOAT DEFAULT 0.0',
        }

        for column_name, ddl in migrations.items():
            if column_name not in columns:
                with engine.begin() as conn:
                    conn.execute(text(f"ALTER TABLE payrolls ADD COLUMN {column_name} {ddl}"))
    except Exception:
        # Ignore migration errors so startup can still proceed if the database is being rebuilt.
        pass


def init_db():
    """Initialize database tables and apply lightweight migrations."""
    Base.metadata.create_all(engine)
    _ensure_employee_columns()
    _ensure_payroll_columns()

def get_session():
    """Get a database session."""
    return SessionLocal()
