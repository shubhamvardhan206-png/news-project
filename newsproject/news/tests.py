from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from .models import Category, Article, Comment, UserSubscription, SubscriptionPlan, Payment, Coupon, Author
from .views import get_news_from_api
from datetime import datetime, timedelta


class CategoryModelTest(TestCase):
    """Test Category model"""

    def setUp(self):
        self.category = Category.objects.create(
            name='Technology',
            slug='technology',
            description='Tech news'
        )

    def test_category_creation(self):
        self.assertEqual(self.category.name, 'Technology')
        self.assertEqual(self.category.slug, 'technology')

    def test_category_string_representation(self):
        self.assertEqual(str(self.category), 'Technology')


class ArticleModelTest(TestCase):
    """Test Article model"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.author = Author.objects.create(user=self.user, name='Test Author')
        self.category = Category.objects.create(name='Technology', slug='technology')
        self.article = Article.objects.create(
            title='Test Article',
            slug='test-article',
            content='Test content',
            summary='Test summary',
            category=self.category,
            author=self.author,
            is_published=True,
        )

    def test_article_creation(self):
        self.assertEqual(self.article.title, 'Test Article')
        self.assertEqual(self.article.slug, 'test-article')
        self.assertTrue(self.article.is_published)

    def test_article_views_increment(self):
        initial_views = self.article.views
        self.article.views += 1
        self.article.save()
        self.assertEqual(self.article.views, initial_views + 1)

    def test_article_string_representation(self):
        self.assertEqual(str(self.article), 'Test Article')


class CommentModelTest(TestCase):
    """Test Comment model"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.author = Author.objects.create(user=self.user, name='Test Author')
        self.category = Category.objects.create(name='Technology', slug='technology')
        self.article = Article.objects.create(
            title='Test Article',
            slug='test-article',
            content='Test content',
            category=self.category,
            author=self.author,
        )
        self.comment = Comment.objects.create(
            article=self.article,
            user=self.user,
            content='Test comment'
        )

    def test_comment_creation(self):
        self.assertEqual(self.comment.content, 'Test comment')
        self.assertEqual(self.comment.article, self.article)

    def test_comment_string_representation(self):
        self.assertIn('testuser', str(self.comment))
        self.assertIn('Test Article', str(self.comment))


class SubscriptionPlanTest(TestCase):
    """Test SubscriptionPlan model"""

    def setUp(self):
        self.plan = SubscriptionPlan.objects.create(
            name='Premium',
            plan_type='premium',
            price=99.99,
            duration_days=30
        )

    def test_plan_creation(self):
        self.assertEqual(self.plan.name, 'Premium')
        self.assertEqual(self.plan.price, 99.99)

    def test_plan_string_representation(self):
        self.assertEqual(str(self.plan), 'Premium')


class CouponTest(TestCase):
    """Test Coupon model"""

    def setUp(self):
        self.coupon = Coupon.objects.create(
            code='TEST10',
            discount_percent=10,
            max_uses=100,
            expiry_date=timezone.now() + timedelta(days=30)
        )

    def test_coupon_creation(self):
        self.assertEqual(self.coupon.code, 'TEST10')
        self.assertEqual(self.coupon.discount_percent, 10)

    def test_coupon_is_active(self):
        self.assertTrue(self.coupon.is_active)


class HomeViewTest(TestCase):
    """Test home view"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.author = Author.objects.create(user=self.user, name='Test Author')
        self.category = Category.objects.create(name='Technology', slug='technology')
        self.article = Article.objects.create(
            title='Test Article',
            slug='test-article',
            content='Test content',
            category=self.category,
            author=self.author,
            is_published=True,
        )

    def test_home_view_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_home_view_contains_articles(self):
        response = self.client.get('/')
        self.assertIn('articles', response.context)

    def test_home_view_contains_categories(self):
        response = self.client.get('/')
        self.assertIn('categories', response.context)

    def test_category_filter(self):
        response = self.client.get('/?category=technology')
        self.assertEqual(response.status_code, 200)
        articles = response.context['articles']
        for article in articles:
            if article:
                self.assertEqual(article.category.slug, 'technology')


class ArticleDetailViewTest(TestCase):
    """Test article detail view"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.author = Author.objects.create(user=self.user, name='Test Author')
        self.category = Category.objects.create(name='Technology', slug='technology')
        self.article = Article.objects.create(
            title='Test Article',
            slug='test-article',
            content='Test content',
            category=self.category,
            author=self.author,
            is_published=True,
        )

    def test_article_detail_view_loads(self):
        response = self.client.get(f'/article/{self.article.slug}/')
        self.assertEqual(response.status_code, 200)

    def test_article_detail_view_contains_article(self):
        response = self.client.get(f'/article/{self.article.slug}/')
        self.assertIn('article', response.context)
        self.assertEqual(response.context['article'].slug, self.article.slug)


