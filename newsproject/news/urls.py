from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('article/<slug:slug>/', views.article_detail, name='article_detail'),
    path('category/<slug:slug>/', views.category_view, name='category_articles'),
    path('search/', views.search_view, name='search'),        # ← search_view
    path('author/<int:author_id>/', views.author_profile, name='author_profile'),
    path('login/', views.login_view, name='login'),           # ← login_view
    path('logout/', views.logout_view, name='logout'),        # ← logout_view
    path('register/', views.register_view, name='register'),  # ← register_view
    path('comment/<slug:slug>/', views.add_comment, name='add_comment'),
    path('like/<slug:slug>/', views.like_article, name='like_article'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('plans/', views.subscription_plans, name='subscription_plans'),
    path('subscribe/<int:plan_id>/', views.subscribe, name='subscribe'),
    path('save-upi/', views.save_upi, name='save_upi'),
    path('upi/<int:plan_id>/', views.upi_checkout, name='upi_checkout'),
    path('upi/confirm/<int:plan_id>/', views.upi_confirm, name='upi_confirm'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/history/', views.payment_history, name='payment_history'),
]