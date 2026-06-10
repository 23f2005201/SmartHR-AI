from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    joining_date = Column(Date, nullable=False)
    salary = Column(Float, nullable=False)

    # Relationships
    user = relationship("User", back_populates="employee_profile")
    department = relationship("Department", back_populates="employees")
    attendance_records = relationship("Attendance", back_populates="employee")
    leave_requests = relationship("LeaveRequest", back_populates="employee")