from django.urls import path
from . import views

urlpatterns = [
    # Landing & Home
    path('', views.landing, name='landing'),           # Root / shows landing page
    path('home/', views.home, name='home'),            # /home/ shows news homepage
    
    # News & Articles
    path('services/', views.services, name='services'),
    path('article/<slug:slug>/', views.article_detail, name='article_detail'),
    path('category/<slug:slug>/', views.category_view, name='category_articles'),
    path('search/', views.search_view, name='search'),
    path('author/<int:author_id>/', views.author_profile, name='author_profile'),
    path('category/<slug:slug>/', views.category_detail, name='category'),  # Add this line
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    
    # Comments & Interactions
    path('comment/<slug:slug>/', views.add_comment, name='add_comment'),
    path('like/<slug:slug>/', views.like_article, name='like_article'),
    
    # Admin Dashboard
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/subscriptions/', views.admin_subscriptions, name='admin_subscriptions'),
    path('dashboard/coupons/', views.admin_coupons, name='admin_coupons'),
    path('dashboard/payments/', views.admin_payment_history, name='admin_payment_history'),
    path('dashboard/share-links/', views.generate_share_links, name='generate_share_links'),
    path('dashboard/user/<int:user_id>/subscription/', views.user_subscription_detail, name='user_subscription_detail'),
    
    # Subscription & Payment
    path('plans/', views.subscription_plans, name='subscription_plans'),
    path('subscribe/<int:plan_id>/', views.subscribe, name='subscribe'),
    path('payment-link/<int:plan_id>/', views.generate_payment_link, name='generate_payment_link'),
    path('save-upi/', views.save_upi, name='save_upi'),
    path('upi/<int:plan_id>/', views.upi_checkout, name='upi_checkout'),
    path('upi/confirm/<int:plan_id>/', views.upi_confirm, name='upi_confirm'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/receipt/<str:txn_id>/', views.payment_receipt, name='payment_receipt'),
    path('payment/history/', views.payment_history, name='payment_history'),
    
    # E-Paper
    path('epaper/', views.epaper, name='epaper'),
    
    # Location API
    path('api/states/', views.api_get_states, name='api_get_states'),
    path('api/districts/', views.api_get_districts, name='api_get_districts'),
    path('api/blocks/', views.api_get_blocks, name='api_get_blocks'),
    path('api/news-by-location/', views.api_get_news_by_location, name='api_get_news_by_location'),
    path('api/fetch-news-location/', views.api_fetch_news_for_location, name='api_fetch_news_for_location'),
    path('location-news/', views.location_news, name='location_news'),
    path('api/state-districts/<int:state_id>/', views.state_news_api, name='state_districts_api'),
    path('api/district-blocks/<int:district_id>/', views.district_news_api, name='district_blocks_api'), 
    path('api/states/', views.get_all_states, name='api_states'),
    path('api/districts/', views.get_all_districts, name='api_districts'),
    path('api/news/state/', views.fetch_news_by_state, name='api_news_by_state'),
    path('api/news/district/', views.fetch_news_by_district, name='api_news_by_district'),
    path('news-by-location/', views.news_by_location, name='news_by_location'),
    
    # Information Pages
    path('about/', views.about_us, name='about_us'),
    path('contact/', views.contact_us, name='contact_us'),
    path('advertise/', views.advertise, name='advertise'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-use/', views.terms_of_use, name='terms_of_use'),
    path('cookie-policy/', views.cookie_policy, name='cookie_policy'),
    path('feedback/', views.feedback, name='feedback'),

]