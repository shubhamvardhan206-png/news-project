from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count, Sum
from django.db import models
from django.utils import timezone
from datetime import timedelta
from .models import (
    Article, Category, Comment, Author, Like, Advertisement,
    SubscriptionPlan, UserSubscription, UserProfile, Payment, Coupon
)
import requests
from django.conf import settings
from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.urls import reverse
from urllib.parse import urlencode
from . import selectors, services
from .utils import generate_qr_code
from django.views.decorators.cache import cache_page
from .transactions import TransactionManager, get_transaction_context
import feedparser
from django.http import HttpResponse



# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def is_admin(user):
    """Check if user is admin"""
    return user.is_staff


def get_ads(position):
    """Get advertisement by position"""
    return Advertisement.objects.filter(position=position, is_active=True).first()


def get_news_from_api(category=None):
    """Fetch news from NewsAPI"""
    cache_key = f'news_api_{category or "all"}'
    cached = cache.get(cache_key)
    if cached:
        return cached

    api_key = settings.NEWS_API_KEY
    all_articles = []

    category_map = {
        'technology': 'technology',
        'sports': 'sports',
        'business': 'business',
        'entertainment': 'entertainment',
        'health': 'health',
        'science': 'science',
        'politics': 'general',
        'world': 'general',
    }

    news_category = category_map.get(category, 'general') if category else 'general'

    try:
        # India News
        r1 = requests.get('https://newsapi.org/v2/everything', params={
            'apiKey': api_key,
            'q': f'{news_category} India',
            'language': 'en',
            'sortBy': 'publishedAt',
            'pageSize': 6,
        })
        data1 = r1.json()
        if data1.get('status') == 'ok':
            for article in data1['articles']:
                article['source_region'] = '🇮🇳 India'
            all_articles += data1['articles']

        # World News
        r2 = requests.get('https://newsapi.org/v2/everything', params={
            'apiKey': api_key,
            'q': news_category,
            'language': 'en',
            'sortBy': 'publishedAt',
            'pageSize': 6,
        })
        data2 = r2.json()
        if data2.get('status') == 'ok':
            for article in data2['articles']:
                article['source_region'] = '🌍 World'
            all_articles += data2['articles']

        cache.set(cache_key, all_articles, 60 * 30)
        return all_articles

    except Exception as e:
        print("API ERROR:", e)
        return []


# ============================================================================
# MAIN VIEWS
# ============================================================================

def home(request):
    """Home page with articles and filters"""
    articles = Article.objects.all()
    categories = Category.objects.all()
    
    query = request.GET.get('query', '')
    category_slug = request.GET.get('category', '')

    if query:
        articles = articles.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(summary__icontains=query)
        )
    if category_slug:
        articles = articles.filter(category__slug=category_slug)

    api_news = get_news_from_api(category=category_slug if category_slug else None)
    featured = articles.first()
    trending = Article.objects.filter(is_published=True).order_by('-views')[:5]
    latest = articles[:12]
    banner_ads = Advertisement.objects.filter(position='banner_top', is_active=True)
    sidebar_ads = Advertisement.objects.filter(position='sidebar', is_active=True)

    return render(request, 'home.html', {
        'articles': latest,
        'featured': featured,
        'trending': trending,
        'categories': categories,
        'query': query,
        'active_category': category_slug,
        'banner_ads': banner_ads,
        'sidebar_ads': sidebar_ads,
        'api_news': api_news,
    })


