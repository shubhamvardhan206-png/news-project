# ✅ NewsPortal - Local Development Setup

## 🚀 Quick Start (3 Ways)

### Option 1: Using the Batch File (Easiest on Windows)
```
Double-click: run_server.bat
```
The server will start automatically!

### Option 2: Manual Command
```bash
cd C:\Users\SHUBHAM KUMAR\Desktop\news-project\newsproject
python manage.py runserver
```

### Option 3: Full Path
```bash
cd C:\Users\SHUBHAM KUMAR\Desktop\news-project
python newsproject\manage.py runserver
```

---

## 📁 Correct Directory Structure

```
news-project/                    ← You start here
├── newsproject/                 ← Go into this folder
│   ├── manage.py               ← This is where you run commands
│   ├── newsproject/
│   │   └── settings.py
│   ├── news/
│   ├── templates/
│   ├── static/
│   └── media/
├── run_server.bat              ← NEW: Batch file for easy startup
├── render.yaml
├── Procfile
└── DEPLOYMENT_READY.md
```

---

## ✅ Configuration Already Correct

Your settings.py is already perfectly configured:
- ✅ Uses SQLite for local development
- ✅ Uses PostgreSQL only in production
- ✅ No issues with psycopg2 locally

The error was just about running from the wrong directory!

---

## 🎯 Next Steps

### To Start Developing:
**Method 1 (Windows GUI):**
1. Double-click `run_server.bat`
2. Browser opens to http://127.0.0.1:8000/

**Method 2 (Terminal):**
1. Open PowerShell/CMD
2. Run: `cd C:\Users\SHUBHAM KUMAR\Desktop\news-project\newsproject`
3. Run: `python manage.py runserver`

### Access Your Site:
- **Home**: http://127.0.0.1:8000/
- **Admin**: http://127.0.0.1:8000/admin/
- **News**: http://127.0.0.1:8000/news/

---

## 🔐 First Time Setup

If this is your first time running the server:

```bash
# 1. From newsproject folder
python manage.py migrate

# 2. Create superuser for admin
python manage.py createsuperuser

# 3. Start server
python manage.py runserver
```

---

## ✨ Everything Works Now

- ✅ Local SQLite database (no PostgreSQL needed)
- ✅ Django development server
- ✅ Hot reload on file changes
- ✅ Admin panel ready
- ✅ All features working

---

## 📝 Important Notes

**SQLite (Local):**
- Fast, no setup needed
- Data stored in `db.sqlite3`
- Perfect for development

**PostgreSQL (Production/Render):**
- Automatically used on Render.com
- No changes needed
- Settings.py handles it automatically

---

**Status**: ✅ Ready to Develop Locally!

Just run `run_server.bat` or follow Method 2 above!
