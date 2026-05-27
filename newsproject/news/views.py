from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Count, Prefetch
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
import json
import uuid

from .models import (
    Article, Category, Author, Comment, Like, 
    State, District, Block, Village,
    FetchedNews, Service, Advertisement, Feedback, ContactMessage,
    SubscriptionPlan, UserSubscription, Coupon, Payment, UPIPayment,
    UserProfile
)

# ==================== LANDING & HOME ====================

def landing(request):
    """Landing page"""
    featured_articles = Article.objects.filter(
        is_published=True, 
        is_premium=False
    ).order_by('-published_at')[:5]
    
    top_services = Service.objects.filter(is_active=True).order_by('order')[:3]
    
    context = {
        'featured_articles': featured_articles,
        'top_services': top_services,
    }
    return render(request, 'landing.html', context)


def home(request):
    """News homepage - MATCHES home.html template exactly"""
    
    # 1. Featured article (single, most recent published)
    featured = Article.objects.filter(
        is_published=True
    ).order_by('-published_at').first()
    
    # 2. Trending articles (top 5 by views)
    trending = Article.objects.filter(
        is_published=True
    ).order_by('-views')[:5]
    
    # 3. Categories
    categories = Category.objects.all()
    active_category = request.GET.get('category')
    
    # 4. Latest articles (filtered by category if selected)
    articles = Article.objects.filter(is_published=True)
    if active_category:
        articles = articles.filter(category__slug=active_category)
    
    articles = articles.order_by('-published_at')[:12]
    
    # 5. API News (World & India news)
    api_news = FetchedNews.objects.filter(is_active=True).order_by('-published_at')[:20]
    
    # Add source_region to api_news for template filtering
    for news in api_news:
        if news.state and news.state.name:
            # If it has a state, it's India news
            news.source_region = "🇮🇳 India"
        else:
            # Otherwise it's world news
            news.source_region = "🌍 World"
    
    # 6. Top services
    top_services = Service.objects.filter(is_active=True).order_by('order')[:3]
    
    # 7. Sidebar advertisements (left sidebar - position='sidebar')
    sidebar_ads = Advertisement.objects.filter(
        is_active=True,
        position='sidebar',
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    ).order_by('?')[:5]  # Random order
    
    # 8. Bottom banner advertisements (position='inline' or 'footer')
    bottom_banner_ads = Advertisement.objects.filter(
        is_active=True,
        position__in=['inline', 'footer'],
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    ).order_by('?')[:3]  # Random order
    
    context = {
        'featured': featured,
        'trending': trending,
        'categories': categories,
        'active_category': active_category,
        'articles': articles,
        'api_news': api_news,
        'top_services': top_services,
        'sidebar_ads': sidebar_ads,
        'bottom_banner_ads': bottom_banner_ads,
    }
    
    return render(request, 'home.html', context)


# ==================== ARTICLE & CATEGORY ====================

def article_detail(request, slug):
    """Article detail page"""
    article = get_object_or_404(Article, slug=slug, is_published=True)
    
    # Increment views
    article.increment_views()
    
    # Get comments
    comments = article.comments.all()
    
    # Related articles (same category)
    related = Article.objects.filter(
        category=article.category,
        is_published=True
    ).exclude(id=article.id)[:5]
    
    # Sidebar ads
    sidebar_ads = Advertisement.objects.filter(
        is_active=True,
        position='sidebar'
    ).order_by('?')[:5]
    
    context = {
        'article': article,
        'comments': comments,
        'related': related,
        'sidebar_ads': sidebar_ads,
    }
    return render(request, 'article_detail.html', context)


def category_view(request, slug):
    """Category articles"""
    category = get_object_or_404(Category, slug=slug)
    articles = Article.objects.filter(
        category=category,
        is_published=True
    ).order_by('-published_at')
    
    paginator = Paginator(articles, 12)
    page = request.GET.get('page', 1)
    articles = paginator.get_page(page)
    
    context = {
        'category': category,
        'articles': articles,
        'page_obj': articles,
    }
    return render(request, 'category_articles.html', context)


