# EMS 安装与运行说明（PyCharm / VS Code）

> 项目：Meítǐ Shāngchéng 员工排班管理系统（Employee Management System）
> 小组：Group 8 ｜ 交付阶段：Phase 1 原型（截止 2026-11-01）
> 项目目录：`ems/`（就是本文件所在的文件夹）

---

## 0. 需要安装什么（一页清单）

| 序号 | 要装的东西 | 版本要求 | 作用 | 是否必需 |
|---|---|---|---|---|
| 1 | **Python** | 3.10 – 3.12（推荐 3.11） | 运行环境 | 必需 |
| 2 | **PyCharm**（Community 免费版即可） 或 **VS Code + Python 扩展** | 最新版 | 编辑器 | 必需 |
| 3 | **pip 依赖包**（见 `requirements.txt`） | 自动匹配 | Flask 框架、ORM、测试 | 必需 |
| 4 | **MySQL 8**（+ PyMySQL 驱动） | 8.0+ | 课程规定的正式数据库 | 可选（默认 SQLite 即可跑） |
| 5 | Git | 任意 | 版本控制（课程强制） | 建议 |

`requirements.txt` 里的 7 个包：

```
Flask>=3.0,<4.0              # Web 框架
Flask-SQLAlchemy>=3.1,<4.0   # Flask 的 ORM 集成
SQLAlchemy>=2.0,<3.0         # ORM 本体（8 张表的映射）
Werkzeug>=3.0,<4.0           # 密码哈希、WSGI（Flask 自带依赖）
python-dotenv>=1.0           # 读取 .env 配置
PyMySQL>=1.1                 # MySQL 驱动（用 SQLite 时用不到）
pytest>=8.0                  # 自动化测试
```

> 只装这 7 个包，**不需要** npm / Node.js / Vue，前端是原生 HTML+CSS+JS（Bootstrap 5 通过 CDN 引入）。

---

## 1. 安装 Python（跳过如果你已有 3.10+）

1. 打开 <https://www.python.org/downloads/> 下载 3.11.x（Windows installer 64-bit）。
2. 安装时**务必勾选** `Add python.exe to PATH`，然后点 Install Now。
3. 验证（Win + R → `cmd`）：

```bat
python --version
pip --version
```

出现 `Python 3.11.x` 即成功。若提示"不是内部或外部命令"，说明第一步没勾 PATH，重装并勾选即可。

---

## 2. PyCharm 完整步骤（推荐用于本课程）

### 2.1 打开项目
`File ▸ Open…` → 选中 **`ems`** 文件夹（里面能看到 `app.py` 的那一层）→ OK。

### 2.2 创建虚拟环境（venv）
打开项目后，PyCharm 底部会提示解释器未配置：
**Add interpreter ▸ New ▸ Virtualenv Environment ▸ Location 默认为 `ems\.venv` ▸ OK**。

若没有提示：`File ▸ Settings ▸ Project: ems ▸ Python Interpreter ▸ 齿轮 ▸ Add Local Interpreter ▸ Virtualenv Environment ▸ New ▸ OK`。
确认列表里出现 `...\ems\.venv\Scripts\python.exe`。

### 2.3 安装依赖包
打开底部 **Terminal**（此时提示符前面应带 `(.venv)`，说明虚拟环境已激活），执行：

```bash
pip install -r requirements.txt
```

> 国内网络慢时换镜像：
> `pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`

验证安装成功：

```bash
pip list
```
应能看到 `Flask / Flask-SQLAlchemy / SQLAlchemy / PyMySQL / pytest` 等。

### 2.4 初始化数据库 + 演示数据
终端执行（或右键 `seed.py ▸ Run 'seed'`）：

```bash
python seed.py
```

输出类似：`Seeded 10 employees, 62 schedule cells, 28 attendance rows.`
此时 `ems/instance/ems.sqlite3` 已生成。

### 2.5 启动网站
终端执行 `python app.py`，或右键 `app.py ▸ Run 'app'`。
控制台出现：

```
 * Running on http://127.0.0.1:5000
 * Debugger is active!
```

浏览器打开 <http://127.0.0.1:5000/>，用下面账号登录：

| 角色 | 账号 | 密码 | 进入的页面 |
|---|---|---|---|
| HR 管理员 | `hr` | `hr123` | 员工档案 / 周排班 / 工作天数 / 请假审核 |
| 主管·经理 | `manager` | `manager123` | 审批 / 人员状态 / 报表 |
| 普通员工 | `employee` | `emp123` | 个人信息 / 我的班表 / 偏好 / 请假 / 上班打卡 |