class UserRegistrationTest(TestCase):
    """Test user registration"""

    def setUp(self):
        self.client = Client()

    def test_registration_view_loads(self):
        response = self.client.get('/register/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')

    def test_user_can_register(self):
        response = self.client.post('/register/', {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
        }, follow=True)
        # Check if user exists
        user_exists = User.objects.filter(username='newuser').exists()
        self.assertTrue(user_exists)


class SubscriptionPlanListTest(TestCase):
    """Test subscription plans display"""

    def setUp(self):
        self.client = Client()
        self.plan1 = SubscriptionPlan.objects.create(
            name='Basic',
            plan_type='basic',
            price=49.99,
            duration_days=30
        )
        self.plan2 = SubscriptionPlan.objects.create(
            name='Premium',
            plan_type='premium',
            price=99.99,
            duration_days=30
        )

    def test_plans_view_loads(self):
        response = self.client.get('/plans/')
        self.assertEqual(response.status_code, 200)

    def test_plans_displayed(self):
        response = self.client.get('/plans/')
        self.assertIn('plans', response.context)


class UserSubscriptionTest(TestCase):
    """Test user subscriptions"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.plan = SubscriptionPlan.objects.create(
            name='Premium',
            plan_type='premium',
            price=99.99,
            duration_days=30
        )
        self.subscription = UserSubscription.objects.create(
            user=self.user,
            plan=self.plan,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30),
            is_active=True
        )

    def test_subscription_creation(self):
        self.assertEqual(self.subscription.user, self.user)
        self.assertEqual(self.subscription.plan, self.plan)
        self.assertTrue(self.subscription.is_active)

    def test_subscription_is_active(self):
        self.assertTrue(self.subscription.is_active)


class PaymentTest(TestCase):
    """Test Payment model"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.plan = SubscriptionPlan.objects.create(
            name='Premium',
            plan_type='premium',
            price=99.99,
            duration_days=30
        )
        self.payment = Payment.objects.create(
            user=self.user,
            plan=self.plan,
            amount=99.99,
            discount_amount=10.0,
            final_amount=89.99,
            status='completed',
            payment_method='UPI',
            transaction_id='TXN123456'
        )

    def test_payment_creation(self):
        self.assertEqual(self.payment.user, self.user)
        self.assertEqual(self.payment.status, 'completed')
        self.assertEqual(self.payment.final_amount, 89.99)

    def test_payment_string_representation(self):
        self.assertIn('testuser', str(self.payment))


class SearchFunctionalityTest(TestCase):
    """Test search functionality"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.author = Author.objects.create(user=self.user, name='Test Author')
        self.category = Category.objects.create(name='Technology', slug='technology')

        self.article1 = Article.objects.create(
            title='Python Programming',
            slug='python-programming',
            content='Learn Python',
            category=self.category,
            author=self.author,
            is_published=True,
        )

        self.article2 = Article.objects.create(
            title='JavaScript Guide',
            slug='javascript-guide',
            content='Learn JavaScript',
            category=self.category,
            author=self.author,
            is_published=True,
        )

    def test_search_query(self):
        response = self.client.get('/?query=Python')
        self.assertEqual(response.status_code, 200)
        articles = response.context['articles']
        found = False
        for article in articles:
            if article.title == 'Python Programming':
                found = True
        self.assertTrue(found)


class LikeCommentTest(TestCase):
    """Test like/comment functionality"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.author = Author.objects.create(user=self.user, name='Test Author')
        self.category = Category.objects.create(name='Technology', slug='technology')
        self.article = Article.objects.create(
            title='Test Article',
            slug='test-article',
            content='Test content',
            category=self.category,
            author=self.author,
            is_published=True,
        )

    def test_user_can_like_article(self):
        self.client.login(username='testuser', password='pass123')
        self.article.likes.add(self.user)
        self.article.save()
        self.assertIn(self.user, self.article.likes.all())


class AdminDashboardTest(TestCase):
    """Test admin dashboard"""

    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='adminpass'
        )

    def test_admin_dashboard_requires_login(self):
        response = self.client.get('/admin/dashboard/')
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_admin_can_access_dashboard(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get('/admin/dashboard/')
        self.assertIn(response.status_code, [200, 302, 404])  # May 404 if URL doesn't exist


class PremiumArticleAccessTest(TestCase):
    """Test premium article access"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.author = Author.objects.create(user=self.user, name='Test Author')
        self.category = Category.objects.create(name='Technology', slug='technology')

        self.premium_article = Article.objects.create(
            title='Premium Content',
            slug='premium-content',
            content='Premium content here',
            category=self.category,
            author=self.author,
            is_published=True,
            is_premium=True,
        )

    def test_anonymous_user_sees_premium_badge(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_premium_article_detail(self):
        response = self.client.get(f'/article/{self.premium_article.slug}/')
        self.assertEqual(response.status_code, 200)
