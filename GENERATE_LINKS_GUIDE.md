# Quick Guide: Generate & Share Payment Links

## Step 1: Start Your Server
Run the batch file:
```
C:\Users\SHUBHAM KUMAR\Desktop\news-project\run_server.bat
```
Or manually:
```
cd C:\Users\SHUBHAM KUMAR\Desktop\news-project\newsproject
python manage.py runserver
```
✅ Visit: http://localhost:8000/

---

## Step 2: Login as Admin
1. Go to: http://localhost:8000/admin/
2. Login with your admin credentials

---

## Step 3: Generate Shareable Links
1. In admin, go to: **Dashboard** > **Share Links** 
   - Direct link: http://localhost:8000/dashboard/share-links/

2. You will see a table with all your plans and coupons

3. **Copy any link** by clicking the "Copy" button

---

## Example Links (Replace localhost with your domain)

### Without Coupon:
```
http://localhost:8000/subscribe/1/
http://localhost:8000/subscribe/2/
http://localhost:8000/subscribe/3/
```

### With Your 3 Coupons:
```
http://localhost:8000/subscribe/1/?coupon=CODE1
http://localhost:8000/subscribe/2/?coupon=CODE2
http://localhost:8000/subscribe/3/?coupon=CODE3
```

Replace:
- **localhost:8000** → Your actual domain (e.g., yourdomain.com)
- **CODE1, CODE2, CODE3** → Your actual coupon codes from admin

---

## Step 4: Share with Users

**Option A: Email** (Use template in Share Links page)
```
Subject: 🎉 Exclusive Subscription Offer - Get Discounts!

Hi there,

Get premium access with a special discount!

👉 Click here: http://localhost:8000/subscribe/1/?coupon=SAVE20
Price: ₹99 → ₹79 (20% off)

Subscribe now!
```

**Option B: WhatsApp / SMS**
```
🎊 LIMITED TIME OFFER! 🎊

Get premium news access!

📰 Subscribe: http://localhost:8000/subscribe/1/?coupon=SAVE20

Don't miss out! 👉
```

**Option C: Social Media / Website**
```
Special offer for our readers! 
Use code: SAVE20 
Get 20% discount on Premium subscription
Link: http://localhost:8000/subscribe/1/?coupon=SAVE20
```

---

## Step 5: Check Payment Details

### Option 1: Admin Dashboard
1. Go to: http://localhost:8000/admin/news/payment/
2. See all payments with:
   - User name
   - Amount paid
   - Coupon used
   - Payment status
   - Date & time

### Option 2: Custom Payment Dashboard
1. Go to: http://localhost:8000/dashboard/subscriptions/
2. See:
   - All active subscriptions
   - Recent payments
   - Total revenue
   - Payment statistics

### Option 3: User Payment History
1. Go to: http://localhost:8000/dashboard/user/USER_ID/subscription/
2. Replace USER_ID with actual user ID
3. See all payments by that user

---

## What Users See When They Click the Link

1. They visit your link (with coupon auto-applied)
2. They see subscription confirm page
3. Coupon is auto-applied at checkout
4. They save UPI ID
5. They scan QR code and make payment
6. Payment is recorded in admin with coupon info

---

## Your 3 Coupon Codes

Go to: http://localhost:8000/admin/news/coupon/

You should see your 3 coupons with codes like:
- CODE1 (20% off)
- CODE2 (₹100 off)
- CODE3 (15% off)

Use these in your shareable links!

---

## Production (Real Domain)

When you deploy to production (Render, PythonAnywhere, etc.):

Replace all **localhost:8000** with your actual domain:
- **localhost:8000** → **yourdomain.com**
- **localhost:8000** → **news.example.com**

Example production links:
```
https://yourdomain.com/subscribe/1/?coupon=SAVE20
https://yourdomain.com/dashboard/share-links/
https://yourdomain.com/admin/news/payment/
```

---

## Summary

✅ Go to: /dashboard/share-links/ → Copy links → Share with users
✅ Users click link → Coupon auto-applies → They pay
✅ Check payments: /admin/news/payment/
✅ Track revenue: /dashboard/subscriptions/

That's it! 🚀
