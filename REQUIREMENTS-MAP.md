# 需求 ↔ 代码 ↔ 测试 对照表

这份表可以直接贴进报告的"实现说明"或"测试计划"章节：老师问"这条需求在哪儿实现的、怎么验证的"，按表查即可。

图例：**FR** 功能需求 ｜ **NFR** 非功能需求 ｜ **UC** 用例

---

## 1. 教师/课程硬性要求（来自 Project Plan 第 6、8 章）

| 要求（原文要点） | 落点 |
|---|---|
| Web 应用（B/S 架构），Python Flask 后端 | `app.py`、`app/__init__.py::create_app()` |
| 前端 HTML/CSS/JS | `app/templates/**`（28 个页面）、`app/static/css/ems.css`、`app/static/js/ems.js` |
| 数据库 MySQL | `config.py::_mysql_uri()`（`EMS_DATABASE=mysql` 即切换，`PyMySQL` 驱动已列入 requirements） |
| 架构模块化，支持 ≥3 个未来扩展 | 5 个蓝图分模块：`app/views/{auth,employees,scheduling,attendance,reports}.py`；新增功能 = 新增一个视图文件 + 在工厂注册 |
| Git 版本控制 | `.gitignore`（忽略 `venv/`、`instance/*.sqlite3`、`.env`） |
| 恰好 3 个角色 + RBAC，保护薪酬数据 | `app/security.py`（`ROLE_EMPLOYEE/HR/MANAGER`、`@roles_required`、`@backend_required`）；薪酬字段只在 `employees/form.html` 的后台页面出现 |
| 页面 3 秒内加载、支持 500 员工 | `employees.list_employees()` 每页 20 条分页；`reports.py` 全部为聚合查询；唯一索引见 `models.py` 的 `index=True` |
| 每步操作 1 秒内给出明确反馈 | `base.html` 的 flash 提示区；打卡按钮的 AJAX JSON 反馈（`static/js/ems.js`） |
| 零严重缺陷、最多 2 个外观小缺陷 | 统一错误页 `templates/errors/{400,403,404,500}.html`；500 时 `db.session.rollback()` |
| M4 需要测试计划 / 测试记录 | `tests/test_requirements.py`（每个用例名标注 FR/NFR/UC），`pytest.ini` |

---

## 2. 功能需求（URS 2.2 MoSCoW）

| ID | 需求 | 页面 / 路由 | 业务逻辑 | 数据表 | 测试用例 |
|---|---|---|---|---|---|
| **FR-01** (Must) | HR 维护员工基本信息（邮箱、地址、紧急联系人），工号唯一 | `GET/POST /employees`、`/employees/new`、`/employees/<id>`、`/employees/<id>/edit` | `services.validate_employee_form()`（必填、邮箱格式、**工号唯一**、邮箱唯一） | `employees` | `TestEmployeeRecords`（5 个） |
| **FR-02** (Must) | HR 手工排周班（早/中/晚固定班次），同员工不得重叠，每周 5 天 | `GET /schedule/`、`POST /schedule/week`、`/schedule/cell`、`/schedule/conflicts`、`/schedule/preview` | `services.conflicts_for()`、`assign_shift()`、`validate_week()`、`coverage_for_week()` | `schedules`、`shift_templates` | `TestScheduling`（10 个） |
| **FR-03** (Must) | 员工选择偏好班次 + 可用工作日期 | `GET/POST /me/preferences` | `services.save_preference()`、`preference_summary()` | `shift_preferences` | `TestPreferences`（6 个） |
| **FR-04** (Must) | HR 为非 5 天制员工设置每周 3/4 天工作日 | 员工详情页"For working days"面板、`POST /employees/<id>/working-days` | `services.set_working_days()`、`normalise_working_days()` | `employee_working_days` | `TestWorkingDays`（3 个） |
| **FR-05** (Should) | 员工在线提交请假申请（日期 + 原因） | `GET/POST /leave`、`/leave/submit`、`/leave/<id>`、`/leave/<id>/review` | `services.create_leave_request()`、`review_leave_request()`（批准后自动清除冲突班次） | `leave_requests` | `TestLeaveRequests`（6 个） |
| **FR-06** (Should) | 员工通过**单独按钮**手工打卡，禁止以登录判断出勤 | 门户 `GET /me/attendance`、`POST /attendance/on-duty`；后台 `GET /attendance`、`/attendance/history` | `services.mark_on_duty()`（每天一条、禁止未来日期、记录打卡时间戳）、`attendance_board()` | `attendance` | `TestAttendance`（5 个） |
| **FR-07** (Could) | 账号管理 + 员工自助注册（HR 审批） | 顶部 **Administration** 菜单：`GET /users`、`GET/POST /users/new`、`GET/POST /users/<id>/edit`、`POST /users/<id>/reset-password`、`POST /users/<id>/toggle`、`POST /users/<id>/delete`；登录页 `GET/POST /register`、`POST /users/<id>/approve`、`POST /users/<id>/reject` | `security.validate_account_form()`、`account_guard_errors()`、`validate_registration_form()`：用户名唯一、仅 HR 可建 HR/经理账号、最后一个启用的 HR 管理员不可降级/停用/删除、自助注册只能建普通员工账号且必须匹配未绑定的工号、审批前禁止登录 | `users`（`registration_status`） | `TestAccountManagement`（11 个）+ `TestSelfRegistration`（12 个） |

