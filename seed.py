"""Demo data loader for the EMS prototype.

Usage (virtual environment activated, inside the project folder):

    python seed.py

It creates the database, the three fixed shift types, three login accounts and
ten employees (including two part-time employees on 4- and 3-day weeks), then
builds a realistic weekly schedule for the current week so every screen has
content for the demonstration.

Logins:  hr / hr123        HR administrator
         manager / manager123   Supervisor / Manager
         employee / emp123      Ordinary Employee (EMP-0001)
"""

from datetime import date, timedelta

from app import create_app
from app.extensions import db
from app.models import (
    Attendance,
    Employee,
    LeaveRequest,
    Schedule,
    ShiftPreference,
    User,
)
from app.security import ROLE_EMPLOYEE, ROLE_HR, ROLE_MANAGER
from app.services import (
    bootstrap_database,
    iso_week_key,
    set_working_days,
    shift_map,
    week_days,
    week_start,
)

EMPLOYEES = [
    # employee_id, name, gender, phone, email, department, position, type,
    # hire_date, wage_type, rate, working_days (None = Mon-Fri), account
    ("EMP-0001", "Li Wei", "MALE", "138-0000-0001", "li.wei@meiti-mall.cn",
     "Front Desk", "Service Associate", "FULL_TIME", "2026-08-01", "MONTHLY", None, None, "employee"),
    ("EMP-0002", "Wang Fang", "FEMALE", "138-0000-0002", "wang.fang@meiti-mall.cn",
     "Sales", "Sales Associate", "FULL_TIME", "2026-08-01", "MONTHLY", None, None, None),
    ("EMP-0003", "Zhang Min", "FEMALE", "138-0000-0003", "zhang.min@meiti-mall.cn",
     "Sales", "Senior Sales Associate", "FULL_TIME", "2026-07-15", "MONTHLY", None, None, None),
    ("EMP-0004", "Chen Jie", "MALE", "138-0000-0004", "chen.jie@meiti-mall.cn",
     "Logistics", "Stock Assistant", "PART_TIME", "2026-09-01", "HOURLY", 22.0, [0, 2, 4, 6], None),
    ("EMP-0005", "Liu Yang", "MALE", "138-0000-0005", "liu.yang@meiti-mall.cn",
     "Front Desk", "Cashier", "FULL_TIME", "2026-08-10", "MONTHLY", None, None, None),
    ("EMP-0006", "Xu Lan", "FEMALE", "138-0000-0006", "xu.lan@meiti-mall.cn",
     "Administration", "Administrative Assistant", "PART_TIME", "2026-09-05", "HOURLY", 25.0, [1, 3, 5], None),
    ("EMP-0007", "Ma Chao", "MALE", "138-0000-0007", "ma.chao@meiti-mall.cn",
     "Security", "Security Officer", "FULL_TIME", "2026-08-01", "MONTHLY", None, None, None),
    ("EMP-0008", "Sun Yu", "FEMALE", "138-0000-0008", "sun.yu@meiti-mall.cn",
     "Sales", "Sales Associate", "FULL_TIME", "2026-08-20", "MONTHLY", None, None, None),
    ("EMP-0009", "Guo Peng", "MALE", "138-0000-0009", "guo.peng@meiti-mall.cn",
     "Logistics", "Logistics Assistant", "PART_TIME", "2026-09-12", "HOURLY", 21.0, [0, 1, 3, 5], None),
    ("EMP-0010", "He Xin", "FEMALE", "138-0000-0010", "he.xin@meiti-mall.cn",
     "Front Desk", "Service Associate", "FULL_TIME", "2026-08-01", "MONTHLY", None, None, None),
]

# A deterministic rotation so the generated roster looks like a real one.
ROTATION = ["EARLY", "MID", "LATE"]


def seed_users():
    accounts = [
        ("hr", "hr123", ROLE_HR, "HR Administrator"),
        ("manager", "manager123", ROLE_MANAGER, "Store Manager"),
        ("employee", "emp123", ROLE_EMPLOYEE, "Li Wei"),
    ]
    for username, password, role, display_name in accounts:
        user = User.query.filter_by(username=username).first()
        if user is None:
            user = User(username=username, role=role, display_name=display_name)
            user.set_password(password)
            db.session.add(user)
        else:
            user.role = role
            user.display_name = display_name
            if not user.password_hash:
                user.set_password(password)
    db.session.commit()