def epaper(request):
    """E-Paper landing page (DB + API + RSS fallback)"""
    # 1) Manual mode / DB articles
    db_articles = Article.objects.filter(is_published=True).order_by('-created_at')[:20]

    # 2) API news (reuse existing NewsAPI integration)
    # Optional: allow filtering by category through query param
    category_slug = request.GET.get('category', '').strip() or None
    api_news = get_news_from_api(category=category_slug)

    # 3) RSS feed fallback (free/zero cost)
    # We keep it very light: fetch + extract minimal fields.
    rss_items = []
    try:
        import feedparser

        rss_urls = [
            # These are example RSS sources; you can update URLs any time.
            # They must be RSS/Atom endpoints.
            'https://indianexpress.com/indian-express-rss/',
            'https://www.thehindu.com/rss/india/?service=rss',
        ]

        for url in rss_urls:
            feed = feedparser.parse(url)
            for e in getattr(feed, 'entries', [])[:10]:
                rss_items.append({
                    'title': getattr(e, 'title', '')[:300],
                    'url': getattr(e, 'link', ''),
                    'publishedAt': str(getattr(e, 'published', '')),
                    'source': {'name': getattr(feed.feed, 'title', 'RSS')},
                    'urlToImage': getattr(e, 'image', None) and getattr(e.image, 'url', None),
                })
    except Exception as _e:
        rss_items = []

    # Simple cache-friendly slice for rendering performance
    api_news = api_news[:30] if api_news else []
    rss_items = rss_items[:30] if rss_items else []

    mode = (request.GET.get('mode') or 'both').lower()
    # mode: db | api | rss | both
    if mode == 'db':
        api_news = []
        rss_items = []
    elif mode == 'api':
        db_articles = Article.objects.none()
        rss_items = []
    elif mode == 'rss':
        db_articles = Article.objects.none()
        api_news = []
    elif mode == 'both':
        # keep all
        pass

    return render(request, 'epaper.html', {
        'db_articles': db_articles,
        'api_news': api_news,
        'rss_items': rss_items,
        'active_mode': mode,
        'categories': Category.objects.all(),
        'active_category': category_slug,
    })



def article_detail(request, slug):
    """Show single article with comments"""
    article = get_object_or_404(Article, slug=slug, is_published=True)
    article.views += 1
    article.save()
    related = Article.objects.filter(
        category=article.category, is_published=True
    ).exclude(id=article.id)[:3]
    comments = article.comments.all()
    liked = False
    if request.user.is_authenticated:
        liked = Like.objects.filter(article=article, user=request.user).exists()
    return render(request, 'article_detail.html', {
        'article': article,
        'related': related,
        'comments': comments,
        'liked': liked,
        'like_count': article.likes.count(),
        'ad_article_top': get_ads('article_top'),
        'ad_article_bottom': get_ads('article_bottom'),
        'ad_sidebar': get_ads('sidebar'),
    })


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin dashboard"""
    return render(request, 'admin_dashboard.html', {
        'total_articles': Article.objects.count(),
        'total_published': Article.objects.filter(is_published=True).count(),
        'total_comments': Comment.objects.count(),
        'total_likes': Like.objects.count(),
        'total_subscribers': UserSubscription.objects.filter(is_active=True).count(),
        'recent_articles': Article.objects.order_by('-created_at')[:10],
        'recent_comments': Comment.objects.order_by('-created_at')[:10],
        'top_articles': Article.objects.filter(is_published=True).order_by('-views')[:5],
        'categories': Category.objects.all(),
    })


def category_view(request, slug):
    """Show articles by category"""
    category = get_object_or_404(Category, slug=slug)
    articles = Article.objects.filter(category=category, is_published=True)
    api_news = get_news_from_api(category=slug)
    return render(request, 'category.html', {
        'category': category,
        'articles': articles,
        'categories': Category.objects.all(),
        'api_news': api_news,
        'active_category': slug,
        'ad_header': get_ads('banner_top'),
    })


def search_view(request):
    """Search articles"""
    query = request.GET.get('query', '')
    articles = []
    if query:
        articles = Article.objects.filter(
            title__icontains=query
        ) | Article.objects.filter(
            content__icontains=query
        )
    return render(request, 'search.html', {
        'articles': articles,
        'query': query
    })


@login_required
def add_comment(request, slug):
    """Add comment to article"""
    article = get_object_or_404(Article, slug=slug, is_published=True)
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Comment.objects.create(article=article, user=request.user, content=content)
            messages.success(request, 'Comment posted!')
        else:
            messages.error(request, 'Comment cannot be empty.')
    return redirect('article_detail', slug=slug)


@login_required
def like_article(request, slug):
    """Like/unlike article"""
    if request.method == 'POST':
        article = get_object_or_404(Article, slug=slug)
        like, created = Like.objects.get_or_create(article=article, user=request.user)
        if not created:
            like.delete()
            liked = False
        else:
            liked = True
        return JsonResponse({'liked': liked, 'count': article.likes.count()})
    return JsonResponse({'error': 'Invalid request'}, status=400)


def author_profile(request, author_id):
    """Show author profile and articles"""
    author = get_object_or_404(Author, id=author_id)
    articles = Article.objects.filter(author=author, is_published=True)
    return render(request, 'author_profile.html', {
        'author': author,
        'articles': articles,
        'categories': Category.objects.all(),
    })


def ad_click(request, ad_id):
    """Redirect to ad URL and increment click count"""
    ad = get_object_or_404(Advertisement, id=ad_id)
    ad.clicks += 1
    ad.save()
    return redirect(ad.url or '/')


# ============================================================================
# AUTHENTICATION VIEWS
# ============================================================================

def register_view(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {
        'form': form,
        'categories': Category.objects.all()
    })


def login_view(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, 'Welcome back!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {
        'form': form,
        'categories': Category.objects.all()
    })


def logout_view(request):
    """User logout"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