def category_detail(request, slug):
    """Category detail (alias for category_view)"""
    return category_view(request, slug)


# ==================== SEARCH & AUTHOR ====================

def search_view(request):
    """Search articles"""
    query = request.GET.get('q', '')
    
    articles = Article.objects.filter(is_published=True)
    
    if query:
        articles = articles.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(summary__icontains=query)
        )
    
    articles = articles.order_by('-published_at')
    
    # Pagination
    paginator = Paginator(articles, 12)
    page = request.GET.get('page', 1)
    articles = paginator.get_page(page)
    
    context = {
        'articles': articles,
        'query': query,
        'page_obj': articles,
    }
    return render(request, 'search_results.html', context)


def author_profile(request, author_id):
    """Author profile page"""
    author = get_object_or_404(Author, id=author_id)
    articles = author.articles.filter(is_published=True).order_by('-published_at')
    
    # Pagination
    paginator = Paginator(articles, 12)
    page = request.GET.get('page', 1)
    articles = paginator.get_page(page)
    
    context = {
        'author': author,
        'articles': articles,
        'page_obj': articles,
    }
    return render(request, 'author_profile.html', context)


# ==================== AUTHENTICATION ====================

def login_view(request):
    """User login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            context = {'error': 'Invalid credentials'}
            return render(request, 'login.html', context)
    
    return render(request, 'login.html')


def logout_view(request):
    """User logout"""
    logout(request)
    return redirect('landing')


def register_view(request):
    """User registration"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        if password != password2:
            context = {'error': 'Passwords do not match'}
            return render(request, 'register.html', context)
        
        if User.objects.filter(username=username).exists():
            context = {'error': 'Username already exists'}
            return render(request, 'register.html', context)
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        # Create user profile
        UserProfile.objects.create(user=user)
        
        login(request, user)
        return redirect('home')
    
    return render(request, 'register.html')


# ==================== COMMENTS & LIKES ====================

@login_required
def add_comment(request, slug):
    """Add comment to article"""
    article = get_object_or_404(Article, slug=slug)
    
    if request.method == 'POST':
        content = request.POST.get('content', '')
        
        if content:
            Comment.objects.create(
                article=article,
                user=request.user,
                content=content
            )
    
    return redirect('article_detail', slug=slug)


@login_required
def like_article(request, slug):
    """Like/unlike article"""
    article = get_object_or_404(Article, slug=slug)
    
    like, created = Like.objects.get_or_create(
        article=article,
        user=request.user
    )
    
    if not created:
        like.delete()
    
    return redirect('article_detail', slug=slug)


# ==================== LOCATION FILTERING - API ENDPOINTS ====================

@csrf_exempt
@require_http_methods(["GET"])
def api_get_states(request):
    """Get all states - JSON API"""
    states = list(State.objects.all().values('id', 'name', 'code', 'slug'))
    return JsonResponse(states, safe=False)


@csrf_exempt
@require_http_methods(["GET"])
def api_get_districts(request):
    """Get districts by state - JSON API"""
    state_id = request.GET.get('state_id')
    
    if not state_id:
        return JsonResponse({'error': 'state_id required'}, status=400)
    
    districts = list(District.objects.filter(
        state_id=state_id
    ).values('id', 'name', 'code', 'slug'))
    
    return JsonResponse(districts, safe=False)


@csrf_exempt
@require_http_methods(["GET"])
def api_get_blocks(request):
    """Get blocks by district - JSON API"""
    district_id = request.GET.get('district_id')
    
    if not district_id:
        return JsonResponse({'error': 'district_id required'}, status=400)
    
    blocks = list(Block.objects.filter(
        district_id=district_id
    ).values('id', 'name', 'code', 'slug'))
    
    return JsonResponse(blocks, safe=False)


