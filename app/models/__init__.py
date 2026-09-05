"""
Database models for MEKPAIE application.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from app.database import Base


class Company(Base):
    """Company model."""
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    ice = Column(String(50), nullable=True)
    fiscal_id = Column(String(50), nullable=True)
    cnss = Column(String(50), nullable=True)
    address = Column(String(500), nullable=True)
    city = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(120), nullable=True)
    sector = Column(String(100), nullable=True)
    responsible = Column(String(255), nullable=True)
    logo_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employees = relationship("Employee", back_populates="company", cascade="all, delete-orphan")
    payrolls = relationship("Payroll", back_populates="company", cascade="all, delete-orphan")


class Employee(Base):
    """Employee model."""
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    matricule = Column(String(50), nullable=False, unique=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    cin = Column(String(50), nullable=True)
    cnss = Column(String(50), nullable=True)
    birth_date = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)
    marital_status = Column(String(50), nullable=True)
    children_count = Column(Integer, default=0)
    hire_date = Column(Date, nullable=True)
    position = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)
    contract_type = Column(String(50), nullable=True)
    categorie = Column(String(50), nullable=True)
    transport_premium_enabled = Column(Boolean, default=False)
    status = Column(String(50), default="Actif")
    base_salary = Column(Float, default=0.0)
    payment_method = Column(String(50), nullable=True)
    amo = Column(String(50), nullable=True)
    photo_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="employees")
    payrolls = relationship("Payroll", back_populates="employee", cascade="all, delete-orphan")


class Payroll(Base):
    """Payroll calculation model."""
    __tablename__ = "payrolls"
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    
    # Work input
    hours_or_days_worked = Column(Float, default=0.0)
    rate_per_unit = Column(Float, default=0.0)
    holiday_days_in_month = Column(Float, default=0.0)
    employee_worked_holiday_day = Column(Boolean, default=False)
    all_days_worked_without_absence = Column(Boolean, default=False)
    holiday_paid_days = Column(Float, default=0.0)
    holiday_unpaid_days = Column(Float, default=0.0)
    absence_justified = Column(String(255), nullable=True)
    absence_authorized = Column(String(255), nullable=True)
    absence_at = Column(String(255), nullable=True)
    absence_sickness = Column(String(255), nullable=True)
    
    # Earnings
    base_salary = Column(Float, default=0.0)
    holiday_paid_amount = Column(Float, default=0.0)
    leave_balance = Column(Float, default=0.0)
    overtime_hours_25 = Column(Float, default=0.0)
    overtime_hours_50 = Column(Float, default=0.0)
    overtime_amount_25 = Column(Float, default=0.0)
    overtime_amount_50 = Column(Float, default=0.0)
    overtime_amount = Column(Float, default=0.0)
    
    # Premiums (calculated but not added to salary)
    salary_premium = Column(Float, default=0.0)  # 8 DH per day
    wage_premium = Column(Float, default=0.0)    # 22.80 DH per day
    transport_premium = Column(Float, default=0.0)  # 19.00 DH per day
    
    # Deductions
    cnss_employee = Column(Float, default=0.0)  # 4.48% of base salary
    amo_employee = Column(Float, default=0.0)   # 2.26% of base salary
    total_deductions = Column(Float, default=0.0)
    
    # Net salary
    net_taxable_salary = Column(Float, default=0.0)  # base_salary - (CNSS + AMO)
    
    # Status and timestamps
    status = Column(String(50), default="Brouillon")  # Brouillon, Finalisé
    rules_version = Column(String(20), default="2026")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="payrolls")
    employee = relationship("Employee", back_populates="payrolls")
    payslip = relationship("Payslip", uselist=False, back_populates="payroll", cascade="all, delete-orphan")


class Payslip(Base):
    """Generated payslip model."""
    __tablename__ = "payslips"
    
    id = Column(Integer, primary_key=True)
    payroll_id = Column(Integer, ForeignKey("payrolls.id"), nullable=False, unique=True)
    pdf_path = Column(String(500), nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow)
    printed = Column(Boolean, default=False)
    printed_at = Column(DateTime, nullable=True)
    
    # Relationship
    payroll = relationship("Payroll", back_populates="payslip")


class Settings(Base):
    """Application settings model."""
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True)
    key = Column(String(100), nullable=False, unique=True)
    value = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
