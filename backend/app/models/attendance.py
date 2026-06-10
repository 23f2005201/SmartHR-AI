from sqlalchemy import Column, Integer, Date, Time, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    date = Column(Date, nullable=False)
    clock_in = Column(Time, nullable=True)
    clock_out = Column(Time, nullable=True)
    status = Column(String, default="Present")  # Present, Absent, Late, Half-day

    # Relationships
    employee = relationship("Employee", back_populates="attendance_records")