# ============================================================================
# SIGNALS
# ============================================================================

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Create UserProfile when User is created"""
    if created:
        UserProfile.objects.get_or_create(user=instance)


# ============================================================================
# SUBSCRIPTION & PAYMENT VIEWS
# ============================================================================

def subscription_plans(request):
    """Show subscription plans"""
    plans = SubscriptionPlan.objects.filter(is_active=True)
    user_sub = None
    if request.user.is_authenticated:
        user_sub = UserSubscription.objects.filter(
            user=request.user, is_active=True
        ).order_by('-start_date').first()
    return render(request, 'subscription.html', {
        'plans': plans,
        'user_sub': user_sub,
        'categories': Category.objects.all(),
    })


@login_required
def subscribe(request, plan_id):
    """Confirm subscription"""
    plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)
    coupon = request.GET.get('coupon', '').strip()
    if request.method == 'POST':
        # Preserve coupon parameter when redirecting to checkout
        url = reverse('upi_checkout', args=[plan.id])
        if coupon:
            url += '?' + urlencode({'coupon': coupon})
        return redirect(url)
    return render(request, 'subscribe_confirm.html', {
        'plan': plan,
        'categories': Category.objects.all(),
        'coupon': coupon,
    })


def generate_payment_link(request, plan_id):
    """Generate a shareable subscription link, optionally with coupon code"""
    plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)
    coupon = request.GET.get('coupon', '').strip()
    path = reverse('subscribe', args=[plan.id])
    url = request.build_absolute_uri(path)
    if coupon:
        url += '?' + urlencode({'coupon': coupon})
    return JsonResponse({'link': url, 'plan': plan.name, 'price': str(plan.price)})


@login_required
def save_upi(request):
    """Save user's UPI ID"""
    plan_id = request.GET.get('next_plan', '1')
    if request.method == 'POST':
        upi_id = request.POST.get('upi_id', '').strip()
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.upi_id = upi_id
        profile.save()
        messages.success(request, 'UPI ID saved successfully!')
        return redirect('upi_checkout', plan_id=plan_id)
    return render(request, 'save_upi.html', {
        'categories': Category.objects.all(),
        'plan_id': plan_id
    })