### 2.6 运行测试
终端执行：

```bash
pytest -q
```

或在左侧 `tests` 文件夹上右键 ▸ **Run 'pytest in test_requirements.py'**。
预期：全部用例通过（51 个），每个用例名对应 URS 的 FR/NFR 编号。

---

## 3. VS Code 完整步骤

1. 打开文件夹：`File ▸ Open Folder…` → 选 `ems`。
2. 侧边栏 **Extensions** 搜索安装 **Python**（可选再装 **Jinja** 或 **Better Jinja**，模板会高亮）。
3. `Ctrl+Shift+P` → `Python: Select Interpreter` → 选择 `ems\.venv\Scripts\python.exe`（没有就选 `Create Virtual Environment`）。
4. 打开集成终端（`` Ctrl+` ``），安装依赖：

```bash
pip install -r requirements.txt
```

5. 初始化数据并启动：

```bash
python seed.py
python app.py
```

6. 测试：左侧 **Testing**（烧瓶图标）→ `Configure Python Tests` → **pytest** → 选中 `tests` 目录，然后点 ▶ 全跑；或终端 `pytest -q`。

---

## 3.5 新增账号（FR-07）

`seed.py` 只生成 3 个演示账号；正式使用时账号在**网页上**创建，三种方式：

### 方式 A（推荐）：HR 登录网页创建

1. 用 `hr / hr123` 登录 → 顶部导航 **Administration ▸ Create login account**（或 **User accounts** 页右上角 **+ New account**）
2. 填写：用户名、密码（≥5 位、两次一致）、显示名、**角色**、**关联员工记录**
3. 保存后新账号立即可用；在 **User accounts** 页可随时改角色、重置密码、停用/启用、删除

系统强制的规则：
- 用户名唯一（不区分大小写）；
- **只有 HR 能创建 HR / 经理账号**，经理只能建普通员工账号；
- 普通员工账号**必须关联一条员工记录**，否则门户里没有班表数据；
- **最后一个启用的 HR 管理员**不能被降级、停用或删除（防止把系统锁死）；
- 不能停用自己当前登录的账号；被停用的账号登录会被拒绝。

### 方式 B：命令行创建（适合部署或批量）

```bat
flask --app app create-user
```

交互式依次询问用户名、密码、角色；也可一次写完：

```bat
flask --app app create-user --username wangfang --password fang123 --role EMPLOYEE --employee-id EMP-0002
```

`--role` 取 `EMPLOYEE` / `HR` / `MANAGER`；`--employee-id` 填员工工号即可自动关联。

### 方式 D：员工自助注册 + HR 审批

登录页底部有 **"New employee? Create your account"** 链接，员工可以自己提交注册：

1. 点登录页的 **Create your account**
2. 填 4 项：**Employee ID（工号）**、**Full name（与档案完全一致）**、**User name**、**Password ×2**
3. 提交后账号是 **Pending approval（待审批）** 状态——此时登录会提示
   *"Your registration is waiting for HR approval"*，进不去系统
4. HR 登录后打开 **Administration ▸ User accounts**，顶部出现黄色
   **Pending registrations (n)** 区块：
   - **Approve** → 账号立即启用，员工可用该账号登录
   - **Reject** → 账号删除，员工档案解绑，员工可重新注册

规则：
- 自助注册**只能**创建 Ordinary Employee 账号（防止有人自己注册成 HR/经理）；
- 工号必须已存在于员工档案，且该档案**还没绑账号**，姓名必须与档案一致；
- 同一个工号/用户名不能重复注册（重复用户名会提示"已有注册在等待审批"）。

> 旧数据库升级：启动时会自动执行一次轻量的表结构升级（`users` 表加
> `registration_status` 列），已有账号与员工数据不受影响。也可以手动执行
> `flask --app app init-db` 或 `python seed.py` 触发同样的升级。
### 方式 C：改 `seed.py`（仅用于演示数据）

`seed_users()` 里有三个账号定义，可自行增删；改完执行 `python seed.py`。该脚本是**幂等**的：已存在的账号不会重置密码，只补缺失的内容。想彻底重来就删掉 `instance\ems.sqlite3` 再跑一次。

---

## 3.6 角色权限（谁负责什么）

登录页**不再选择角色**：一个输入框收所有人，系统根据账号自动判断身份，登录后页面顶部会显示
"Signed in as …" 徽章（个人版块里也有一行 "My role (identity)"）。

| 功能 | 员工 | HR 管理员 | 主管 / 经理 |
|---|---|---|---|
| 登录 / 注册（自助注册需审批） | ✅ | ✅ | ✅ |
| 查看自己的班表、偏好、请假、打卡 | ✅ | — | — |
| 员工档案增删改（招聘） | — | ✅ | 只读 |
| 账号管理：新建 / 审批注册 / 重置密码 / 停用 | — | ✅ | — |
| **周排班（保存、复制、清空）** | — | 只读 | ✅ |
| 冲突与警告、班表打印 | — | ✅ | ✅ |
| **请假审批（批准 / 拒绝）** | 提交 | 只读 | ✅ |
| 考勤看板、报表、人员状态 | — | ✅ | ✅ |

改动说明（相比第一版）：

- 登录不再需要选角色，账号本身就决定跳到员工门户还是后台；
- 主管新增**排班**权限（保存/复制/清空），HR 打开同一个页面是只读视图；
- 请假审批**只由主管**执行，HR 打开请假页只看到"waiting for the manager"；
- 账号管理（含注册审批）**只由 HR** 执行；
- 自助注册时工号**可以留空**，HR 审批时在下拉框里把账号关联到某条员工档案。

> 想改回"HR 也能排班"：把 `app/views/scheduling.py` 里 4 个
> `@roles_required(*SCHEDULER_ROLES)` 改成 `@roles_required(ROLE_HR, ROLE_MANAGER)` 即可；
> 想改回"HR 也能批假"：把 `app/security.py` 的 `APPROVER_ROLES` 改回 `(ROLE_MANAGER, ROLE_HR)`。

## 4. 切换到 MySQL（课程规定的正式数据库）

默认用 SQLite 是为了"零配置先跑起来"；课程要求的 MySQL 只需一个环境变量，**不用改任何代码**。

### 4.1 建库建用户（用 MySQL 管理员身份执行一次）

```sql
CREATE DATABASE ems CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ems_user'@'localhost' IDENTIFIED BY 'ems_password';
GRANT ALL PRIVILEGES ON ems.* TO 'ems_user'@'localhost';
FLUSH PRIVILEGES;
```

### 4.2 让项目连 MySQL

Windows cmd（PyCharm 的 Terminal 默认就是 cmd）：

```bat
set EMS_DATABASE=mysql
python seed.py
python app.py
```

PowerShell：

```powershell
$env:EMS_DATABASE = "mysql"
```

Git Bash / macOS / Linux：

```bash
export EMS_DATABASE=mysql
```

或者更省事：把 `.env.example` 复制成 `.env`，把 `EMS_DATABASE=sqlite` 改成 `mysql`，填上账号密码——`python-dotenv` 会自动读取，不用每次敲 `set`。

> 若改回 SQLite：删除 `EMS_DATABASE` 变量，或 `.env` 里改回 `sqlite`。

---

## 5. 目录结构（老师看代码时的顺序）

```
ems/
├─ app.py                ← PyCharm 里运行这个文件即可启动
├─ config.py             ← SQLite/MySQL 切换 + 业务常量（班次时间、每周 5 天…）
├─ requirements.txt      ← 要安装的包
├─ seed.py               ← 生成账号、10 名员工、本周排班
├─ pytest.ini / tests/   ← 测试
└─ app/
   ├─ __init__.py        ← create_app() 工厂：注册蓝图、CSRF、错误页
   ├─ security.py        ← 3 个角色 + 登录 + @roles_required 权限装饰器
   ├─ models.py          ← 8 张表（users / employees / 工作日 / 班次 / 排班 / 偏好 / 请假 / 考勤）
   ├─ services.py        ← 业务规则：校验、冲突检测、请假、打卡
   ├─ views/             ← auth · employees · scheduling · attendance · reports（5 个蓝图）
   ├─ templates/         ← 28 个页面（登录、门户、后台、报表、错误页）
   └─ static/            ← css + js
