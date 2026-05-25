from django.contrib import admin
from .models import (Article, Category, Comment, Author, Like,
                     Advertisement, SubscriptionPlan, UserSubscription,
                     Coupon, UPIPayment)
from .models import UserProfile
from .models import Payment
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ['name', 'slug']
    search_fields = ['name']
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'bio']
    search_fields = ['name', 'user__username']
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status',
                    'is_published', 'is_premium', 'published_at', 'views']
    list_editable = ['is_published', 'status']
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ['is_published', 'status', 'category', 'created_at', 'is_premium']
    search_fields = ['title', 'content', 'summary']
    readonly_fields = ['views', 'created_at', 'published_at']
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'article', 'liked', 'created_at']
    list_filter = ['liked', 'created_at']
    search_fields = ['content', 'user__username']
@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'article', 'created_at']
    search_fields = ['user__username', 'article__title']

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ['title', 'position', 'is_active', 'clicks', 'start_date', 'end_date']
    list_filter = ['position', 'is_active']
    search_fields = ['title']
    list_editable = ['is_active']
@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'plan_type', 'price', 'duration_days', 'is_active']
    list_filter = ['plan_type', 'is_active']
    search_fields = ['name']
    list_editable = ['is_active']
@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active', 'plan']
    search_fields = ['user__username']
    readonly_fields = ['start_date']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'upi_id', 'phone']
    search_fields = ['user__username', 'upi_id']
    


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    # This customizes how the list looks in the admin panel
    list_display = ('user', 'transaction_id', 'amount', 'status', 'created_at')

    # This adds a filter on the right sidebar so you can see 'Pending' vs 'Approved' payments quickly
    list_filter = ('status', 'created_at')

    # This adds a search bar to find payments by username or transaction ID
    search_fields = ('user__username', 'transaction_id')

    # Allows you to edit the status directly from the list view
    list_editable = ('status',)


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'discount_amount', 'valid_until', 'is_active', 'times_used', 'max_uses')
    list_filter = ('is_active', 'valid_until', 'created_at')
    search_fields = ('code', 'description')
    list_editable = ('is_active',)
    filter_horizontal = ('applicable_plans',)
    readonly_fields = ('times_used', 'created_at')
    fieldsets = (
        ('Coupon Code', {
            'fields': ('code', 'description')
        }),
        ('Discount Settings', {
            'fields': ('discount_percent', 'discount_amount')
        }),
        ('Validity Period', {
            'fields': ('valid_from', 'valid_until', 'is_active')
        }),
        ('Usage Limits', {
            'fields': ('max_uses', 'times_used')
        }),
        ('Plans', {
            'fields': ('applicable_plans',),
            'description': 'Leave empty to apply to all subscription plans'
        }),
    )


@admin.register(UPIPayment)
class UPIPaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'upi_id', 'amount', 'status', 'transaction_ref_id', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'upi_id', 'transaction_ref_id')
    readonly_fields = ('created_at', 'updated_at', 'qr_code_base64')

