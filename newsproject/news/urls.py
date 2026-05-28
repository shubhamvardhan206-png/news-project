from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),  # ←
    
    # News homepage - shown after redirect from welcome
    path('home/', views.home, name='home'),
    
    # Optional: Article detail page
    path('article/<slug:slug>/', views.article_detail, name='article_detail'),
    path('category/<slug:slug>/', views.category_articles, name='category_articles'),
    path('search/', views.search_view, name='search'),        # ← search_view
    path('author/<int:author_id>/', views.author_profile, name='author_profile'),
    path('login/', views.login_view, name='login'),           # ← login_view
    path('logout/', views.logout_view, name='logout'),        # ← logout_view
    path('register/', views.register_view, name='register'),  # ← register_view
    path('comment/<slug:slug>/', views.add_comment, name='add_comment'),
    path('like/<slug:slug>/', views.like_article, name='like_article'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('plans/', views.subscription_plans, name='subscription_plans'),
    path('epaper/', views.epaper, name='epaper'),
    path('subscribe/<int:plan_id>/', views.subscribe, name='subscribe'),
    path('payment-link/<int:plan_id>/', views.generate_payment_link, name='generate_payment_link'),
    path('save-upi/', views.save_upi, name='save_upi'),
    path('upi/<int:plan_id>/', views.upi_checkout, name='upi_checkout'),
    path('upi/confirm/<int:plan_id>/', views.upi_confirm, name='upi_confirm'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/history/', views.payment_history, name='payment_history'),
    path('dashboard/subscriptions/', views.admin_subscriptions, name='admin_subscriptions'),
    path('dashboard/coupons/', views.admin_coupons, name='admin_coupons'),
    path('dashboard/payments/', views.admin_payment_history, name='admin_payment_history'),
    path('dashboard/user/<int:user_id>/subscription/', views.user_subscription_detail, name='user_subscription_detail'),
    path('dashboard/share-links/', views.generate_share_links, name='generate_share_links'),
    path('receipt/<int:payment_id>/', views.payment_receipt, name='payment_receipt'),
    path('contact/', views.contact_us, name='contact_us'),
    path('advertise/', views.advertise_with_us, name='advertise_with_us'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
    path('terms/', views.terms_of_use, name='terms_of_use'),
    path('cookies/', views.cookie_policy, name='cookie_policy'),
    path('about/', views.about_us, name='about_us'),
    path('meet-developers/', views.meet_developers, name='meet_developers'),
    # Location API endpoints
    path('api/states/', views.api_get_states, name='api_get_states'),
    path('api/districts/', views.api_get_districts, name='api_get_districts'),
    path('api/blocks/', views.api_get_blocks, name='api_get_blocks'),
    path('api/news-by-location/', views.api_get_news_by_location, name='api_get_news_by_location'),
    path('api/fetch-news-location/', views.api_fetch_news_for_location, name='api_fetch_news_for_location'),
]