```

---

## 6. 常见报错速查

| 报错 | 原因与解决 |
|---|---|
| `ModuleNotFoundError: No module named 'flask'` | 没激活 venv 或解释器选错。终端先 `venv\Scripts\activate`，PyCharm 里确认解释器是 `.venv` |
| `'python' 不是内部或外部命令` | 装 Python 时没勾 PATH；或改用 `py -3 -m venv .venv` |
| `pip install` 卡住不动 | 网络问题，加清华镜像：`-i https://pypi.tuna.tsinghua.edu.cn/simple` |
| `Address already in use`（端口 5000 被占） | 关掉已在跑的服务，或把 `app.py` 最后一行改成 `port=5001` |
| `Access denied for user 'ems_user'@'localhost'` | 第 4.1 步 SQL 没执行，或不设 `EMS_DATABASE` 回退到 SQLite |
| 登录提示 "registered as …" | 角色选错。URS 4.1 要求先选角色再输密码，系统会校验角色与账号是否一致 |
| 想重来一遍 | 删掉 `instance/ems.sqlite3`，重新 `python seed.py` |

---

## 7. 演示脚本（课堂 10 分钟建议顺序）

1. 以 `hr` 登录 → 首页看板（人数、覆盖率、今日打卡、待审批、冲突数）。
2. 新员工录入 → 故意填重复工号 / 缺必填项 → 展示 UC-01 的两条扩展流程。
3. 打开某员工 → 把工作天数设为"周二/周四/周六" → 展示 FR-04（3 天制兼职）。
4. 周排班表：同一员工同一天排两个班 → 系统拒绝（UC-02 扩展 2a）；排到非工作日 → 软警告，可勾选覆盖。
5. 冲突与警告页 → 列出本周所有规则命中项。
6. 以 `employee` 登录 → 偏好（班次+可用日期）、请假申请、点"上班打卡"按钮（强调 URS 写的"不能以登录判断出勤"）。
7. 以 `manager` 登录 → 批准请假（会自动清掉冲突班次）→ 人员状态看板 → 报表页。
8. 排班预览页 `Ctrl+P` 打印周排班表（可当交付物截图）。

