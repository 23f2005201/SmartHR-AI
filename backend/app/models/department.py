from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    employees = relationship("Employee", back_populates="department")