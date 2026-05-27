from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Article, Category, Author, Comment, Like,
    State, District, Block, Village,
    FetchedNews, Service, Advertisement, Feedback, ContactMessage,
    SubscriptionPlan, UserSubscription, Coupon, Payment, UPIPayment,
    UserProfile
)


# ==================== LOCATION MODELS ====================

@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    search_fields = ['name', 'code']
    ordering = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ['name', 'state', 'code']
    search_fields = ['name', 'state__name']
    list_filter = ['state']
    ordering = ['state', 'name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ['name', 'district', 'get_state']
    search_fields = ['name', 'district__name', 'district__state__name']
    list_filter = ['district__state', 'district']
    ordering = ['district', 'name']
    prepopulated_fields = {'slug': ('name',)}
    
    def get_state(self, obj):
        return obj.district.state.name
    get_state.short_description = 'State'


@admin.register(Village)
class VillageAdmin(admin.ModelAdmin):
    list_display = ['name', 'block', 'get_district', 'get_state']
    search_fields = ['name', 'block__name', 'block__district__name', 'block__district__state__name']
    list_filter = ['block__district__state', 'block__district', 'block']
    ordering = ['block', 'name']
    prepopulated_fields = {'slug': ('name',)}
    
    def get_district(self, obj):
        return obj.block.district.name
    get_district.short_description = 'District'
    
    def get_state(self, obj):
        return obj.block.district.state.name
    get_state.short_description = 'State'


# ==================== CATEGORY ====================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name']
    ordering = ['name']
    prepopulated_fields = {'slug': ('name',)}


# ==================== AUTHOR ====================

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'email', 'phone', 'created_at']
    search_fields = ['name', 'user__username', 'email']
    list_filter = ['created_at']
    readonly_fields = ['created_at']
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'name', 'email', 'phone')
        }),
        ('Profile', {
            'fields': ('profile_image', 'bio')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


# ==================== ARTICLE ====================

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'author', 'category', 'status',
        'is_published', 'is_premium', 'published_at', 'views',
        'get_location'
    ]
    list_editable = ['is_published', 'status']
    list_filter = [
        'is_published', 'status', 'category', 'is_premium',
        'created_at', 'state', 'district', 'block'
    ]
    search_fields = ['title', 'content', 'summary']
    readonly_fields = ['views', 'created_at', 'published_at', 'updated_at']
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Article Info', {
            'fields': ('title', 'slug', 'author', 'category')
        }),
        ('Content', {
            'fields': ('summary', 'content', 'image')
        }),
        ('Location', {
            'fields': ('state', 'district', 'block', 'village'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('status', 'is_published', 'is_premium', 'published_at')
        }),
        ('Engagement', {
            'fields': ('views',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_location(self, obj):
        location = []
        if obj.state:
            location.append(obj.state.name)
        if obj.district:
            location.append(obj.district.name)
        if obj.block:
            location.append(obj.block.name)
        if obj.village:
            location.append(obj.village.name)
        return ' > '.join(location) if location else '—'
    get_location.short_description = 'Location'


# ==================== COMMENT ====================

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'article', 'liked', 'created_at', 'get_content_preview']
    list_filter = ['liked', 'created_at']
    search_fields = ['content', 'user__username', 'article__title']
    readonly_fields = ['created_at']
    
    def get_content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    get_content_preview.short_description = 'Content'


# ==================== LIKE ====================

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'article', 'created_at']
    search_fields = ['user__username', 'article__title']
    list_filter = ['created_at']
    readonly_fields = ['created_at']


# ==================== ADVERTISEMENT ====================

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ['title', 'position', 'is_active', 'clicks', 'start_date', 'end_date']
    list_filter = ['position', 'is_active', 'start_date']
    search_fields = ['title']
    list_editable = ['is_active']
    fieldsets = (
        ('Advertisement Info', {
            'fields': ('title', 'description', 'image')
        }),
        ('Display Settings', {
            'fields': ('position', 'is_active')
        }),
        ('Link & Click', {
            'fields': ('url', 'clicks')
        }),
        ('Validity Period', {
            'fields': ('start_date', 'end_date')
        }),
    )


# ==================== SUBSCRIPTION ====================

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'plan_type', 'price', 'duration_days', 'is_active']
    list_filter = ['plan_type', 'is_active']
    search_fields = ['name']
    list_editable = ['is_active']
    fieldsets = (
        ('Plan Info', {
            'fields': ('name', 'plan_type', 'description')
        }),
        ('Pricing', {
            'fields': ('price', 'duration_days')
        }),
        ('Features', {
            'fields': ('features',),
            'description': 'Enter each feature on a new line'
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'start_date', 'end_date', 'is_active', 'get_status']
    list_filter = ['is_active', 'plan', 'start_date']
    search_fields = ['user__username', 'plan__name']
    readonly_fields = ['start_date']
    
    def get_status(self, obj):
        if obj.is_expired():
            return format_html('<span style="color: red;">Expired</span>')
        return format_html('<span style="color: green;">Active</span>')
    get_status.short_description = 'Status'


# ==================== USER PROFILE ====================

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'upi_id']
    search_fields = ['user__username', 'upi_id', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Contact', {
            'fields': ('phone', 'upi_id')
        }),
        ('Profile', {
            'fields': ('profile_image', 'bio')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# ==================== PAYMENT ====================

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_id', 'amount', 'status', 'payment_method', 'created_at')
    list_filter = ('status', 'created_at', 'payment_method')
    search_fields = ('user__username', 'transaction_id')
    list_editable = ('status',)
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Transaction', {
            'fields': ('transaction_id', 'amount')
        }),
        ('User', {
            'fields': ('user',)
        }),
        ('Payment', {
            'fields': ('payment_method', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# ==================== COUPON ====================

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'discount_percent', 'discount_amount',
        'valid_until', 'is_active', 'times_used', 'max_uses'
    )
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


# ==================== UPI PAYMENT ====================

@admin.register(UPIPayment)
class UPIPaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'upi_id', 'amount', 'status', 'transaction_ref_id', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'upi_id', 'transaction_ref_id')
    readonly_fields = ('created_at', 'updated_at', 'qr_code_base64')
    
    fieldsets = (
        ('User & Payment', {
            'fields': ('user', 'upi_id', 'amount')
        }),
        ('Transaction', {
            'fields': ('transaction_ref_id', 'status')
        }),
        ('QR Code', {
            'fields': ('qr_code_base64',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# ==================== FETCHED NEWS ====================

@admin.register(FetchedNews)
class FetchedNewsAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'state', 'district', 'block',
        'category', 'published_at', 'views', 'is_active'
    )
    list_filter = (
        'state', 'district', 'block', 'category',
        'language', 'is_active', 'published_at'
    )
    search_fields = ('title', 'description', 'source_name')
    readonly_fields = ('fetched_at', 'views')
    list_editable = ('is_active',)
    
    fieldsets = (
        ('News Info', {
            'fields': ('title', 'description', 'content')
        }),
        ('Source', {
            'fields': ('source_name', 'source_url', 'image_url')
        }),
        ('Location', {
            'fields': ('state', 'district', 'block', 'village'),
            'classes': ('collapse',)
        }),
        ('Category & Language', {
            'fields': ('category', 'language')
        }),
        ('Status', {
            'fields': ('is_active', 'views')
        }),
        ('Timestamps', {
            'fields': ('published_at', 'fetched_at'),
            'classes': ('collapse',)
        }),
    )


# ==================== SERVICE ====================

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon', 'order', 'is_active', 'created_at')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'slug', 'short_description', 'description')
        }),
        ('Display', {
            'fields': ('image', 'icon', 'icon_color', 'order', 'is_active')
        }),
        ('Features', {
            'fields': ('features',),
            'description': 'Enter each feature on a new line'
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


# ==================== CONTACT MESSAGE ====================

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Contact Info', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Message', {
            'fields': ('subject', 'message')
        }),
        ('Status', {
            'fields': ('is_read', 'created_at')
        }),
    )


# ==================== FEEDBACK ====================

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'feedback_type', 'rating', 'created_at', 'is_read')
    list_filter = ('feedback_type', 'rating', 'created_at', 'is_read')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('User Info', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Feedback', {
            'fields': ('feedback_type', 'subject', 'message', 'rating')
        }),
        ('Status', {
            'fields': ('is_read', 'created_at')
        }),
    )