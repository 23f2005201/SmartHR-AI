import sys
import os
from datetime import date, time, timedelta  # ✅ ADDED: imported 'time' object

# Append the root path so python can find the app module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, Base, engine
from app.models.user import User
from app.models.department import Department
from app.models.employee import Employee
from app.models.attendance import Attendance
from app.models.leave import LeaveRequest
from app.core.security import get_password_hash

def seed_database():
    print("Initialising local database connections...")
    Base.metadata.create_all(bind=engine)
    print("Database tables structurally verified and built.")

    db = SessionLocal()
    
    print("Flushing existing mock records to establish clean data arrays...")
    db.query(LeaveRequest).delete()
    db.query(Attendance).delete()
    db.query(Employee).delete()
    db.query(Department).delete()
    db.query(User).delete()
    db.commit()

    print("Generating baseline enterprise metadata...")
    
    # 1. Create Login Users for ALL Mock Personnel
    admin_user = User(
        email="admin@smarthr.com",
        hashed_password=get_password_hash("AdminSecure2026!"),
        role="Admin",
        is_active=True
    )
    hr_user = User(
        email="hr@smarthr.com",
        hashed_password=get_password_hash("HRSecure2026!"),
        role="HR",
        is_active=True
    )
    rahul_user = User(
        email="rahul@smarthr.com",
        hashed_password=get_password_hash("EmployeeSecure2026!"),
        role="Employee",
        is_active=True
    )
    priya_user = User(
        email="priya@smarthr.com",
        hashed_password=get_password_hash("EmployeeSecure2026!"),
        role="Employee",
        is_active=True
    )
    
    db.add_all([admin_user, hr_user, rahul_user, priya_user])
    db.flush()

    # 2. Setup Corporate Departments
    engineering_dept = Department(name="Engineering", manager_id=None)
    hr_dept = Department(name="Human Resources", manager_id=admin_user.id)
    db.add_all([engineering_dept, hr_dept])
    db.flush()

    # 3. Create Seed Employee Pool
    employees = [
        Employee(user_id=admin_user.id, first_name="Vimal", last_name="AVK", department_id=hr_dept.id, joining_date=date(2026, 1, 15), salary=95000.00),
        Employee(user_id=hr_user.id, first_name="Ananya", last_name="Sharma", department_id=hr_dept.id, joining_date=date(2026, 2, 1), salary=75000.00),
        Employee(user_id=rahul_user.id, first_name="Rahul", last_name="Verma", department_id=engineering_dept.id, joining_date=date(2025, 6, 10), salary=110000.00),
        Employee(user_id=priya_user.id, first_name="Priya", last_name="Nair", department_id=engineering_dept.id, joining_date=date(2026, 3, 20), salary=85000.00),
    ]
    db.add_all(employees)
    db.flush()

    # Set Rahul as the manager of Engineering
    engineering_dept.manager_id = employees[2].id
    db.flush()

    # 4. Generate ACTIVE Attendance Tracking Logs for today (Fills "Staff Clocked In Today")
    print("Seeding active attendance logs for today...")
    today = date.today()
    
    for emp in employees[:3]:
        attendance_record = Attendance(
            employee_id=emp.id,
            date=today,
            clock_in=time(9, 0, 0),  # ✅ FIXED: Now passing a clean python time object instead of a string
            clock_out=None,          # Active shift
            status="Present"
        )
        db.add(attendance_record)

    # 5. Generate Pending Leave Requests (Fills "Action Required" and Grid tables)
    print("Seeding active pending leave requests...")
    leave_fixtures = [
        LeaveRequest(
            employee_id=employees[2].id, 
            leave_type="Sick Leave", 
            start_date=today + timedelta(days=2), 
            end_date=today + timedelta(days=5), 
            status="Pending"
        ),
        LeaveRequest(
            employee_id=employees[3].id, 
            leave_type="Casual Leave", 
            start_date=today + timedelta(days=10), 
            end_date=today + timedelta(days=12), 
            status="Pending"
        )
    ]
    db.add_all(leave_fixtures)
    
    db.commit()
    print("\n" + "="*60)
    print(" 🎉 SUCCESS: Database seeded cleanly with schema-compliant profiles!")
    print(" Staff Clocked In Added: 3")
    print(" Pending Leaves Added: 2")
    print(" Credentials: admin@smarthr.com / AdminSecure2026!")
    print("="*60)
    db.close()

if __name__ == "__main__":
    seed_database()