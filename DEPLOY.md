# 把代码放到 Git 并拿到永久链接（部署指南）

> 先搞清楚一件事：**Git 只存代码，不会给你网址**。
> 永久链接 = 代码推到 GitHub + 托管平台从 GitHub 拉代码运行，平台给你一个固定域名。
>
> 本项目已内置以下部署文件，不用你再改：
> `wsgi.py`（生产入口）· `Procfile`（通用启动命令）· `render.yaml`（Render 一键部署）·
> `runtime.txt` / `.python-version`（Python 3.11）· `requirements.txt`（含 gunicorn）

---

## 第 0 步：装 Git（你的电脑还没有）

任选一种：

**方式 A — 装 Git 命令行（推荐，后面命令都能用）**

```bat
winget install --id Git.Git -e --source winget
```

装完**关掉并重新打开** PyCharm，验证：

```bat
git --version
```

**方式 B — GitHub Desktop（图形界面，自带 Git，不用命令行）**

下载 <https://desktop.github.com/> → 安装 → 登录 GitHub → `File ▸ Add local repository` 选择 `ems` 文件夹 → `Create repository` → `Publish repository`。

> 方式 B 更简单，但下面我按命令行写，两条路等效。

---

## 第 1 步：在 GitHub 建仓库并推送代码

1. 浏览器打开 <https://github.com/new>
2. Repository name 填 `ems`（或 `meiti-ems`），**Private 或 Public 都行**（Private 也能部署，只是要看平台授权），**不要**勾选 "Add a README"（避免冲突）
3. 创建后复制仓库地址，形如 `https://github.com/你的用户名/ems.git`

在 PyCharm 的 Terminal 里（`cd` 到 `ems` 目录，能看到 `app.py` 那一层）：

```bat
git init
git add .
git commit -m "EMS Phase 1: Flask prototype (FR-01..FR-07, self-registration, RBAC)"
git branch -M main
git remote add origin https://github.com/你的用户名/ems.git
git push -u origin main
```

推送时会要求登录：
- 密码处**不能填 GitHub 登录密码**，要填 **Personal Access Token**：
  GitHub ▸ Settings ▸ Developer settings ▸ Personal access tokens ▸ Tokens (classic) ▸ Generate new token ▸ 勾 `repo` ▸ 生成后复制，当作密码粘贴
- 或者用 GitHub Desktop 推送，省去 token

确认没把垃圾推上去：`.gitignore` 已排除 `instance/`、`.venv/`、`__pycache__`、`.env`。
**数据库文件不会上传**，部署后平台会自己跑 `seed.py` 重新生成。

---

## 第 2 步：选一个平台部署（两条免费路线）

| 平台 | 永久链接 | 数据是否保留 | 难度 | 适合 |
|---|---|---|---|---|
| **Render**（免费 Web Service） | `https://ems-xxxx.onrender.com` | ❌ 免费档 SQLite 每次部署/重启会重置 | ⭐ 最简单，连 GitHub 自动部署 | 课程演示、给老师看 |
| **PythonAnywhere**（免费档） | `https://你的用户名.pythonanywhere.com` | ✅ 文件持久保存，SQLite 数据不丢 | ⭐⭐ 要在网页上配置一次 | 需要"长期可用 + 数据不丢" |

### 路线 A：Render（最快，5 分钟）

1. 注册 <https://render.com/>（用 GitHub 账号登录最方便）
2. **New +** ▸ **Blueprint** ▸ 选择你的 `ems` 仓库 ▸ Apply
   - Render 会读取 `render.yaml`，自动配置：构建 `pip install -r requirements.txt`、启动 `python seed.py && gunicorn wsgi:application`
3. 等 2–4 分钟构建完成，得到 `https://ems-xxxx.onrender.com`
4. 打开链接 → 用 `hr / hr123` 登录 → 改密码

注意（免费档特性）：
- 15 分钟没人访问会休眠，下次打开需要等 30–60 秒唤醒，属正常现象
- 每次重新部署，SQLite 数据会重置为演示数据（账号、排班回到初始状态）
- 想持久化：Render 付费磁盘（$1–7/月）或改用 Postgres，见 `render.yaml` 里的注释

### 路线 B：PythonAnywhere（数据不丢，推荐长期用）