@login_required
def upi_checkout(request, plan_id):
    """
    Complete UPI checkout with:
    - QR code generation
    - Coupon code support
    - Payment verification
    - Proper bank integration
    """
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)

    # 1. Get user's UPI ID
    try:
        user_upi = request.user.userprofile.upi_id
    except:
        user_upi = None

    if not user_upi:
        messages.warning(request, 'Please save your UPI ID before checkout!')
        return redirect(f"/save-upi/?next_plan={plan.id}")

    # 2. Handle coupon code (support shareable link via GET and form input via POST)
    coupon = None
    discount = 0
    final_amount = float(plan.price)
    # Prefer coupon from GET (shareable link) else from POST form
    coupon_code = request.GET.get('coupon', '').strip() or (request.POST.get('coupon_code', '').strip() if request.method == 'POST' else '')

    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code, is_active=True)
            if coupon.is_expired():
                messages.error(request, 'This coupon has expired!')
                coupon = None
            elif not coupon.can_apply_to_plan(plan):
                messages.error(request, 'Coupon cannot be applied to this plan!')
                coupon = None
            else:
                if coupon.discount_percent:
                    discount = (float(plan.price) * coupon.discount_percent) / 100
                else:
                    discount = float(coupon.discount_amount or 0)
                final_amount = float(plan.price) - discount
                messages.success(request, f'Coupon applied! Discount: ₹{discount:.2f}')
        except Coupon.DoesNotExist:
            messages.error(request, 'Invalid coupon code!')
            coupon = None

    # 3. Handle form submission (POST) - Payment processing
    if request.method == 'POST' and 'transaction_id' in request.POST:
        txn_id = request.POST.get('transaction_id', '').strip()

        if not txn_id:
            messages.error(request, 'Transaction ID is required!')
            return render(request, 'upi_checkout.html', {
                'plan': plan,
                'user_upi_id': user_upi,
                'final_amount': final_amount,
                'coupon': coupon,
                'categories': Category.objects.all(),
            })

        # Check if transaction already exists
        if services.verify_payment_integrity(txn_id):
            messages.error(request, 'This transaction ID has already been used.')
            return render(request, 'upi_checkout.html', {
                'plan': plan,
                'user_upi_id': user_upi,
                'final_amount': final_amount,
                'coupon': coupon,
                'categories': Category.objects.all(),
            })

        # Create payment record
        payment = services.create_payment_record(
            request.user,
            txn_id,
            final_amount,
            coupon
        )

        # Activate subscription
        end_date = timezone.now() + timedelta(days=plan.duration_days)
        UserSubscription.objects.update_or_create(
            user=request.user,
            defaults={
                'plan': plan,
                'end_date': end_date,
                'is_active': True
            }
        )

        messages.success(request, f'✅ Payment successful! {plan.name} subscription is now active!')
        return redirect('payment_history')

    # 4. Generate QR code for UPI payment
    owner_upi = "8434117879@ybl"  # Replace with your actual UPI ID
    upi_link = f"upi://pay?pa={owner_upi}&pn=NewsPortal&am={final_amount:.2f}&cu=INR&tr={plan.id}"

    # Generate QR code image
    qr_code_base64 = generate_qr_code(upi_link)

    # 5. GET request - Show checkout form
    return render(request, 'upi_checkout.html', {
        'plan': plan,
        'owner_upi': owner_upi,
        'user_upi_id': user_upi,
        'upi_link': upi_link,
        'qr_code': qr_code_base64,
        'final_amount': final_amount,
        'original_amount': float(plan.price),
        'discount': discount,
        'coupon': coupon,
        'categories': Category.objects.all(),
    })


@login_required
def upi_confirm(request, plan_id):
    """
    Deprecated - use upi_checkout instead
    This function is kept for backward compatibility
    """
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)

    if request.method == 'POST':
        txn_id = request.POST.get('transaction_id', '').strip()
        if txn_id:
            end_date = timezone.now() + timedelta(days=plan.duration_days)
            UserSubscription.objects.update_or_create(
                user=request.user,
                defaults={'plan': plan, 'end_date': end_date, 'is_active': True}
            )
            messages.success(request, f'Payment verified! {plan.name} subscription is now active!')
            return redirect('payment_success')
        else:
            messages.error(request, 'Transaction verification failed.')

    return redirect('upi_checkout', plan_id=plan.id)


@login_required
def payment_history(request):
    """Display user's payment history with period filtering and download"""
    # Get period from request
    period = request.GET.get('period', 'all')
    
    # Check if download requested
    if request.GET.get('download'):
        all_payments = Payment.objects.filter(user=request.user).select_related('plan', 'coupon')
        filtered_payments = TransactionManager.filter_transactions(all_payments, period)
        return TransactionManager.export_to_csv_response(
            filtered_payments, 
            period, 
            f"{request.user.username}_transactions"
        )
    
    # Get transaction context with all periods
    all_payments = Payment.objects.filter(user=request.user).select_related('plan', 'coupon').order_by('-created_at')
    subscriptions = UserSubscription.objects.filter(user=request.user).select_related('plan')
    
    # Filter by selected period
    filtered_payments = TransactionManager.filter_transactions(all_payments, period)
    stats = TransactionManager.get_transaction_stats(filtered_payments)
    
    # Get data for all periods for display
    period_data = {}
    for p in ['week', 'month', 'year', 'all']:
        p_filtered = TransactionManager.filter_transactions(all_payments, p)
        period_data[p] = {
            'count': p_filtered.count(),
            'total': sum([x.final_amount for x in p_filtered.filter(status='completed')]) if p_filtered.exists() else 0,
            'display_name': TransactionManager.get_period_display(p),
        }

    context = {
        'payments': filtered_payments,
        'subscriptions': subscriptions,
        'categories': Category.objects.all(),
        'current_period': period,
        'period_data': period_data,
        'stats': stats,
        'periods': ['week', 'month', 'year', 'all'],
    }
    return render(request, 'payment_history.html', context)


