from sqlalchemy import Column, Integer, Float, String, ForeignKey, Date
from app.core.database import Base

class PayrollRecord(Base):
    __tablename__ = "payroll_records"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    pay_period_start = Column(Date, nullable=False)
    pay_period_end = Column(Date, nullable=False)
    gross_salary = Column(Float, nullable=False)
    tax_deductions = Column(Float, nullable=False)
    net_salary = Column(Float, nullable=False)
    status = Column(String, default="Processed") # Processed, Paid, On-Hold