1. 注册 <https://www.pythonanywhere.com/> 免费账号（用户名会成为你的域名）
2. 打开 **Consoles ▸ Bash**，克隆代码：

```bash
git clone https://github.com/你的用户名/ems.git
cd ems
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python seed.py
```

3. 打开 **Web ▸ Add a new web app** ▸ **Manual configuration** ▸ 选 **Python 3.11**
4. 在 Web 页面里设置：
   - **Source code**: `/home/你的用户名/ems`
   - **Virtualenv**: `/home/你的用户名/ems/.venv`
5. 点 **WSGI configuration file** 那个链接，把内容改成：

```python
import os
import sys

path = "/home/你的用户名/ems"
if path not in sys.path:
    sys.path.insert(0, path)

os.environ["EMS_SECRET_KEY"] = "换成一串很长的随机字符"
os.environ["EMS_DATABASE"] = "sqlite"
os.environ["EMS_ALLOW_REGISTRATION"] = "1"

from wsgi import application  # noqa: E402,F401
```

6. 点 **Reload**，访问 `https://你的用户名.pythonanywhere.com`
7. 以后更新代码：Bash 里 `cd ems && git pull` → 回到 Web 页面点 **Reload**

> 免费档限制：每 3 个月要在网页上点一次续期；CPU 秒数有限（演示够用）。

---

## 第 3 步：部署完成后的检查清单

- [ ] 打开链接能看到登录页（不是 500 错误页）
- [ ] `hr / hr123` 能登录，看到后台看板
- [ ] **马上改掉演示密码**：My account ▸ Change password（hr、manager 两个账号都改）
- [ ] 注册页能正常提交（或按需关闭：环境变量 `EMS_ALLOW_REGISTRATION=0`）
- [ ] 用手机浏览器打开一次，确认公网可访问
- [ ] 把链接发给组员，让每人用自己的工号注册 → 你用 HR 账号审批

---

## 常见报错

| 现象 | 原因 / 解决 |
|---|---|
| Render 构建失败 `No module named 'flask'` | `requirements.txt` 被改坏了（比如第一行写成了 `pip install ...`）。这个文件里**只能**一行一个包名，不能有 `pip install` |
| 部署后 500：`no such table: users` | 启动命令里没跑 `seed.py`。Render 用 `render.yaml` 的 startCommand；PythonAnywhere 在 Bash 里手动 `python seed.py` |
| 打开链接 502 / 一直加载 | Render 免费档在唤醒，等 60 秒；仍失败看 Logs |
| PythonAnywhere 显示 `Something went wrong` | 看 Error log：通常是虚拟环境路径写错，或 `wsgi.py` 里路径没改成自己的用户名 |
| 改动后网站没变化 | Render：重新部署（push 新 commit 会自动触发）；PythonAnywhere：先 `git pull` 再点 Reload |
| 数据全没了 | Render 免费档的 SQLite 存在临时磁盘，重启即重置；换 PythonAnywhere 或加付费磁盘 |
| `git push` 报 Authentication failed | 用 Personal Access Token 代替密码（见第 1 步） |
| `git` 不是内部或外部命令 | Git 没装好或 PyCharm 没重启，回到第 0 步 |

---

## 附：不想用 Git 也能部署（备选）

- **PythonAnywhere**：Web 页面有 "Upload a file"，可以打包上传 zip，再在 Bash 里 `unzip`。但后续更新麻烦，不推荐。
- **本地公网临时链接**：`cloudflared tunnel --url http://127.0.0.1:5000`（见 INSTALL.md 第 8 节），适合当天演示，不是永久链接。

---

## 部署文件说明（老师问起可以这样答）

| 文件 | 作用 |
|---|---|
| `wsgi.py` | 生产环境入口，暴露 `application` 给 gunicorn/uWSGI |
| `Procfile` | 平台通用的启动命令：先跑幂等的 `seed.py`，再用 gunicorn 起 2 worker × 4 线程 |
| `render.yaml` | Render 蓝图：构建、启动命令与环境变量（自动生成 SECRET_KEY） |
| `runtime.txt` / `.python-version` | 固定 Python 3.11 |
| `requirements.txt` | 依赖清单，含生产服务器 `gunicorn` |
| `.gitignore` | 排除虚拟环境、数据库、缓存、密钥，避免把 132 KB 的 sqlite 和 3 万个 venv 文件推到仓库 |
