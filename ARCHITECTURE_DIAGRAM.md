# 🏗️ Transactions Feature - Architecture Diagram

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER/ADMIN BROWSER                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  User Request: /payment/history/?period=month&download=1      │
│  OR                                                             │
│  Admin Request: /dashboard/payments/?period=week              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                         DJANGO URLS                             │
├─────────────────────────────────────────────────────────────────┤
│  urlpatterns = [                                               │
│    path('payment/history/', payment_history, name='...'),      │
│    path('dashboard/payments/', admin_payment_history, name=''), │
│  ]                                                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                       DJANGO VIEWS                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  payment_history(request)          admin_payment_history()    │
│  ├─ @login_required               ├─ @login_required          │
│  ├─ Get period parameter          ├─ @user_passes_test()      │
│  ├─ Get user payments             ├─ Get all payments         │
│  └─ Handle download               └─ Handle download          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              TRANSACTIONS UTILITY (transactions.py)             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─ TransactionManager                                         │
│  │  ├─ get_date_range(period)                                 │
│  │  │  └─ Returns: (start_date, end_date) tuple               │
│  │  │                                                           │
│  │  ├─ filter_transactions(queryset, period)                  │
│  │  │  └─ Returns: Filtered queryset by date range            │
│  │  │                                                           │
│  │  ├─ get_transaction_stats(transactions)                    │
│  │  │  └─ Returns: {count, total, completed, average, ...}   │
│  │  │                                                           │
│  │  ├─ export_to_csv(transactions, period)                    │
│  │  │  └─ Returns: CSV string content                          │
│  │  │                                                           │
│  │  └─ export_to_csv_response(transactions, period, filename) │
│  │     └─ Returns: HTTP file download response                │
│  │                                                              │
│  └─ get_transaction_context(user, admin)                       │
│     └─ Returns: Context data for all periods                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      DATABASE (Models)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Payment Model Queries:                                        │
│  ├─ Payment.objects.filter(user=user)                         │
│  ├─ Payment.objects.filter(created_at__range=[...])           │
│  ├─ Payment.objects.filter(status='completed')                │
│  └─ Payment.objects.all()                                      │
│                                                                 │
│  Related Models:                                               │
│  ├─ User (Foreign Key)                                        │
│  ├─ SubscriptionPlan (Foreign Key)                            │
│  └─ Coupon (Foreign Key, nullable)                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      TEMPLATES                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  payment_history.html                admin_payment_history.html │
│  ├─ Period tabs                      ├─ Period tabs           │
│  ├─ Stats cards                      ├─ Download button       │
│  ├─ Download button                  ├─ Stats display         │
│  ├─ Transaction table                ├─ Filters               │
│  └─ Custom CSS                       ├─ Analytics tables      │
│                                       └─ Custom CSS            │
│                                                                 │
│  Uses custom_filters:                                          │
│  ├─ {{ dict|get_item:key }}  - Access dict in template       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     HTTP RESPONSE                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Option 1: HTML View                                           │
│  ├─ Status: 200 OK                                             │
│  ├─ Content-Type: text/html                                   │
│  └─ Body: Rendered HTML template                              │
│                                                                 │
│  Option 2: CSV Download                                        │
│  ├─ Status: 200 OK                                             │
│  ├─ Content-Type: text/csv                                    │
│  ├─ Content-Disposition: attachment; filename="..."           │
│  └─ Body: CSV file content                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     USER BROWSER                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Display rendered dashboard OR download CSV file              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagram

```
START: User navigates to /payment/history/
   │
   ├─ @login_required
   │  └─ Check: User authenticated?
   │     ├─ NO  → Redirect to login
   │     └─ YES → Continue
   │
   ├─ Parse query parameters
   │  ├─ period = 'week' (default: 'all')
   │  └─ download = '1' (optional)
   │
   ├─ Check: download parameter?
   │  │
   │  ├─ YES → CSV Download Flow
   │  │  │
   │  │  ├─ Get user payments
   │  │  │  └─ Payment.objects.filter(user=request.user)
   │  │  │
   │  │  ├─ Filter by period
   │  │  │  └─ TransactionManager.filter_transactions(payments, period)
   │  │  │
   │  │  ├─ Generate CSV
   │  │  │  └─ TransactionManager.export_to_csv(filtered)
   │  │  │
   │  │  └─ Return file response
   │  │     └─ HttpResponse(csv_content, content_type='text/csv')
   │  │
   │  └─ NO → Normal View Flow
   │     │
   │     ├─ Get all user payments
   │     │  └─ Payment.objects.filter(user=request.user)
   │     │
   │     ├─ For each period in ['week', 'month', 'year', 'all']
   │     │  │
   │     │  ├─ Filter transactions
   │     │  │  └─ TransactionManager.filter_transactions(payments, p)
   │     │  │
   │     │  ├─ Calculate stats
   │     │  │  └─ TransactionManager.get_transaction_stats(filtered)
   │     │  │
   │     │  └─ Store in period_data dict
   │     │
   │     ├─ Filter by selected period
   │     │  └─ displayed_payments = period_data[current_period]
   │     │
   │     ├─ Build context
   │     │  ├─ payments = filtered_payments
   │     │  ├─ period_data = all_periods_data
   │     │  ├─ stats = current_period_stats
   │     │  ├─ current_period = period
   │     │  └─ periods = ['week', 'month', 'year', 'all']
   │     │
   │     └─ Render template
   │        └─ render(request, 'payment_history.html', context)
   │
END: User receives response
```