## 8. 让别人也能访问（局域网 / 公网链接 / 部署）

### 8.1 同一个 Wi-Fi（最简单，免费）

```bat
set EMS_HOST=0.0.0.0
python app.py
```

启动后终端会打印：

```
 Local:   http://127.0.0.1:5000/
 Network: http://192.168.1.23:5000/   <- share this on the same Wi-Fi
```

把 `Network` 那个地址发给同一 Wi-Fi 下的同学/老师即可。

- 第一次启动 Windows 会弹防火墙提示，勾选 **专用网络** 并允许；
- 没弹窗但仍连不上的话：控制面板 ▸ Windows Defender 防火墙 ▸ 允许应用通过防火墙 ▸ 勾选 Python；
- 对方打不开时确认两点：① 两人在同一网络；② 你的电脑没休眠。

### 8.2 公网临时链接（对方在任何网络都能开）

保持服务在本地运行（`python app.py`，默认 127.0.0.1:5000），另开一个终端：

**方式 A — Cloudflare Tunnel（免费、不用注册账号）**

```bat
winget install --id Cloudflare.cloudflared
cloudflared tunnel --url http://127.0.0.1:5000
```

终端会打印一个 `https://xxxx-xxxx.trycloudflare.com` 链接，直接发给别人即可。

**方式 B — ngrok**

```bat
winget install Ngrok.Ngrok
ngrok config add-authtoken <你的 token>     :: 免费注册后获取
ngrok http 5000
```

会得到 `https://xxxx.ngrok-free.app` 链接。

> 两种隧道都是**临时**的：关掉终端链接就失效；链接拿到的人都能访问，演示完记得关。
> 隧道只暴露你本机的 5000 端口，你的代码和虚拟环境不会被上传。

### 8.3 长期部署（免费额度）

| 平台 | 说明 |
|---|---|
| **PythonAnywhere**（免费档） | 上传项目 ▸ 新建 Web App ▸ 选 Flask ▸ 指定 WSGI 入口 `app:create_app()` ▸ 安装 `requirements.txt` |
| **Render**（免费 Web Service） | 连 GitHub 仓库，Build: `pip install -r requirements.txt`，Start: `gunicorn "app:create_app()"` |
| **国内云服务器**（阿里云/腾讯云轻量） | 装 Python + `pip install`，用 `gunicorn -b 0.0.0.0:80 "app:create_app()"`，再用 nginx 反代 |

部署到公网时数据库建议切到 MySQL（见第 4 节），SQLite 更适合本地和小范围演示。

### 8.4 公开链接前的安全检查

```bat
set EMS_SECRET_KEY=换成一串很长的随机字符
set EMS_ALLOW_REGISTRATION=0      :: 关闭自助注册，只让 HR 建号
set EMS_DEBUG=0                   :: 关闭调试器
```

另外建议：
- **改掉演示密码**（`hr/hr123`、`manager/manager123`）——登录后 My account ▸ Change password；
- 演示结束关掉隧道 / 停止服务；
- 页面上的"Prototype demo accounts"提示在正式展示前可以从 `templates/auth/login.html` 删掉。
