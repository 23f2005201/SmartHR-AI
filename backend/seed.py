import sys
import os
# Append the root path so python can find the app module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import date
from app.core.database import SessionLocal, Base, engine
# We must import all models here so SQLAlchemy knows what tables to build
from app.models.user import User
from app.models.department import Department
from app.models.employee import Employee
from app.models.attendance import Attendance
from app.models.leave import LeaveRequest
from app.core.security import get_password_hash

def seed_database():
    print("Initialising local database connections...")
    
    #FORCE CREATE ALL TABLES DIRECTLY
    Base.metadata.create_all(bind=engine)
    print("Database tables structurally verified and built.")

    db = SessionLocal()
    
    admin_exists = db.query(User).filter(User.email == "admin@smarthr.com").first()
    if admin_exists:
        print("Database has already been configured with an administrator account profile.")
        db.close()
        return

    print("Generating baseline administrative profile metadata...")
    
    admin_user = User(
        email="admin@smarthr.com",
        hashed_password=get_password_hash("AdminSecure2026!"),
        role="Admin",
        is_active=True
    )
    db.add(admin_user)
    db.flush()

    hr_department = Department(
        name="Human Resources",
        manager_id=admin_user.id
    )
    db.add(hr_department)
    db.flush()

    admin_employee = Employee(
        user_id=admin_user.id,
        first_name="Vimal",
        last_name="AVK",
        department_id=hr_department.id,
        joining_date=date(2026, 6, 10),
        salary=85000.00
    )
    db.add(admin_employee)
    
    db.commit()
    print("Successfully seeded database! Use credentials: admin@smarthr.com / AdminSecure2026!")
    db.close()

if __name__ == "__main__":
    seed_database()