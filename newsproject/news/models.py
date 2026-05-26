from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone
from datetime import datetime

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='author_profile')
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='authors/', null=True, blank=True)

    def __str__(self):
        return self.name


class Article(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField()
    summary = models.TextField(blank=True)
    image = models.ImageField(upload_to='articles/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_published = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    views = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
            self.status = 'published'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    liked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Comment by {self.user.username} on {self.article.title}'


class Like(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('article', 'user')

    def __str__(self):
        return f'{self.user.username} likes {self.article.title}'


class Advertisement(models.Model):
    POSITION_CHOICES = [
        ('banner_top', 'Top Banner'),
        ('sidebar', 'Sidebar'),
        ('inline', 'Article Inline'),
        ('banner_bottom', 'Bottom Banner'),
    ]
    
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='ads/', blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    position = models.CharField(max_length=20, choices=POSITION_CHOICES, default='banner_top')
    is_active = models.BooleanField(default=True)
    clicks = models.PositiveIntegerField(default=0)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class SubscriptionPlan(models.Model):
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('basic', 'Basic'),
        ('premium', 'Premium'),
    ]

    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    duration_days = models.PositiveIntegerField(default=30)
    description = models.TextField(blank=True)
    features = models.TextField(blank=True, help_text="List features separated by commas")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['price']

    def __str__(self):
        return self.name


class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f'{self.user.username} - {self.plan}'

    def is_expired(self):
        """Check if subscription has expired"""
        return self.end_date and timezone.now() > self.end_date


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    upi_id = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.upi_id}'


# ✅ FIXED: Complete Coupon Model
class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percent = models.PositiveIntegerField(default=10, help_text="Discount percentage (0-100)")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Fixed discount amount (alternative to percent)")
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    max_uses = models.PositiveIntegerField(null=True, blank=True, help_text="Maximum times coupon can be used")
    times_used = models.PositiveIntegerField(default=0)
    applicable_plans = models.ManyToManyField(SubscriptionPlan, blank=True, help_text="Leave empty for all plans")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-valid_until']

    def __str__(self):
        return self.code

    def is_expired(self):
        """Check if coupon has expired"""
        return timezone.now() > self.valid_until

    def is_valid(self):
        """Check if coupon is valid"""
        if not self.is_active:
            return False
        if self.is_expired():
            return False
        if self.max_uses and self.times_used >= self.max_uses:
            return False
        return True

    def can_apply_to_plan(self, plan):
        """Check if coupon can be applied to a specific plan"""
        if self.applicable_plans.exists():
            return self.applicable_plans.filter(id=plan.id).exists()
        return True


# ✅ FIXED: Complete Payment Model
class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True, blank=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    transaction_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50, default='UPI', choices=[
        ('UPI', 'UPI'),
        ('CARD', 'Credit/Debit Card'),
        ('NETBANKING', 'Net Banking'),
        ('WALLET', 'Digital Wallet'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - {self.transaction_id}'


# ✅ FIXED: Complete UPIPayment Model
class UPIPayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='upi_payments')
    upi_id = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    qr_code_base64 = models.TextField(blank=True, null=True, help_text="Base64 encoded QR code for display")
    upi_link = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ])
    transaction_ref_id = models.CharField(max_length=255, blank=True, null=True)
    payment = models.OneToOneField(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'UPI Payment - {self.user.username} - {self.amount}'


class State(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class District(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='districts')
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']
        unique_together = ('state', 'name')

    def __str__(self):
        return f'{self.name} - {self.state.name}'


class Block(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='blocks')
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']
        unique_together = ('district', 'name')

    def __str__(self):
        return f'{self.name} - {self.district.name}'


class FetchedNews(models.Model):
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    source_url = models.URLField(unique=True)
    source_name = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=100, default='India')
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True)
    block = models.ForeignKey(Block, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.CharField(max_length=100, blank=True)
    language = models.CharField(max_length=10, default='en')
    published_at = models.DateTimeField(blank=True, null=True)
    fetched_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['state', '-published_at']),
            models.Index(fields=['district', '-published_at']),
            models.Index(fields=['category', '-published_at']),
        ]

    def __str__(self):
        return self.title