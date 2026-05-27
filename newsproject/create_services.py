"""
Script to create sample services for the news portal
Run: python manage.py shell < create_services.py
"""
from news.models import Service

# Delete existing services to start fresh
Service.objects.all().delete()

services_data = [
    {
        'title': 'Breaking News Alerts',
        'slug': 'breaking-news-alerts',
        'short_description': 'Get instant notifications for breaking news stories as they happen.',
        'description': 'Stay ahead of the curve with real-time breaking news alerts delivered directly to your device. Our intelligent notification system ensures you never miss important stories.',
        'icon': 'bell',
        'icon_color': '#e63946',
        'features': 'Real-time notifications\nCustomizable alert categories\nMulti-device sync\n24/7 coverage\nLocation-based news',
        'order': 1,
        'is_active': True,
    },
    {
        'title': 'Premium Journalism',
        'slug': 'premium-journalism',
        'short_description': 'In-depth, award-winning journalism from our expert reporters.',
        'description': 'Access exclusive investigative reports, expert analysis, and behind-the-scenes stories from our network of professional journalists around the globe.',
        'icon': 'newspaper',
        'icon_color': '#c0392b',
        'features': 'Exclusive interviews\nInvestigative reports\nExpert analysis\nOriginal journalism\nDaily columnists',
        'order': 2,
        'is_active': True,
    },
    {
        'title': 'Personalized News Feed',
        'slug': 'personalized-news-feed',
        'short_description': 'Customize your news experience based on your interests.',
        'description': 'Create a personalized news feed tailored to your interests and preferences. Choose your favorite categories, sources, and topics.',
        'icon': 'chart',
        'icon_color': '#e67e22',
        'features': 'Custom categories\nBookmark stories\nRead history\nTopic preferences\nSmart recommendations',
        'order': 3,
        'is_active': True,
    },
    {
        'title': 'Mobile App Access',
        'slug': 'mobile-app-access',
        'short_description': 'Read news on the go with our powerful mobile applications.',
        'description': 'Download our native iOS and Android apps to stay connected with the latest news wherever you are. Full offline reading capabilities included.',
        'icon': 'mobile',
        'icon_color': '#27ae60',
        'features': 'iOS and Android apps\nOffline reading\nPush notifications\nDark mode\nCross-device sync',
        'order': 4,
        'is_active': True,
    },
    {
        'title': 'Social Media Integration',
        'slug': 'social-media-integration',
        'short_description': 'Share stories and engage with our community across platforms.',
        'description': 'Easily share articles to your favorite social media platforms. Connect with other readers and participate in discussions about the stories that matter.',
        'icon': 'share',
        'icon_color': '#3498db',
        'features': 'One-click sharing\nSocial discussions\nCommunity engagement\nViral story tracking\nInfluencer highlights',
        'order': 5,
        'is_active': True,
    },
    {
        'title': 'E-Paper Edition',
        'slug': 'epaper-edition',
        'short_description': 'Digital version of the print edition with all content accessible.',
        'description': 'Read the full e-paper edition with enhanced digital features. Includes all sections, photos, and advertisements from the print edition.',
        'icon': 'bookmark',
        'icon_color': '#9b59b6',
        'features': 'Full e-paper access\nHighlight and annotate\nDownload articles\nArchive access\nPrint-quality images',
        'order': 6,
        'is_active': True,
    },
]

created_count = 0
for data in services_data:
    service, created = Service.objects.get_or_create(
        slug=data['slug'],
        defaults=data
    )
    if created:
        created_count += 1
        print(f"✓ Created: {service.title}")
    else:
        print(f"~ Already exists: {service.title}")

print(f"\nTotal new services created: {created_count}")
print(f"Total services in database: {Service.objects.count()}")
