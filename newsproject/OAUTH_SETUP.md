# OAuth Setup Guide - Google & Facebook

## Step 1: Google OAuth Setup

### 1.1 Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Go to **APIs & Services** → **Credentials**
4. Click **Create Credentials** → **OAuth 2.0 Client ID**
5. Choose **Web Application**
6. Add Authorized redirect URIs:
   ```
   http://127.0.0.1:8000/accounts/google/login/callback/
   http://localhost:8000/accounts/google/login/callback/
   ```
7. Copy the **Client ID** and **Client Secret**

### 1.2 Add to Django Admin

1. Login to Django admin: `http://127.0.0.1:8000/admin/`
2. Go to **Sites** and make sure you have:
   - Domain: `127.0.0.1:8000`
   - Name: `NewsPortal`
3. Go to **Social applications** and click **Add**
4. Fill in:
   - **Provider**: Google
   - **Name**: Google
   - **Client ID**: (paste from Google Console)
   - **Secret key**: (paste from Google Console)
   - **Sites**: Select your site
5. Save

---

## Step 2: Facebook OAuth Setup

### 2.1 Create Facebook App

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Click **My Apps** → **Create App**
3. Choose **Consumer** as app type
4. Fill app details and create
5. Go to **Settings** → **Basic** (copy App ID and App Secret)
6. Go to **Facebook Login** → **Settings**
7. Add Valid OAuth Redirect URIs:
   ```
   http://127.0.0.1:8000/accounts/facebook/login/callback/
   http://localhost:8000/accounts/facebook/login/callback/
   ```

### 2.2 Add to Django Admin

1. Go to Django admin → **Social applications** → **Add**
2. Fill in:
   - **Provider**: Facebook
   - **Name**: Facebook
   - **Client ID**: (App ID from Facebook)
   - **Secret key**: (App Secret)
   - **Sites**: Select your site
3. Save

---

## Step 3: Update Django Settings (if needed)

Your `settings.py` should have:

```python
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'APP': {
            'client_id': 'YOUR_CLIENT_ID',
            'secret': 'YOUR_SECRET',
            'key': ''
        }
    },
    'facebook': {
        'METHOD': 'oauth2',
        'SCOPE': ['email', 'public_profile'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'INIT_PARAMS': {'cookie': True},
        'FIELDS': [
            'id',
            'email',
            'name',
            'picture',
            'verified'
        ],
        'EXCHANGE_TOKEN': True,
        'VERIFIED_EMAIL': True,
        'VERSION': 'v13.0',
    }
}

SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'
```

---

## Step 4: For Production (Important!)

Update redirect URIs when deploying:

**For Render:**
```
https://your-app-name.onrender.com/accounts/google/login/callback/
https://your-app-name.onrender.com/accounts/facebook/login/callback/
```

**For PythonAnywhere:**
```
https://yourusername.pythonanywhere.com/accounts/google/login/callback/
https://yourusername.pythonanywhere.com/accounts/facebook/login/callback/
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "OAuth client not found" | Check Django admin → Social applications (make sure it's created) |
| Redirect URI mismatch | Make sure redirect URIs in OAuth app exactly match Django URLs |
| Site not found | Go to Django admin → Sites and ensure domain matches |
| Users can't login | Check SOCIALACCOUNT_AUTO_SIGNUP = True in settings |