@csrf_exempt
@require_http_methods(["GET"])
def api_get_villages(request):
    """Get villages by block - JSON API"""
    block_id = request.GET.get('block_id')
    
    if not block_id:
        return JsonResponse({'error': 'block_id required'}, status=400)
    
    villages = list(Village.objects.filter(
        block_id=block_id
    ).values('id', 'name', 'code', 'slug'))
    
    return JsonResponse(villages, safe=False)


def state_news_api(request, state_id):
    """Get districts for state (URL pattern alias)"""
    request.GET = request.GET.copy()
    request.GET['state_id'] = state_id
    return api_get_districts(request)


def district_news_api(request, district_id):
    """Get blocks for district (URL pattern alias)"""
    request.GET = request.GET.copy()
    request.GET['district_id'] = district_id
    return api_get_blocks(request)


# ==================== NEWS BY LOCATION ====================

def news_by_location(request):
    """Filter news by location - STATE > DISTRICT > BLOCK > VILLAGE"""
    state_id = request.GET.get('state')
    district_id = request.GET.get('district')
    block_id = request.GET.get('block')
    village_id = request.GET.get('village')
    
    # Filter articles by location
    articles = Article.objects.filter(is_published=True)
    
    if state_id:
        articles = articles.filter(state_id=state_id)
    if district_id:
        articles = articles.filter(district_id=district_id)
    if block_id:
        articles = articles.filter(block_id=block_id)
    if village_id:
        articles = articles.filter(village_id=village_id)
    
    articles = articles.order_by('-published_at')
    
    # Filter fetched news by location
    fetched_news = FetchedNews.objects.filter(is_active=True)
    
    if state_id:
        fetched_news = fetched_news.filter(state_id=state_id)
    if district_id:
        fetched_news = fetched_news.filter(district_id=district_id)
    if block_id:
        fetched_news = fetched_news.filter(block_id=block_id)
    if village_id:
        fetched_news = fetched_news.filter(village_id=village_id)
    
    fetched_news = fetched_news.order_by('-published_at')
    
    # Get location details for display
    location_name = ""
    try:
        if state_id:
            state = State.objects.get(id=state_id)
            location_name = state.name
        if district_id:
            district = District.objects.get(id=district_id)
            location_name += f" - {district.name}"
        if block_id:
            block = Block.objects.get(id=block_id)
            location_name += f" - {block.name}"
        if village_id:
            village = Village.objects.get(id=village_id)
            location_name += f" - {village.name}"
    except:
        location_name = "Selected Location"
    
    # Pagination
    paginator = Paginator(articles, 12)
    page = request.GET.get('page', 1)
    articles = paginator.get_page(page)
    
    context = {
        'articles': articles,
        'fetched_news': fetched_news,
        'location_name': location_name,
        'page_obj': articles,
        'filters': {
            'state': state_id,
            'district': district_id,
            'block': block_id,
            'village': village_id,
        }
    }
    
    return render(request, 'news_by_location.html', context)


def location_news(request):
    """Location news (alias for news_by_location)"""
    return news_by_location(request)


# ==================== API ENDPOINTS FOR NEWS ====================

def api_get_news_by_location(request):
    """API: Get articles by location (JSON)"""
    state_id = request.GET.get('state')
    district_id = request.GET.get('district')
    block_id = request.GET.get('block')
    village_id = request.GET.get('village')
    
    articles = Article.objects.filter(is_published=True)
    
    if state_id:
        articles = articles.filter(state_id=state_id)
    if district_id:
        articles = articles.filter(district_id=district_id)
    if block_id:
        articles = articles.filter(block_id=block_id)
    if village_id:
        articles = articles.filter(village_id=village_id)
    
    data = [{
        'id': a.id,
        'title': a.title,
        'slug': a.slug,
        'author': a.author.name if a.author else '',
        'views': a.views,
        'published_at': a.published_at.isoformat() if a.published_at else ''
    } for a in articles.order_by('-published_at')[:50]]
    
    return JsonResponse(data, safe=False)


