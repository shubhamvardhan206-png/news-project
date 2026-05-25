# Payment & Coupon Sharing System - Complete Guide

## Overview
This guide explains how to:
1. **Generate and share coupon codes** with users
2. **Create payment links** for subscriptions
3. **Track and view payment details** in admin dashboard

---

## Part 1: Creating & Sharing Coupons

### Step 1: Create Coupons in Admin Panel

1. Go to: `http://localhost:8000/admin/news/coupon/`
2. Click **"Add Coupon"**
3. Fill in the details:

```
Code: SAVE20
Discount Percent: 20 (or Discount Amount: 200)
Valid From: Today's date
Valid Until: Date when coupon expires
Is Active: ✓ (checked)
Max Uses: 100 (or leave blank for unlimited)
Applicable Plans: Select specific plans (or leave empty for all plans)
Description: Get 20% discount on all plans
```

### Step 2: Share Coupon with Users

**Option A: Direct Link (Share this URL)**
```
https://yoursite.com/plans/?coupon=SAVE20
```

**Option B: Email Template**
```
Subject: 🎉 Exclusive Discount - 20% Off Subscription

Dear User,

Use coupon code: SAVE20
Get 20% discount on all subscription plans!

👉 Use Coupon: https://yoursite.com/plans/?coupon=SAVE20

Valid until: [DATE]
```

**Option C: Social Media / WhatsApp**
```
🎊 LIMITED TIME OFFER! 🎊
Get 20% OFF subscription with code: SAVE20
Use here: [yoursite.com/plans]
Hurry! Offer expires on [DATE]
```

### Step 3: Copy Coupon Code to Share
Go to Admin > Coupons and copy the **Coupon Code** field and share via:
- Email
- WhatsApp
- Telegram
- Social Media
- SMS

---

## Part 2: Payment Links for Users

### Method 1: Direct Subscription Plan Link
Share these links with users:

```
https://yoursite.com/plans/                    # View all plans
https://yoursite.com/subscribe/1/              # Subscribe to plan with ID 1
```

**With Coupon:**
```
https://yoursite.com/subscribe/1/?coupon=SAVE20
```

### Method 2: API Endpoint to Generate Payment Links
Add this to your `news/views.py`:

```python
@login_required
def generate_payment_link(request, plan_id):
    """Generate shareable payment link for a plan"""
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    coupon = request.GET.get('coupon', '')
    
    # Create unique payment link
    link = f"{request.build_absolute_uri('/subscribe/')}{plan.id}/"
    if coupon:
        link += f"?coupon={coupon}"
    
    return JsonResponse({
        'link': link,
        'plan': plan.name,
        'price': str(plan.price),
        'coupon': coupon or None
    })
```

Add to `urls.py`:
```python
path('payment-link/<int:plan_id>/', views.generate_payment_link, name='generate_payment_link'),
```

---

## Part 3: Admin Dashboard - View Payment Details

### Option 1: Built-in Django Admin

Go to: `http://localhost:8000/admin/news/payment/`

You can see:
- ✅ User name
- ✅ Transaction ID
- ✅ Amount paid
- ✅ Payment status (Pending, Completed, Failed, Refunded)
- ✅ Payment method (UPI, Card, etc.)
- ✅ Date & time
- ✅ Coupon used (if any)
- ✅ Discount applied

**Features:**
- Click any payment to see full details
- Edit status directly from list
- Search by username or transaction ID
- Filter by status and date

### Option 2: Custom Admin Dashboard View

Add this to your `news/views.py`:

```python
from django.db.models import Sum, Count
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def payment_dashboard(request):
    """Admin dashboard with payment analytics"""
    
    # Payment stats
    total_payments = Payment.objects.filter(status='completed').count()
    total_revenue = Payment.objects.filter(
        status='completed'
    ).aggregate(Sum('final_amount'))['final_amount__sum'] or 0
    pending_payments = Payment.objects.filter(status='pending').count()
    failed_payments = Payment.objects.filter(status='failed').count()
    
    # Recent payments
    recent_payments = Payment.objects.select_related(
        'user', 'plan', 'coupon'
    ).order_by('-created_at')[:20]
    
    # Revenue by plan
    revenue_by_plan = Payment.objects.filter(
        status='completed'
    ).values('plan__name').annotate(
        total=Sum('final_amount'),
        count=Count('id')
    )
    
    # Most used coupons
    top_coupons = Coupon.objects.order_by('-times_used')[:10]
    
    return render(request, 'admin/payment_dashboard.html', {
        'total_payments': total_payments,
        'total_revenue': total_revenue,
        'pending_payments': pending_payments,
        'failed_payments': failed_payments,
        'recent_payments': recent_payments,
        'revenue_by_plan': revenue_by_plan,
        'top_coupons': top_coupons,
    })

@staff_member_required
def user_payment_history(request, user_id):
    """View all payments for a specific user"""
    user = get_object_or_404(User, id=user_id)
    payments = Payment.objects.filter(user=user).select_related(
        'plan', 'coupon'
    ).order_by('-created_at')
    
    total_spent = payments.filter(
        status='completed'
    ).aggregate(Sum('final_amount'))['final_amount__sum'] or 0
    
    return render(request, 'admin/user_payment_history.html', {
        'user': user,
        'payments': payments,
        'total_spent': total_spent,
    })
```

