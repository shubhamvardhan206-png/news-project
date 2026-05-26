from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from news.api_services import LocationAPIService, NewsDataService
from news.models import State, District, Block, FetchedNews


class Command(BaseCommand):
    help = 'Fetch and store location data from REST India API and news from NewsData.io'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fetch-locations',
            action='store_true',
            help='Fetch and store location data (states, districts, blocks)',
        )
        parser.add_argument(
            '--fetch-news',
            action='store_true',
            help='Fetch and store news articles from NewsData.io',
        )
        parser.add_argument(
            '--state',
            type=str,
            help='State name for news filtering',
        )
        parser.add_argument(
            '--district',
            type=str,
            help='District name for news filtering',
        )
        parser.add_argument(
            '--category',
            type=str,
            help='News category to filter',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Fetch both locations and news',
        )

    def handle(self, *args, **options):
        if options['all']:
            options['fetch_locations'] = True
            options['fetch_news'] = True

        if not any([options['fetch_locations'], options['fetch_news']]):
            raise CommandError(
                'Please specify --fetch-locations, --fetch-news, or --all'
            )

        if options['fetch_locations']:
            self.fetch_locations()

        if options['fetch_news']:
            state_name = options.get('state')
            district_name = options.get('district')
            category = options.get('category')
            self.fetch_news(state_name, district_name, category)

    def fetch_locations(self):
        """Fetch and store locations from REST India API"""
        self.stdout.write(
            self.style.SUCCESS('Starting location data fetch...')
        )

        try:
            success = LocationAPIService.fetch_and_store_locations()

            if success:
                state_count = State.objects.count()
                district_count = District.objects.count()
                block_count = Block.objects.count()

                self.stdout.write(
                    self.style.SUCCESS(
                        'Location data fetched successfully!'
                    )
                )
                self.stdout.write(
                    f'  States: {state_count}'
                )
                self.stdout.write(
                    f'  Districts: {district_count}'
                )
                self.stdout.write(
                    f'  Blocks: {block_count}'
                )
            else:
                self.stdout.write(
                    self.style.ERROR('Failed to fetch location data')
                )
        except Exception as e:
            raise CommandError(f'Error fetching locations: {str(e)}')

    def fetch_news(self, state_name=None, district_name=None, category=None):
        """Fetch and store news from NewsData.io"""
        self.stdout.write(
            self.style.SUCCESS('Starting news fetch...')
        )

        try:
            filters = []
            if state_name:
                filters.append(f'State: {state_name}')
            if district_name:
                filters.append(f'District: {district_name}')
            if category:
                filters.append(f'Category: {category}')

            if filters:
                self.stdout.write(f'  Filters: {", ".join(filters)}')

            count = NewsDataService.fetch_and_store_news(
                state_name=state_name,
                district_name=district_name,
                category=category
            )

            if count > 0:
                total_news = FetchedNews.objects.count()
                self.stdout.write(
                    self.style.SUCCESS(
                        'News fetched successfully!'
                    )
                )
                self.stdout.write(
                    f'  Articles added: {count}'
                )
                self.stdout.write(
                    f'  Total articles in database: {total_news}'
                )
            else:
                self.stdout.write(
                    self.style.WARNING('No new articles found')
                )
        except Exception as e:
            raise CommandError(f'Error fetching news: {str(e)}')