def api_fetch_news_for_location(request):
    """API: Get fetched news by location (JSON)"""
    state_id = request.GET.get('state')
    district_id = request.GET.get('district')
    block_id = request.GET.get('block')
    village_id = request.GET.get('village')
    
    news = FetchedNews.objects.filter(is_active=True)
    
    if state_id:
        news = news.filter(state_id=state_id)
    if district_id:
        news = news.filter(district_id=district_id)
    if block_id:
        news = news.filter(block_id=block_id)
    if village_id:
        news = news.filter(village_id=village_id)
    
    data = [{
        'id': n.id,
        'title': n.title,
        'description': n.description,
        'source': n.source_name,
        'image': n.image_url,
        'published_at': n.published_at.isoformat() if n.published_at else ''
    } for n in news.order_by('-published_at')[:50]]
    
    return JsonResponse(data, safe=False)


def get_all_states(request):
    """Get all states (alias)"""
    return api_get_states(request)


def get_all_districts(request):
    """Get all districts (alias)"""
    return api_get_districts(request)


def fetch_news_by_state(request):
    """Fetch news by state (alias)"""
    return api_get_news_by_location(request)


def fetch_news_by_district(request):
    """Fetch news by district (alias)"""
    return api_get_news_by_location(request)


# ==================== SERVICES ====================

def services(request):
    """Services page"""
    services = Service.objects.filter(is_active=True).order_by('order')
    
    context = {
        'services': services,
    }
    return render(request, 'services.html', context)


# ==================== SUBSCRIPTION & PAYMENT ====================

def subscription_plans(request):
    """Subscription plans page"""
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price')
    
    context = {
        'plans': plans,
    }
    return render(request, 'subscription_plans.html', context)


@login_required
def subscribe(request, plan_id):
    """Subscribe to plan"""
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    
    # Calculate end date
    end_date = timezone.now() + timedelta(days=plan.duration_days)
    
    # Create or update subscription
    subscription, created = UserSubscription.objects.update_or_create(
        user=request.user,
        defaults={
            'plan': plan,
            'end_date': end_date,
            'is_active': True
        }
    )
    
    return redirect('payment_success')


@login_required
def generate_payment_link(request, plan_id):
    """Generate payment link"""
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    
    context = {
        'plan': plan,
    }
    return render(request, 'payment_link.html', context)


@login_required
def save_upi(request):
    """Save UPI ID"""
    if request.method == 'POST':
        upi_id = request.POST.get('upi_id')
        
        profile = request.user.profile
        profile.upi_id = upi_id
        profile.save()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})


@login_required
def upi_checkout(request, plan_id):
    """UPI checkout"""
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    
    context = {
        'plan': plan,
    }
    return render(request, 'upi_checkout.html', context)


@login_required
def upi_confirm(request, plan_id):
    """Confirm UPI payment"""
    if request.method == 'POST':
        plan = get_object_or_404(SubscriptionPlan, id=plan_id)
        
        # Create UPI payment record
        upi_payment = UPIPayment.objects.create(
            user=request.user,
            upi_id=request.user.profile.upi_id or 'N/A',
            amount=plan.price,
            transaction_ref_id=str(uuid.uuid4()),
            status='success'
        )
        
        # Create subscription
        end_date = timezone.now() + timedelta(days=plan.duration_days)
        UserSubscription.objects.update_or_create(
            user=request.user,
            defaults={
                'plan': plan,
                'end_date': end_date,
                'is_active': True
            }
        )
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})


@login_required
def payment_success(request):
    """Payment success page"""
    context = {}
    return render(request, 'payment_success.html', context)


@login_required
def payment_receipt(request, txn_id):
    """Payment receipt"""
    payment = get_object_or_404(Payment, transaction_id=txn_id, user=request.user)
    
    context = {
        'payment': payment,
    }
    return render(request, 'payment_receipt.html', context)


