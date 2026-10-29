# EMS — Employee Management System

Employee scheduling, attendance and leave management for **Meítǐ Shāngchéng** (retail store, Zhengzhou).
Built for the Fontys × ZZULI waterfall project, **Group 8** — Phase 1 prototype, final deadline
**1 November 2026**.

* Backend: **Python 3.11+ / Flask 3** (application-factory + blueprints)
* Database: **MySQL** is the target platform from the technical constraints; **SQLite** runs out of the box
* Front end: **HTML / CSS / JavaScript** (Bootstrap 5, no build step)
* Version control: **Git**

---

## 1. What is implemented (traceability to the URS)

| URS item | Requirement | Where it lives |
| --- | --- | --- |
| FR-01 | HR maintains employee basic information, unique employee ID | `app/views/employees.py`, `app/models.py::Employee` |
| FR-02 | HR builds the weekly shift schedule (early / mid / late), no overlapping shift per employee, 5 days/week | `app/views/scheduling.py`, `app/services.py::assign_shift/conflicts_for` |
| FR-03 | Employee selects preferred shift + available working dates | `app/views/employees.py::my_preferences`, `ShiftPreference` |
| FR-04 | HR marks working days for non-5-day-week employees (3 / 4 days) | `set_working_days()`, "Working days" panel on the employee form |
| FR-05 | Employee submits a leave request online (date + reason) | `app/views/attendance.py::submit_leave`, `LeaveRequest` |
| FR-06 | Manual on-duty attendance through a separate "on-duty" button | `mark_on_duty()`, `Attendance`, `data-on-duty` button in the portal |
| FR-07 | Account administration + self-service registration approved by HR (Could) | `app/views/auth.py` (`/users`, `/register`, approve/reject), `User.registration_status` |
| NFR-01 | Stability, transactional safety, graceful errors | error handlers, `db.session.rollback()` on 500, validation before every write |
| NFR-02 | Fast response, simple operation, clear feedback within 1 s | flash messages, JSON answers for AJAX, `/healthz` probe |
| NFR-03 | 50–500 employees, paginated queries, aggregate reporting | `per_page` pagination, `reports.py` aggregate queries |
| URS 1.3 | Exactly three roles (Ordinary Employee / HR / Supervisor-Manager) | `app/security.py`, `roles_required`, `backend_required` |
| URS 3.2 | UC-01 … UC-06 including the extension flows | implemented in `app/services.py`, each UC has a test |
| URS 4.x | Login screen, backend management page, operations page, employee personal page | `templates/auth/login.html`, `dashboard.html`, `scheduling/week.html`, `portal/*` |
| Won't-01…03 | No auto-scheduling algorithm, no hardware clocks, no Jupiter/mobile app | not implemented by design |

Out-of-scope items from the project plan (inventory, payroll, production hosting) are intentionally
absent.

---

## 2. Project structure

```
ems/
├─ app.py                     # PyCharm / VS Code run entry point (python app.py)
├─ config.py                  # environment + SQLite/MySQL switch, business constants
├─ requirements.txt
├─ seed.py                    # demo accounts, 10 employees, current-week roster
├─ pytest.ini
├─ .env.example               # copy to .env for MySQL credentials
├─ app/
│  ├─ __init__.py             # create_app() factory, blueprints, error handlers, CSRF guard
│  ├─ config_test.py          # in-memory test configuration
│  ├─ extensions.py           # SQLAlchemy object
│  ├─ security.py             # roles, login, CSRF, @roles_required
│  ├─ models.py               # 8 tables (users, employees, working days, shifts, schedules, …)
│  ├─ services.py             # business rules: validation, conflict checks, leave, attendance
│  ├─ views/                  # auth · employees · scheduling · attendance · reports
│  ├─ templates/              # Jinja2 pages grouped per application area
│  └─ static/                 # css/ems.css, js/ems.js
└─ tests/
   ├─ conftest.py             # app fixture + domain factories
   └─ test_requirements.py    # 51 tests, each naming the FR/NFR/UC it covers
```

Everything is modular on purpose: a new feature = a new file in `app/views/` plus a blueprint
registration in `create_app()`, which satisfies the "modular architecture supporting at least 3 future
extensions" success metric.

