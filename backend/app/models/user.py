from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="Employee")  # Admin, HR, Employee
    is_active = Column(Boolean, default=True)

    # Relationship to the detailed profile
    employee_profile = relationship("Employee", back_populates="user", uselist=False)