@login_required
def payment_history(request):
    """Payment history"""
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(payments, 10)
    page = request.GET.get('page', 1)
    payments = paginator.get_page(page)
    
    context = {
        'payments': payments,
        'page_obj': payments,
    }
    return render(request, 'payment_history.html', context)


# ==================== EPAPER ====================

def epaper(request):
    """E-Paper page"""
    context = {}
    return render(request, 'epaper.html', context)


# ==================== ADMIN DASHBOARD ====================

@login_required
def admin_dashboard(request):
    """Admin dashboard"""
    if not request.user.is_staff:
        return redirect('home')
    
    context = {
        'total_articles': Article.objects.count(),
        'total_users': User.objects.count(),
        'total_comments': Comment.objects.count(),
        'total_subscriptions': UserSubscription.objects.filter(is_active=True).count(),
    }
    return render(request, 'admin/dashboard.html', context)


@login_required
def admin_subscriptions(request):
    """Admin subscriptions"""
    if not request.user.is_staff:
        return redirect('home')
    
    subscriptions = UserSubscription.objects.all().order_by('-start_date')
    
    # Pagination
    paginator = Paginator(subscriptions, 20)
    page = request.GET.get('page', 1)
    subscriptions = paginator.get_page(page)
    
    context = {
        'subscriptions': subscriptions,
        'page_obj': subscriptions,
    }
    return render(request, 'admin/subscriptions.html', context)


@login_required
def admin_coupons(request):
    """Admin coupons"""
    if not request.user.is_staff:
        return redirect('home')
    
    coupons = Coupon.objects.all().order_by('-valid_until')
    context = {'coupons': coupons}
    return render(request, 'admin/coupons.html', context)


@login_required
def admin_payment_history(request):
    """Admin payment history"""
    if not request.user.is_staff:
        return redirect('home')
    
    payments = Payment.objects.all().order_by('-created_at')
    
    # Pagination
    paginator = Paginator(payments, 20)
    page = request.GET.get('page', 1)
    payments = paginator.get_page(page)
    
    context = {
        'payments': payments,
        'page_obj': payments,
    }
    return render(request, 'admin/payment_history.html', context)


@login_required
def generate_share_links(request):
    """Generate share links"""
    if not request.user.is_staff:
        return redirect('home')
    
    context = {}
    return render(request, 'admin/share_links.html', context)


@login_required
def user_subscription_detail(request, user_id):
    """User subscription detail"""
    if not request.user.is_staff:
        return redirect('home')
    
    subscription = get_object_or_404(UserSubscription, user_id=user_id)
    context = {'subscription': subscription}
    return render(request, 'admin/user_subscription_detail.html', context)


# ==================== INFORMATION PAGES ====================

def about_us(request):
    """About us page"""
    return render(request, 'about.html')


def contact_us(request):
    """Contact us page"""
    if request.method == 'POST':
        ContactMessage.objects.create(
            name=request.POST.get('name', ''),
            email=request.POST.get('email', ''),
            phone=request.POST.get('phone', ''),
            subject=request.POST.get('subject', ''),
            message=request.POST.get('message', ''),
        )
        return redirect('home')
    
    return render(request, 'contact.html')


def advertise(request):
    """Advertise page"""
    return render(request, 'advertise.html')


def privacy_policy(request):
    """Privacy policy"""
    return render(request, 'privacy_policy.html')


def terms_of_use(request):
    """Terms of use"""
    return render(request, 'terms_of_use.html')


def cookie_policy(request):
    """Cookie policy"""
    return render(request, 'cookie_policy.html')


def feedback(request):
    """Feedback page"""
    if request.method == 'POST':
        Feedback.objects.create(
            name=request.POST.get('name', ''),
            email=request.POST.get('email', ''),
            phone=request.POST.get('phone', ''),
            feedback_type=request.POST.get('feedback_type', 'suggestion'),
            subject=request.POST.get('subject', ''),
            message=request.POST.get('message', ''),
            rating=request.POST.get('rating'),
        )
        return redirect('home')
    
    return render(request, 'feedback.html')