---

## 3. Setting up in PyCharm (recommended for this course)

### Step 1 — Open the project
1. `File ▸ Open…` and select the **`ems`** folder (the one containing `app.py`).
2. PyCharm asks about the interpreter: choose **Add interpreter ▸ New** and accept the suggestion.
   *PyCharm creates `.venv` automatically and installs nothing else yet.*

### Step 2 — Make sure the interpreter is the project one
`File ▸ Settings ▸ Project: ems ▸ Python Interpreter` → the list must show `.venv\Scripts\python.exe`.
If it does not: gear icon ▸ **Add Local Interpreter ▸ Virtualenv Environment ▸ New ▸ OK**.

### Step 3 — Install the packages
Open the **Terminal** tab at the bottom (PyCharm activates the venv automatically — the prompt starts
with `(.venv)`):

```bash
pip install -r requirements.txt
```

### Step 4 — Create the database and demo data
Either run the seed script from the terminal:

```bash
python seed.py
```

or right-click `seed.py` in the project tree ▸ **Run 'seed'**. PyCharm creates a run configuration for
you. Marker `app.py` as well if you like: **Run ▸ Edit Configurations ▸ + ▸ Python ▸ Script path:
`app.py`**.

### Step 5 — Run the application
* Terminal: `python app.py`
* or the green ▶ button next to `if __name__ == "__main__":` in `app.py`
* or right-click `app.py` ▸ **Run 'app'**

Console output ends with:

```
 * Running on http://127.0.0.1:5000
 * Debugger is active!
```

Open <http://127.0.0.1:5000/> and log in (section 6).

### Step 6 — Run the automated tests
Right-click the `tests` folder ▸ **Run 'pytest in test_requirements.py'**, or in the terminal:

```bash
pytest -q
```

### Step 7 — Enable PyCharm's Jinja2 support (optional but useful)
`Settings ▸ Languages & Frameworks ▸ Template Languages` → *Template language*: **Jinja2**,
*Template file types*: **HTML**. Autocompletion then works inside `app/templates/*.html`.

---

## 4. Setting up in VS Code

1. Open the `ems` folder (`File ▸ Open Folder…`).
2. Install the **Python** extension (and optionally **Jinja** for template highlighting).
3. Create and activate the virtual environment in the integrated terminal:

   ```powershell
   python -m venv .venv                 # Windows
   .venv\Scripts\activate
   # Git Bash / macOS / Linux:  python -m venv .venv && source .venv/bin/activate
   ```

4. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Create the database + demo data and start the server:

   ```bash
   python seed.py
   python app.py
   ```

6. `Ctrl+Shift+P ▸ Python: Select Interpreter ▸ .venv` so debugging and linting use the venv.
7. Run the tests from the **Testing** sidebar (pytest is auto-discovered via `pytest.ini`) or with
   `pytest -q`.

---

## 5. Switching to MySQL (target platform)

The prototype ships with SQLite so it starts with zero infrastructure, and switches to MySQL with one
environment variable — no code change:

```sql
-- run once as a MySQL administrator
CREATE DATABASE ems CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ems_user'@'localhost' IDENTIFIED BY 'ems_password';
GRANT ALL PRIVILEGES ON ems.* TO 'ems_user'@'localhost';
FLUSH PRIVILEGES;
```

```powershell
# Windows cmd
set EMS_DATABASE=mysql
python seed.py
python app.py
```

```bash
# Git Bash / macOS / Linux
export EMS_DATABASE=mysql
python seed.py && python app.py
```

`PyMySQL` is already in `requirements.txt`, so no driver installation is needed. Copy `.env.example`
to `.env` to keep the credentials out of the shell history (`python-dotenv` loads it automatically).

---

## 6. Demo accounts

| Role | User name | Password | Lands on |
| --- | --- | --- | --- |
| HR Administrator | `hr` | `hr123` | Backend — employee records, scheduling, working days, leave review |
| Supervisor / Manager | `manager` | `manager123` | Backend — approvals, staff status, reports |
| Ordinary Employee | `employee` | `emp123` | Personal page — own schedule, preferences, leave, on-duty button |

Change a password from **My account ▸ Change password**; the login screen asks for the *role* first,
exactly like the URS wireframe (URS 4.1).