---

## 3. 非功能需求（URS 2.3）

| ID | 需求 | 实现方式 | 测试/验证 |
|---|---|---|---|
| **NFR-01** (Must) | 稳定性优先（稳定 > 易用 > 功能丰富） | 所有写操作先校验再提交；唯一约束在数据库层兜底；`errorhandler(500)` 回滚事务；`pool_pre_ping=True` | `test_database_prevents_two_shifts_on_the_same_day`、错误页模板 |
| **NFR-02** (Should) | 响应快、操作简单、反馈明确 | 分页 + 索引；flash 消息；打卡 AJAX 即时回显；`/healthz` 健康检查 | `test_health_probe`、`static/js/ems.js` |
| **NFR-03** (Must) | 支持 50–500 人并平滑扩展 | `per_page=20` 分页；报表全聚合查询；`/employees?format=json` 分页导出 | `test_employee_json_export_is_compact`（25 条 → 每页 20） |

---

## 4. 用例流程（URS 3.2）

| 用例 | 主成功场景 | 扩展流程 | 代码位置 |
|---|---|---|---|
| UC-01 维护员工信息 | 录入 → 校验 → 保存 | **1a** 必填缺失报错返回；**1b** 工号重复报错返回 | `validate_employee_form()` |
| UC-02 排周班 | 逐日排班 → 冲突检查 → 保存 | **2a** 检测到重叠 → 冲突警告并返回 | `conflicts_for()`（`SHIFT_OVERLAP` 为硬拒绝；非工作日/请假/不可用/偏好不符为软警告） |
| UC-03 选择偏好 | 选班次 + 可用日期 → 保存偏好 | 无 | `save_preference()` |
| UC-04 设置非标准工作日 | HR 选 3/4 天 → 保存 | 无 | `set_working_days()` |
| UC-05 提交请假 | 选日期 + 原因 → 记录为 PENDING | 无 | `create_leave_request()` |
| UC-06 上班打卡 | 按"上班打卡"按钮 → 记录打卡时间 | 无 | `mark_on_duty()` |

---

## 5. 界面（URS 第 4 章 GUI / 第 5 章线框图）

| URS 图 | 页面 | 模板文件 | 访问路径 |
|---|---|---|---|
| 图 2 登录页（选角色 + 密码） | 登录 | `templates/auth/login.html` | `/login` |
| 图 3 后台员工与排班管理 | 后台首页看板 | `templates/dashboard.html` | `/dashboard`（HR/经理） |
| 图 3 排班网格 | 周排班表 | `templates/scheduling/week.html` | `/schedule/` |
| 图 4 运营/异常与警告 | 冲突与警告 | `templates/scheduling/conflicts.html` | `/schedule/conflicts` |
| 图 5 员工个人信息页 | 员工门户 | `templates/portal/{dashboard,schedule,preferences,attendance}.html` | `/dashboard`（员工）、`/me/*` |
| —（加分） | 报表 | `templates/reports/index.html` | `/reports/` |
| —（加分） | 人员状态看板 | `templates/reports/status.html` | `/reports/status` |

---

## 6. 明确不做的内容（URS 2.4 Won't / Project Plan 第 7 章）

| 编号 | 不做的东西 | 在哪说明 |
|---|---|---|
| Won't-01 | 智能/自动排班算法 | 排班全部为 HR 手工操作，代码中无算法模块 |
| Won't-02 | 考勤硬件（指纹/打卡机）对接 | 只有网页手工打卡（`check_in_method="MANUAL_ON_DUTY"`） |
| Won't-03 | 母公司 Jupiter 服务、原生 App | 无移动端、无跨公司接口 |
| 非交付物 | 库存/补货、薪资结算、生产服务器托管、移动端自适应 | 未实现；如需可在报告中列入"未来版本" |

---

## 7. 演示与验收提示

1. 每个 Must 需求（FR-01～04）都有对应页面和测试，**演示时先跑 `pytest -q` 再点页面**，说服力最强。
2. 权限演示：先用 `employee` 账号登录，直接在地址栏输入 `/employees`，应看到 403 页面（服务端拦截，不是只隐藏菜单）。
3. 冲突演示：排班表里给同一员工同一天连排两班，系统拒绝并显示具体原因。
4. 数据量演示（NFR-03）：`python seed.py` 后可用循环批量建 500 条员工数据，列表页仍在 3 秒内打开（分页生效）。