def payment_success(request):
    """Payment success page"""
    return render(request, 'payment_success.html')


@login_required
def dashboard_view(request):
    """User dashboard"""
    return render(request, 'dashboard.html')


# ============================================================================
# ADMIN SUBSCRIPTION & PAYMENT TRACKING VIEWS
# ============================================================================

@login_required
@user_passes_test(is_admin)
def admin_subscriptions(request):
    """Admin view: Track all user subscriptions and payments"""
    # Get all active subscriptions
    subscriptions = UserSubscription.objects.filter(is_active=True).select_related(
        'user', 'plan'
    ).prefetch_related('user__payments')

    # Get all payments
    payments = Payment.objects.all().select_related(
        'user', 'plan', 'coupon'
    ).order_by('-created_at')

    # Statistics
    stats = {
        'total_subscribers': subscriptions.count(),
        'active_subscriptions': subscriptions.filter(is_active=True).count(),
        'total_payments': payments.count(),
        'completed_payments': payments.filter(status='completed').count(),
        'total_revenue': sum([p.final_amount for p in payments.filter(status='completed')]),
    }

    context = {
        'subscriptions': subscriptions,
        'payments': payments[:50],  # Show latest 50
        'stats': stats,
        'categories': Category.objects.all(),
    }
    return render(request, 'admin_subscriptions.html', context)


@login_required
@user_passes_test(is_admin)
def admin_coupons(request):
    """Admin view: Manage coupon codes"""
    coupons = Coupon.objects.all().order_by('-created_at')

    # Statistics
    stats = {
        'total_coupons': coupons.count(),
        'active_coupons': coupons.filter(is_active=True).count(),
        'expired_coupons': coupons.filter(is_active=False).count(),
    }

    context = {
        'coupons': coupons,
        'stats': stats,
        'categories': Category.objects.all(),
    }
    return render(request, 'admin_coupons.html', context)


@login_required
@user_passes_test(is_admin)
def admin_payment_history(request):
    """Admin view: Complete payment history with period filtering and download"""
    # Get period from request
    period = request.GET.get('period', 'all')
    
    # Check if download requested
    if request.GET.get('download'):
        all_payments = Payment.objects.all().select_related('user', 'plan', 'coupon')
        filtered_payments = TransactionManager.filter_transactions(all_payments, period)
        return TransactionManager.export_to_csv_response(
            filtered_payments, 
            period, 
            "admin_all_transactions"
        )
    
    # Get all payments with related data
    all_payments = Payment.objects.all().select_related(
        'user', 'plan', 'coupon'
    ).order_by('-created_at')

    # Filters
    status_filter = request.GET.get('status', '')
    coupon_filter = request.GET.get('coupon', '')
    payment_method_filter = request.GET.get('method', '')

    payments = all_payments
    if status_filter:
        payments = payments.filter(status=status_filter)
    if coupon_filter:
        payments = payments.filter(coupon__code__icontains=coupon_filter)
    if payment_method_filter:
        payments = payments.filter(payment_method=payment_method_filter)
    
    # Apply period filter
    payments = TransactionManager.filter_transactions(payments, period)

    # Statistics for all time
    total_payments = all_payments.count()
    completed_payments = all_payments.filter(status='completed')
    total_revenue = sum([p.final_amount for p in completed_payments])
    total_discount = sum([p.discount_amount for p in completed_payments])
    avg_payment = total_revenue / len(completed_payments) if completed_payments else 0

    # Period-wise stats
    period_stats = {}
    for p in ['week', 'month', 'year', 'all']:
        p_filtered = TransactionManager.filter_transactions(all_payments, p)
        p_completed = p_filtered.filter(status='completed')
        period_stats[p] = {
            'count': p_filtered.count(),
            'completed': p_completed.count(),
            'revenue': sum([x.final_amount for x in p_completed]),
            'display_name': TransactionManager.get_period_display(p),
        }

    # Coupon usage stats
    coupon_stats = Coupon.objects.annotate(
        usage_count=models.Count('payment'),
        total_discount=models.Sum('payment__discount_amount')
    ).order_by('-usage_count')[:10]

    # Payment method breakdown
    from django.db.models import Count, Sum
    method_stats = Payment.objects.filter(status='completed').values(
        'payment_method'
    ).annotate(
        count=Count('id'),
        total=Sum('final_amount')
    )

    context = {
        'payments': payments,
        'stats': {
            'total': total_payments,
            'completed': completed_payments.count(),
            'revenue': total_revenue,
            'discount': total_discount,
            'avg': avg_payment,
        },
        'period_stats': period_stats,
        'current_period': period,
        'coupon_stats': coupon_stats,
        'method_stats': method_stats,
        'categories': Category.objects.all(),
        'filters': {
            'status': status_filter,
            'coupon': coupon_filter,
            'method': payment_method_filter,
        },
        'periods': ['week', 'month', 'year', 'all'],
    }
    return render(request, 'admin_payment_history.html', context)


