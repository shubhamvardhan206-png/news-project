# 🚀 PythonAnywhere Deployment Guide

## Step 1: Create PythonAnywhere Account
1. Go to https://www.pythonanywhere.com
2. Sign up with your email
3. Verify email
4. Choose **Beginner** account (free tier available)

---

## Step 2: Set Up via Web Console

1. **Log in** to PythonAnywhere dashboard
2. Go to **Consoles** → Click **+ New console**
3. Select **Bash** console
4. Run these commands:

```bash
# Clone your GitHub repository
cd ~
git clone https://github.com/shubhamvardhan206-png/news-project.git
cd news-project

# Create a virtual environment
mkvirtualenv newsproject --python=/usr/bin/python3.10

# Install dependencies
pip install -r newsproject/requirements.txt

# Navigate to Django project
cd newsproject

# Create/migrate database
python manage.py migrate

# Create superuser (admin)
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

---

## Step 3: Configure Web App

1. Go to **Web** tab in PythonAnywhere
2. Click **+ Add a new web app**
3. Select **Manual configuration**
4. Choose **Python 3.10**
5. Click through to finish

---

## Step 4: Configure WSGI File

1. In the **Web** tab, find your web app (e.g., `yourusername.pythonanywhere.com`)
2. Under **WSGI configuration file**, click the link to edit
3. **Replace the entire file** with this:

```python
# WSGI config for PythonAnywhere
import os
import sys
from pathlib import Path

# Add your project directory to sys.path
project_home = '/home/yourusername/news-project'
sys.path.insert(0, project_home)
sys.path.insert(0, os.path.join(project_home, 'newsproject'))

# Set Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'newsproject.settings'
os.environ['DEBUG'] = 'False'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**⚠️ IMPORTANT:** Replace `yourusername` with your actual PythonAnywhere username!

---

## Step 5: Set Up Static Files

1. In the **Web** tab, scroll to **Static files** section
2. Add this mapping:

| URL path | Directory |
|----------|-----------|
| `/static/` | `/home/yourusername/news-project/newsproject/staticfiles` |

3. Click **Save**

---

## Step 6: Set Up Virtual Environment Path

1. In the **Web** tab, find **Virtualenv path**
2. Set it to: `/home/yourusername/.virtualenvs/newsproject`
3. Click **Save**

---

## Step 7: Reload Web App

1. In the **Web** tab, click **Reload yourusername.pythonanywhere.com**
2. Wait 30 seconds for reload to complete

---

## Step 8: Access Your Site

Visit: `https://yourusername.pythonanywhere.com`

If you see **DisallowedHost** error:
- Go back to settings and check ALLOWED_HOSTS includes your domain ✅ (Already done!)

---

## Troubleshooting

**Error: ModuleNotFoundError**
- Check virtualenv path is set correctly
- Ensure WSGI file has correct path

**Error: Static files not loading**
- Run: `python manage.py collectstatic --noinput` from Bash console
- Check static files URL mapping in Web tab

**Error: Database locked**
- Your free tier uses SQLite (single-user)
- Upgrade to paid for PostgreSQL (optional)

**Site shows 500 error**
- Check **Error log** in Web tab
- Check **Server log** for details

---

## Next: Custom Domain (Optional)

If you want a custom domain:
1. Go to **Web** → **Custom domains**
2. Add your domain
3. Update DNS records with PythonAnywhere's instructions

---

## Important Notes

- ✅ ALLOWED_HOSTS already includes `*.pythonanywhere.com`
- ✅ DEBUG set to False in production
- ✅ Database migrations run automatically
- Free tier: Restarts daily at 6 AM UTC
- Free tier: Limited to 100 MB storage

---

**Questions?** Check https://help.pythonanywhere.com