def seed_employees():
    for (employee_id, full_name, gender, phone, email, department, position,
         employment_type, hire_date, wage_type, rate, working_days, account) in EMPLOYEES:
        employee = Employee.query.filter_by(employee_id=employee_id).first()
        if employee is None:
            employee = Employee(
                employee_id=employee_id,
                full_name=full_name,
                gender=gender,
                phone=phone,
                email=email,
                address="Zhengzhou, Henan, China",
                emergency_contact_name=f"{full_name.split()[0]} contact",
                emergency_contact_phone="139-0000-0000",
                department=department,
                position=position,
                employment_type=employment_type,
                hire_date=hire_date,
                wage_type=wage_type,
                hourly_rate=rate,
                is_active=True,
            )
            db.session.add(employee)
            db.session.flush()
        set_working_days(employee, working_days or [0, 1, 2, 3, 4])

        if account:
            user = User.query.filter_by(username=account).first()
            if user is not None and user.employee is None:
                user.employee = employee
    db.session.commit()


def seed_schedule(weeks=(0, 1)):
    """Fill the given week offsets (0 = current week) with a rotating roster."""
    templates = shift_map()
    employees = Employee.query.order_by(Employee.employee_id).all()
    created = 0

    for offset in weeks:
        start = week_start(date.today()) + timedelta(days=7 * offset)
        for index, employee in enumerate(employees):
            allowed = employee.working_day_numbers
            for position, day in enumerate(week_days(start)):
                if day.weekday() not in allowed:
                    continue
                if Schedule.query.filter_by(employee_id=employee.id, work_date=day.isoformat()).first():
                    continue
                code = ROTATION[(index + position) % len(ROTATION)]
                db.session.add(
                    Schedule(
                        employee_id=employee.id,
                        shift_template_id=templates[code].id,
                        work_date=day.isoformat(),
                        iso_week=iso_week_key(day),
                    )
                )
                created += 1
    db.session.commit()
    return created


def seed_attendance_and_leave():
    employees = Employee.query.order_by(Employee.employee_id).all()
    today = date.today()
    start = week_start(today)
    templates = shift_map()

    created_attendance = 0
    for offset in range(0, 3):  # today, yesterday, two days ago
        day = today - timedelta(days=offset)
        for employee in employees:
            if Schedule.query.filter_by(employee_id=employee.id, work_date=day.isoformat()).first() is None:
                continue
            if Attendance.query.filter_by(employee_id=employee.id, work_date=day.isoformat()).first():
                continue
            from datetime import datetime, timezone

            stamp = datetime.now(timezone.utc).astimezone().replace(hour=8, minute=55 + offset)
            db.session.add(
                Attendance(
                    employee_id=employee.id,
                    work_date=day.isoformat(),
                    check_in_at=stamp.isoformat(timespec="seconds"),
                    check_in_method="MANUAL_ON_DUTY",
                    note="demo data",
                )
            )
            created_attendance += 1

    # A pending leave request and one already approved request.
    if LeaveRequest.query.count() == 0 and len(employees) >= 6:
        db.session.add(
            LeaveRequest(
                employee_id=employees[2].id,
                start_date=(start + timedelta(days=9)).isoformat(),
                end_date=(start + timedelta(days=10)).isoformat(),
                reason="Family matter — travelling to Luoyang.",
                status="PENDING",
            )
        )
        db.session.add(
            LeaveRequest(
                employee_id=employees[5].id,
                start_date=(today + timedelta(days=3)).isoformat(),
                end_date=(today + timedelta(days=3)).isoformat(),
                reason="Medical appointment.",
                status="APPROVED",
                review_comment="Approved, please arrange a replacement.",
            )
        )

    # Preferences for the linked employee portal account.
    employee = employees[0] if employees else None
    if employee is not None and ShiftPreference.query.count() == 0:
        for day in week_days(start + timedelta(days=7)):
            if day.weekday() >= 5:
                continue
            db.session.add(
                ShiftPreference(
                    employee_id=employee.id,
                    work_date=day.isoformat(),
                    shift_code="EARLY" if day.weekday() < 3 else "MID",
                    is_available=True,
                    note="prefers mornings",
                )
            )

    db.session.commit()
    return created_attendance


def seed_demo_data():
    bootstrap_database()
    seed_users()
    seed_employees()
    shifts = seed_schedule()
    attendance = seed_attendance_and_leave()
    print(f"Seeded {len(EMPLOYEES)} employees, {shifts} schedule cells, {attendance} attendance rows.")


if __name__ == "__main__":
    application = create_app()
    with application.app_context():
        seed_demo_data()
    print("Done. Logins -> hr/hr123 , manager/manager123 , employee/emp123")