@login_required
@user_passes_test(is_admin)
def user_subscription_detail(request, user_id):
    """Admin view: Detailed subscription & payment info for a specific user"""
    user = get_object_or_404(User, id=user_id)
    subscriptions = UserSubscription.objects.filter(user=user).select_related('plan')
    payments = Payment.objects.filter(user=user).select_related('plan', 'coupon').order_by('-created_at')

    total_spent = sum([p.final_amount for p in payments.filter(status='completed')])

    context = {
        'user': user,
        'subscriptions': subscriptions,
        'payments': payments,
        'total_spent': total_spent,
        'categories': Category.objects.all(),
    }
    return render(request, 'user_subscription_detail.html', context)


@login_required
@user_passes_test(is_admin)
def generate_share_links(request):
    """Admin view: Generate shareable payment links for all coupon & plan combinations"""
    plans = SubscriptionPlan.objects.filter(is_active=True)
    coupons = Coupon.objects.filter(is_active=True)
    
    # Build domain
    protocol = 'https' if request.is_secure() else 'http'
    domain = request.get_host()
    
    links = []
    
    # Generate links for each plan + coupon combination
    for plan in plans:
        for coupon in coupons:
            path = reverse('subscribe', args=[plan.id])
            url = f"{protocol}://{domain}{path}?coupon={coupon.code}"
            links.append({
                'plan_name': plan.name,
                'plan_price': plan.price,
                'coupon_code': coupon.code,
                'coupon_discount': f"{coupon.discount_percent}%" if coupon.discount_percent else f"₹{coupon.discount_amount}",
                'url': url,
            })
        
        # Also generate link without coupon
        path = reverse('subscribe', args=[plan.id])
        url = f"{protocol}://{domain}{path}"
        links.append({
            'plan_name': plan.name,
            'plan_price': plan.price,
            'coupon_code': 'None (Full Price)',
            'coupon_discount': 'No Discount',
            'url': url,
        })
    
    context = {
        'links': links,
        'plans': plans,
        'coupons': coupons,
        'domain': domain,
        'categories': Category.objects.all(),
    }
    return render(request, 'admin_share_links.html', context)
# views.py


# RSS Feeds (Free, No API Key Needed)
RSS_FEEDS = {
    'The Hindu': 'https://www.thehindu.com/news/national/?service=rss',
    'Indian Express': 'https://indianexpress.com/feed',
    'Patrika': 'https://patrika.com/rss/breaking-news',
    'NDTV': 'https://feeds.ndtv.com/ndtv/latest.xml',
    'BBC News': 'http://feeds.bbc.co.uk/news/rss.xml',
}

@cache_page(60 * 5)  # Cache for 5 minutes
def epaper(request):
    """
    Simply load and display e-paper content
    No modes, no filters - just click and view
    """
    articles = get_epaper_content()
    
    return render(request, 'epaper_simple.html', {
        'articles': articles,
    })

def get_epaper_content():
    """
    Fetch content from RSS feeds automatically
    """
    articles = []
    
    for source_name, feed_url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:5]:  # 5 articles per source
                articles.append({
                    'title': entry.get('title', 'No Title'),
                    'summary': entry.get('summary', '')[:300],  # 300 chars
                    'link': entry.get('link', '#'),
                    'published': entry.get('published', 'Unknown'),
                    'author': entry.get('author', source_name),
                    'source': source_name,
                })
        except Exception as e:
            print(f"Error fetching {source_name}: {e}")
            continue
    
    return articles