---

## 7. Daily usage walkthrough (for the demo)

1. Log in as **hr** → **Dashboard** shows headcount, shift coverage, on-duty count and warnings.
2. **Employees ▸ Add employee** — mandatory fields and duplicate-ID validation are enforced
   (UC-01 extensions 1a/1b).
3. Open an employee → set **Working days** to Tue/Thu/Sat for a part-time contract (FR-04, UC-04).
4. **Scheduling ▸ Weekly schedule** — assign EARLY / MID / LATE per cell and press
   *Save weekly schedule*. Try to give one employee two shifts on the same day: the system refuses it
   and shows the warning (UC-02 extension 2a). Type a date that is not in the employee's working-day
   set: you get a soft warning, which you may override with the *Override soft warnings* checkbox.
5. **Scheduling ▸ Conflicts & warnings** lists every rule that fired for the week.
6. Log out, log in as **employee** → **Preferences** (select shift + available dates), **Leave**
   (submit a request), **Attendance** (press the separate *on-duty* button — attendance is never
   inferred from a login).
7. Log in as **manager** → **Leave** to approve/reject (approving clears conflicting shifts),
   **Staff status** and **Reports** for the management overview.
8. **Roster preview** is print-ready for the staff notice board.

---

## 8. Business rules implemented

| Rule | Source | Behaviour |
| --- | --- | --- |
| Fixed shifts early 08:00–12:00, mid 12:00–16:00, late 16:00–20:00 | URS 1.4 | seeded `shift_templates`, no custom shifts |
| One shift per employee per day, 5 days/week | FR-02 | database unique constraint **and** a blocking conflict message |
| Working-day set per employee (3/4-day weeks) | FR-04 | `employee_working_days`; warns when a shift falls outside it |
| Weekly contract limit | FR-02 / FR-04 | warning above the contract, hard refusal above 7 shifts |
| Leave request carries date + reason | FR-05 | required fields, overlap check, PENDING → APPROVED/REJECTED |
| Attendance by explicit on-duty action | FR-06 | one record per employee per day, check-in time stamped, no future dates |
| Unique employee ID, unique contact e-mail | FR-01 | validated on create *and* update |
| Sensitive pay data | project plan 5.2 | employee records and wage fields are behind `backend_required` |

---

## 9. Tests

```bash
pytest -q                     # 51 tests
pytest -v                     # with the requirement name of each test
python -m pytest tests/test_requirements.py -k scheduling
```

The suite covers every Must and Should requirement, the three use-case extension flows, role-based
access control, the CSRF guard and a SQL-injection-style input check. It is the executable version of
the M4 "Test Plan Document" and "Final Test Record".

---

## 10. Troubleshooting

| Symptom | Fix |
| --- | --- |
| `ModuleNotFoundError: No module named 'flask'` | the venv is not active / the wrong interpreter is selected — reinstall with `pip install -r requirements.txt` |
| `Address already in use` on port 5000 | another server is running: close it, or change the port in `app.py` (`app.run(port=5001)`) |
| `Access denied for user 'ems_user'@'localhost'` | the MySQL user/privileges were not created — rerun the SQL block in section 5, or unset `EMS_DATABASE` to fall back to SQLite |
| `BadZipFile`/CRC error while reading a project DOCX | the document contains a corrupt embedded image; read `word/document.xml` directly (this is what the report-generation script does) |
| Login says "registered as …" | you picked a role that does not match the account — the URS login screen verifies the role |
| Reset everything | delete `instance/ems.sqlite3` and run `python seed.py` again |

---

## 11. Screenshots for the report

With the server running, capture these four views (they map one-to-one onto URS figures 2–5):

1. `/login` — login screen with role selection (Figure 2)
2. `/dashboard` — backend employee & scheduling management (Figure 3)
3. `/schedule/conflicts` — operations / warnings panel (Figure 4)
4. `/dashboard` as `employee` — personal page (Figure 5)

Press `Ctrl+P` on the roster preview page for a printable weekly roster.

---

*Group 8 — Zhang Houze (lead), Liu Yaxin, Lu Siqin, Yan Junyu, Xia Junyu.*
*Tutor: Stan van Hartingsveidt.*