Add to `urls.py`:
```python
path('dashboard/payment-analytics/', views.payment_dashboard, name='payment_dashboard'),
path('dashboard/user/<int:user_id>/payments/', views.user_payment_history, name='user_payment_history'),
```

---

## Part 4: Coupon Management API

### Create API to Check Coupon Validity
Add to `news/views.py`:

```python
def validate_coupon(request):
    """API endpoint to validate coupon"""
    coupon_code = request.GET.get('code', '').strip()
    plan_id = request.GET.get('plan_id', '')
    
    if not coupon_code:
        return JsonResponse({'valid': False, 'error': 'No coupon code provided'})
    
    try:
        coupon = Coupon.objects.get(code=coupon_code)
        
        # Check if valid
        if not coupon.is_valid():
            return JsonResponse({
                'valid': False,
                'error': 'Coupon has expired or is no longer valid'
            })
        
        # Check if applicable to plan
        if plan_id and not coupon.can_apply_to_plan(
            SubscriptionPlan.objects.get(id=plan_id)
        ):
            return JsonResponse({
                'valid': False,
                'error': 'Coupon cannot be applied to this plan'
            })
        
        # Calculate discount
        if plan_id:
            plan = SubscriptionPlan.objects.get(id=plan_id)
            if coupon.discount_percent:
                discount = (float(plan.price) * coupon.discount_percent) / 100
            else:
                discount = float(coupon.discount_amount or 0)
            
            return JsonResponse({
                'valid': True,
                'code': coupon.code,
                'discount_percent': coupon.discount_percent,
                'discount_amount': str(discount),
                'final_price': str(float(plan.price) - discount),
                'description': coupon.description
            })
        
        return JsonResponse({
            'valid': True,
            'code': coupon.code,
            'discount_percent': coupon.discount_percent,
        })
        
    except Coupon.DoesNotExist:
        return JsonResponse({'valid': False, 'error': 'Invalid coupon code'})
```

Add to `urls.py`:
```python
path('api/validate-coupon/', views.validate_coupon, name='validate_coupon'),
```

**Usage (JavaScript in Frontend):**
```javascript
// Check coupon validity
fetch('/api/validate-coupon/?code=SAVE20&plan_id=1')
    .then(r => r.json())
    .then(data => {
        if (data.valid) {
            console.log(`Valid! Discount: ₹${data.discount_amount}`);
        } else {
            console.log(`Invalid: ${data.error}`);
        }
    });
```

---

## Part 5: Email Notifications

### Send Payment Confirmation Email

Add to `news/services.py`:

```python
from django.core.mail import send_mail
from django.conf import settings

def send_payment_confirmation(payment):
    """Send payment confirmation email to user"""
    
    subject = f"Payment Successful - {payment.user.first_name or 'User'}"
    
    message = f"""
    Hi {payment.user.first_name or payment.user.username},
    
    Your payment has been successfully processed!
    
    📋 Payment Details:
    - Transaction ID: {payment.transaction_id}
    - Plan: {payment.plan.name}
    - Amount: ₹{payment.amount}
    - Discount Applied: ₹{payment.discount_amount}
    - Final Amount: ₹{payment.final_amount}
    - Payment Status: {payment.status}
    - Date: {payment.created_at.strftime('%Y-%m-%d %H:%M:%S')}
    
    Your subscription is now active! Enjoy premium access.
    
    Thank you!
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [payment.user.email],
        fail_silently=False,
    )
```

Call this after payment is confirmed:
```python
if payment.status == 'completed':
    send_payment_confirmation(payment)
```

---

## Part 6: Quick Copy-Paste URLs

### Subscription Plans Page
```
https://yoursite.com/plans/
```

### Subscribe to Specific Plan
```
https://yoursite.com/subscribe/1/           # Plan ID 1
https://yoursite.com/subscribe/2/           # Plan ID 2
https://yoursite.com/subscribe/3/           # Plan ID 3
```

### With Coupon Code
```
https://yoursite.com/plans/?coupon=SAVE20
https://yoursite.com/subscribe/1/?coupon=SAVE20
```

### Admin Areas
```
https://yoursite.com/admin/news/payment/              # View all payments
https://yoursite.com/admin/news/coupon/               # Manage coupons
https://yoursite.com/admin/news/subscription/         # View subscriptions
https://yoursite.com/dashboard/payment-analytics/     # Payment dashboard
https://yoursite.com/dashboard/user/<USER_ID>/payments/  # User payment history
```

---

## Part 7: Testing Payment Flow

### Test Steps:
1. **Create a test coupon** in admin
2. **Share the link** with test email
3. **Login** and go to `/plans/`
4. **Apply coupon** (see discount calculated)
5. **Enter UPI ID** (test@upi or paytm@paytm)
6. **Enter transaction ID** (e.g., TXN123456)
7. **Check admin** to verify payment recorded

---

## Summary

✅ **Share Coupons:** Copy the coupon code → Share via email/WhatsApp/social media
✅ **Share Payment Links:** Send subscription plan URLs with coupon parameter
✅ **Track Payments:** Go to Django Admin → News → Payments
✅ **View User Payments:** Admin → Dashboard → User Payment History
✅ **Manage Coupons:** Admin → News → Coupons

That's it! You're ready to share and track payments! 🚀