---

## Period Filtering Logic

```
Period Selected: 'month'
        ↓
get_date_range('month')
        ↓
    now = timezone.now()      ← 2026-05-25 14:30:00
    start = now - timedelta(days=30)  ← 2026-04-25 14:30:00
    return (start, now)
        ↓
filter_transactions(queryset, 'month')
        ↓
    queryset.filter(created_at__range=[start, now])
        ↓
    Only transactions between 2026-04-25 and 2026-05-25
```

---

## CSV Export Process

```
Input: Filtered transactions queryset
   ↓
Create StringIO buffer
   ↓
Create CSV writer
   ↓
Write header row:
│ Transaction ID | User | Plan | Amount | Discount | ... │
   ↓
For each transaction:
│ TXN-123 | john | Premium | 499 | 49.9 | 449.1 | ... │
   ↓
Get CSV string from buffer
   ↓
Create HTTP response:
│ Content-Type: text/csv
│ Content-Disposition: attachment; filename="..."
│ Body: CSV content
   ↓
Return response to browser
   ↓
Browser downloads file
```

---

## Period Statistics Calculation

```
Transactions: [txn1, txn2, txn3, txn4, txn5]

COUNT:
└─ len(transactions) = 5

COMPLETED:
└─ filter(status='completed') = [txn1, txn2, txn3]
   count = 3

TOTAL REVENUE:
└─ sum(txn.final_amount for completed) = ₹1200

TOTAL DISCOUNT:
└─ sum(txn.discount_amount for completed) = ₹120

AVERAGE:
└─ total_revenue / completed_count = 1200 / 3 = ₹400

RESULT:
│ count: 5
│ completed: 3
│ total: 1200
│ total_discount: 120
│ average: 400
│ pending: 1
│ failed: 1
```

---

## Admin vs User Access

```
┌─────────────────────────────────────────┐
│           REQUEST COMES IN              │
├─────────────────────────────────────────┤
│  URL: /payment/history/  OR             │
│  URL: /dashboard/payments/              │
└─────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────┐
│     CHECK: user.is_authenticated?       │
├─────────────────────────────────────────┤
│  NO  → Redirect to /login/              │
│  YES → Continue                         │
└─────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────┐
│  CHECK: user.is_staff (for /dash.../)?  │
├─────────────────────────────────────────┤
│  YES → Show admin view                  │
│       payments = Payment.objects.all()  │
│       └─ Can see ALL user transactions  │
│                                          │
│  NO  → Show user view                   │
│       payments = Payment.objects        │
│                 .filter(user=user)      │
│       └─ Can see ONLY OWN transactions  │
└─────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────┐
│         RENDER TEMPLATE                 │
└─────────────────────────────────────────┘
```

---

## Template Rendering Flow

```
Context Data passed to template:
│
├─ payments: [Paginated transaction list]
├─ current_period: 'month'
├─ periods: ['week', 'month', 'year', 'all']
│
├─ period_data:
│  ├─ 'week':
│  │  ├─ count: 10
│  │  ├─ total: 5000
│  │  └─ display_name: 'Last 7 Days (Weekly)'
│  │
│  ├─ 'month':
│  │  ├─ count: 45
│  │  ├─ total: 22500
│  │  └─ display_name: 'Last 30 Days (Monthly)'
│  │
│  └─ ... (more periods)
│
└─ stats: [Current period statistics]
        ↓
        Template processes:
        ├─ Loop: {% for period in periods %}
        │  └─ Render period tab: {{ period_data|get_item:period|get_item:'count' }}
        │
        ├─ Display stats: {{ stats.total }}
        │
        ├─ Loop: {% for payment in payments %}
        │  └─ Render row: {{ payment.transaction_id }}, {{ payment.amount }}, ...
        │
        └─ Download button:
           href="?period={{ current_period }}&download=1"
        ↓
        Final HTML rendered and sent to browser
```

---

## Security Flow

```
┌─────────────────────────────────────────┐
│           REQUEST ARRIVES               │
└─────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────┐
│   @login_required decorator             │
│   └─ Check: session.user exists?        │
│      NO  → Redirect /login/             │
│      YES → Continue to view             │
└─────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────┐
│   @user_passes_test(is_admin)           │
│   [Admin views only]                    │
│   └─ Check: user.is_staff?              │
│      NO  → Redirect /                   │
│      YES → Continue to view             │
└─────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────┐
│   Query filtering                       │
│   ├─ User view:                         │
│   │  Payment.objects.filter(user=      │
│   │      request.user)                 │
│   │  └─ Only own transactions          │
│   │                                     │
│   └─ Admin view:                        │
│      Payment.objects.all()              │
│      └─ All transactions               │
└─────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────┐
│   Response generation                   │
│   └─ Return appropriate data            │
└─────────────────────────────────────────┘
```

---

## Key Decision Points

```
User Request
    ↓
Is user logged in?
├─ NO  → Redirect to login
└─ YES → Continue
         ↓
         Is admin view?
         ├─ YES → Is user.is_staff?
         │       ├─ NO  → Redirect to home
         │       └─ YES → Show admin dashboard
         │
         └─ NO  → Show user dashboard (always)
                  ↓
                  Download requested?
                  ├─ YES → Generate & stream CSV
                  └─ NO  → Render HTML template
```

---

**Architecture Status: ✅ PRODUCTION READY**

This modular design ensures:
- Clean separation of concerns
- Easy to test individual components
- Simple to extend in future
- Secure by default
- Efficient database queries
