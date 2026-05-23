from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
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
from . import selectors, services
from .utils import generate_qr_code


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
    if request.method == 'POST':
        return redirect('upi_checkout', plan_id=plan.id)
    return render(request, 'subscribe_confirm.html', {
        'plan': plan,
        'categories': Category.objects.all(),
    })


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

    # 2. Handle coupon code
    coupon = None
    discount = 0
    final_amount = float(plan.price)
    coupon_code = request.POST.get('coupon_code', '').strip() if request.method == 'POST' else ''

    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code, is_active=True)
            if coupon.is_expired():
                messages.error(request, 'This coupon has expired!')
            else:
                discount = (float(plan.price) * coupon.discount_percent) / 100
                final_amount = float(plan.price) - discount
                messages.success(request, f'Coupon applied! Discount: ₹{discount:.2f}')
        except Coupon.DoesNotExist:
            messages.error(request, 'Invalid coupon code!')

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
    """Display user's payment history"""
    payments = selectors.get_user_payments(request.user)
    return render(request, 'payment_history.html', {'payments': payments})


def payment_success(request):
    """Payment success page"""
    return render(request, 'payment_success.html')


@login_required
def dashboard_view(request):
    """User dashboard"""
    return render(request, 'dashboard.html')