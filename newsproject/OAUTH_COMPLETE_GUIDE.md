# Complete OAuth Setup Guide for News Portal

## Quick Start (5 Minutes)

### 1️⃣ **Google OAuth Setup**

#### Step 1: Get Google Credentials
- Go to: https://console.cloud.google.com/
- Click **Create Project** (top right)
- Name it "NewsPortal"
- Go to **APIs & Services** → **Enabled APIs & Services**
- Click **+ ENABLE APIS AND SERVICES**
- Search for **"Google+ API"** → Enable it
- Go back to **Credentials** → **+ Create Credentials**
- Choose **OAuth 2.0 Client ID** → **Web Application**
- Fill in:
  - **Name**: NewsPortal Web Client
  - **Authorized JavaScript origins**: `http://127.0.0.1:8000`
  - **Authorized redirect URIs**: `http://127.0.0.1:8000/accounts/google/login/callback/`
- Click Create and **copy Client ID & Secret**

#### Step 2: Add to Django Admin
1. Go to: http://127.0.0.1:8000/admin/
2. Go to **Sites** → Edit the existing site:
   - Domain: `127.0.0.1:8000`
   - Name: `NewsPortal`
3. Go to **Social applications** → **+ Add**
4. Fill:
   - **Provider**: Google
   - **Name**: Google OAuth
   - **Client id**: (paste from Google)
   - **Secret key**: (paste from Google)
   - **Sites**: Select `127.0.0.1:8000`
5. **Save**

---

### 2️⃣ **Facebook OAuth Setup**

#### Step 1: Get Facebook Credentials
- Go to: https://developers.facebook.com/
- Click **My Apps** → **Create App** (top right)
- Choose **Consumer** as type
- Fill app name "NewsPortal" and continue
- Go to **Settings** → **Basic** (copy App ID & App Secret)
- Go to **Facebook Login** → **Settings**
- Add **Valid OAuth Redirect URIs**:
  ```
  http://127.0.0.1:8000/accounts/facebook/login/callback/
  ```
- Go to **Settings** → **Basic** → Add **App Domains**:
  ```
  127.0.0.1
  ```
- Go to **Facebook Login** → **Settings** → Add these URLs:
  - **Valid OAuth Redirect URIs**: `http://127.0.0.1:8000/accounts/facebook/login/callback/`

#### Step 2: Add to Django Admin
1. Go to: http://127.0.0.1:8000/admin/
2. Go to **Social applications** → **+ Add**
3. Fill:
   - **Provider**: Facebook
   - **Name**: Facebook OAuth
   - **Client id**: (paste App ID from Facebook)
   - **Secret key**: (paste App Secret)
   - **Sites**: Select `127.0.0.1:8000`
4. **Save**

---

## Test Your Setup

1. Go to http://127.0.0.1:8000/login/
2. You should see **"Sign in with Google"** and **"Sign in with Facebook"** buttons
3. Click to test

---

## For Production (Render/PythonAnywhere)

### Update Redirect URIs

**For Render:** https://your-app-name.onrender.com
- Google: Add `https://your-app-name.onrender.com/accounts/google/login/callback/`
- Facebook: Add `https://your-app-name.onrender.com/accounts/facebook/login/callback/`

**For PythonAnywhere:** https://yourusername.pythonanywhere.com
- Google: Add `https://yourusername.pythonanywhere.com/accounts/google/login/callback/`
- Facebook: Add `https://yourusername.pythonanywhere.com/accounts/facebook/login/callback/`

### Update Django Admin
- Go to **Sites** → Change domain to your production domain
- Update **Social applications** sites

---

## Share Subscription Links with Users

### Sharing URLs:

**Subscription Plans Page:**
```
http://127.0.0.1:8000/plans/
```

**User Payment History:**
```
http://127.0.0.1:8000/payment/history/
```

**Login Page (with OAuth):**
```
http://127.0.0.1:8000/login/
```

### Share These Steps with Users:

1. **Sign Up**: Click "Sign in with Google" or "Sign in with Facebook"
2. **Choose Plan**: Go to `/plans/` and select a subscription
3. **Add UPI**: Save your UPI ID for payments
4. **Enter Coupon** (optional): Use discount codes like SAVE10
5. **Pay**: Scan QR code and enter transaction ID
6. **Enjoy**: Immediate access to premium content

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "OAuth client not found" | Check Django admin → Social applications (create one) |
| "Redirect URI mismatch" | Match exact URL in OAuth app settings with Django |
| Facebook login not showing | Go to Facebook Developer app → Ensure "Facebook Login" product is added |
| Google login error | Ensure Google+ API is **enabled** in Google Cloud Console |
| "Site not found" | Go to admin → Sites → Make sure domain matches exactly |

---

## Share With Users (Template Message):

```
Join our premium content community!

📖 Read Premium Articles
💬 Access Exclusive Discussions  
🎬 Watch Member-Only Videos

Get started:
1. Sign up: http://127.0.0.1:8000/login/
2. Choose plan: http://127.0.0.1:8000/plans/
3. Use coupon: SAVE10 for 10% off

Questions? Check payment history at:
http://127.0.0.1:8000/payment/history/
```

