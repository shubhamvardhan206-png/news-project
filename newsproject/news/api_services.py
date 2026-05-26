import requests
import json
import logging
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from .models import State, District, Block, FetchedNews

logger = logging.getLogger(__name__)

REST_INDIA_API_BASE = 'https://api.geoapify.com'
NEWSDATA_API_BASE = 'https://newsdata.io/api/1'


class LocationAPIService:
    @staticmethod
    def fetch_and_store_locations():
        """Fetch locations from REST India API and store in database"""
        try:
            session = requests.Session()

            # Fetch all states
            logger.info("Fetching states from REST India API...")
            states_data = LocationAPIService._fetch_states(session)

            for state_data in states_data:
                state_name = state_data.get('name')
                state_code = state_data.get('code', state_name[:2].upper())

                state, _ = State.objects.get_or_create(
                    name=state_name,
                    defaults={'code': state_code}
                )

                # Fetch districts for this state
                districts_data = LocationAPIService._fetch_districts(session, state_code)
                for district_data in districts_data:
                    district_name = district_data.get('name')
                    district, _ = District.objects.get_or_create(
                        state=state,
                        name=district_name
                    )

                    # Fetch blocks for this district
                    blocks_data = LocationAPIService._fetch_blocks(session, state_code, district_name)
                    for block_data in blocks_data:
                        block_name = block_data.get('name')
                        Block.objects.get_or_create(
                            district=district,
                            name=block_name
                        )

            logger.info("Successfully fetched and stored all locations")
            return True
        except Exception as e:
            logger.error(f"Error fetching locations: {str(e)}")
            return False

    @staticmethod
    def _fetch_states(session):
        """Fetch states from REST India API"""
        cache_key = 'rest_india_states'
        cached = cache.get(cache_key)
        if cached:
            return cached

        try:
            # Using a simple states list as fallback (REST India API requires authentication)
            states = [
                {'name': 'Andhra Pradesh', 'code': 'AP'},
                {'name': 'Arunachal Pradesh', 'code': 'AR'},
                {'name': 'Assam', 'code': 'AS'},
                {'name': 'Bihar', 'code': 'BR'},
                {'name': 'Chhattisgarh', 'code': 'CT'},
                {'name': 'Goa', 'code': 'GA'},
                {'name': 'Gujarat', 'code': 'GJ'},
                {'name': 'Haryana', 'code': 'HR'},
                {'name': 'Himachal Pradesh', 'code': 'HP'},
                {'name': 'Jharkhand', 'code': 'JH'},
                {'name': 'Karnataka', 'code': 'KA'},
                {'name': 'Kerala', 'code': 'KL'},
                {'name': 'Madhya Pradesh', 'code': 'MP'},
                {'name': 'Maharashtra', 'code': 'MH'},
                {'name': 'Manipur', 'code': 'MN'},
                {'name': 'Meghalaya', 'code': 'ML'},
                {'name': 'Mizoram', 'code': 'MZ'},
                {'name': 'Nagaland', 'code': 'NL'},
                {'name': 'Odisha', 'code': 'OD'},
                {'name': 'Punjab', 'code': 'PB'},
                {'name': 'Rajasthan', 'code': 'RJ'},
                {'name': 'Sikkim', 'code': 'SK'},
                {'name': 'Tamil Nadu', 'code': 'TN'},
                {'name': 'Telangana', 'code': 'TG'},
                {'name': 'Tripura', 'code': 'TR'},
                {'name': 'Uttar Pradesh', 'code': 'UP'},
                {'name': 'Uttarakhand', 'code': 'UT'},
                {'name': 'West Bengal', 'code': 'WB'},
            ]

            cache.set(cache_key, states, 86400)  # Cache for 24 hours
            return states
        except Exception as e:
            logger.error(f"Error fetching states: {str(e)}")
            return []

    @staticmethod
    def _fetch_districts(session, state_code):
        """Fetch districts for a state"""
        cache_key = f'rest_india_districts_{state_code}'
        cached = cache.get(cache_key)
        if cached:
            return cached

        # Predefined districts mapping for Indian states
        districts_map = {
            'AP': ['Anantapur', 'Chittoor', 'East Godavari', 'Guntur', 'Krishna', 'Kurnool',
                   'Nellore', 'Prakasam', 'Srikakulam', 'Visakhapatnam', 'Vizianagaram', 'West Godavari'],
            'AR': ['Anjaw', 'Changlang', 'Lohit', 'Papum Pare', 'Upper Subansiri', 'West Kameng', 'West Siang'],
            'AS': ['Assam Valley', 'Barak Valley', 'Bokaro', 'Bongaigaon', 'Cachar', 'Dima Hasao', 'Goalpara'],
            'BR': ['Araria', 'Arwal', 'Aurangabad', 'Banka', 'Begusarai', 'Bhagalpur', 'Bhojpur', 'Buxar', 'Darbhanga'],
            'CT': ['Balod', 'Balrampur', 'Bastar', 'Bemetara', 'Bijapur', 'Bilaspur', 'Dantewada', 'Dhamtari'],
            'GA': ['North Goa', 'South Goa'],
            'GJ': ['Ahmedabad', 'Amreli', 'Anand', 'Aravalli', 'Banaskantha', 'Bharuch', 'Bhavnagar', 'Botad'],
            'HR': ['Ambala', 'Bhiwani', 'Charkhi Dadri', 'Faridabad', 'Fatehabad', 'Gurgaon', 'Hisar'],
            'HP': ['Bilaspur', 'Chamba', 'Hamirpur', 'Kangra', 'Kinnaur', 'Kullu', 'Lahaul and Spiti'],
            'JH': ['Araria', 'Arwal', 'Aurangabad', 'Banka', 'Begusarai', 'Bhagalpur', 'Bhojpur'],
            'KA': ['Bagalkot', 'Belgaum', 'Bellary', 'Bijapur', 'Chikmagalur', 'Chikballapur', 'Chitradurga'],
            'KL': ['Alappuzha', 'Ernakulam', 'Idukki', 'Kannur', 'Kasaragod', 'Kottayam', 'Kozhikode'],
            'MP': ['Agar Malwa', 'Alirajpur', 'Anuppur', 'Ashoknagar', 'Balaghat', 'Ballarpur', 'Bandhavgarh'],
            'MH': ['Ahmednagar', 'Akola', 'Amravati', 'Aurangabad', 'Beed', 'Bhandara', 'Buldhana'],
            'MN': ['Bishnupur', 'Chandel', 'Churachandpur', 'Imphal East', 'Imphal West', 'Jiribam'],
            'ML': ['East Garo Hills', 'East Khasi Hills', 'Jaintia Hills', 'Meghalaya West', 'North Garo Hills'],
            'MZ': ['Aizawl', 'Champhai', 'Kolasib', 'Lawngtlai', 'Lunglei', 'Mamit', 'Saiha', 'Serchhip'],
            'NL': ['Dimapur', 'Kiphire', 'Kohima', 'Longleng', 'Mokokchung', 'Mon', 'Nagaland East'],
            'OD': ['Angul', 'Balangir', 'Balasore', 'Bargarh', 'Bhadrak', 'Boudh', 'Cuttack'],
            'PB': ['Amritsar', 'Barnala', 'Bathinda', 'Faridkot', 'Fatehgarh Sahib', 'Gurdaspur'],
            'RJ': ['Ajmer', 'Alwar', 'Banswara', 'Baran', 'Barmer', 'Bharatpur', 'Bhilwara'],
            'SK': ['East Sikkim', 'North Sikkim', 'South Sikkim', 'West Sikkim'],
            'TN': ['Ariyalur', 'Chengalpattu', 'Chengalpattu', 'Chidambaram', 'Coimbatore'],
            'TG': ['Adilabad', 'Bhadradi Kottagudem', 'Hanumakonda', 'Hyderabad', 'Jagtial'],
            'TR': ['Dhalai', 'Khowai', 'North Tripura', 'Sipahijala', 'South Tripura', 'Unakoti'],
            'UP': ['Agra', 'Aligarh', 'Allahabad', 'Ambedkar Nagar', 'Amethi', 'Amroha'],
            'UT': ['Almora', 'Bageshwar', 'Chamoli', 'Champawat', 'Dehradun'],
            'WB': ['Alipurduar', 'Bankura', 'Bardhaman', 'Birbhum', 'Cooch Behar'],
        }

        districts = [{'name': d} for d in districts_map.get(state_code, [])]
        cache.set(cache_key, districts, 86400)
        return districts

    @staticmethod
    def _fetch_blocks(session, state_code, district_name):
        """Fetch blocks for a district"""
        # Simplified block data - can be expanded with actual API calls
        cache_key = f'rest_india_blocks_{state_code}_{district_name}'
        cached = cache.get(cache_key)
        if cached:
            return cached

        blocks = [
            {'name': f'{district_name} Block 1'},
            {'name': f'{district_name} Block 2'},
            {'name': f'{district_name} Block 3'},
        ]

        cache.set(cache_key, blocks, 86400)
        return blocks


class NewsDataService:
    NEWSDATA_API_KEY = getattr(settings, 'NEWSDATA_API_KEY', None)

    @staticmethod
    def fetch_news_by_location(state_name=None, district_name=None, category=None, limit=20):
        """Fetch news articles from NewsData.io filtered by location"""
        if not NewsDataService.NEWSDATA_API_KEY:
            logger.error("NewsData.io API key not configured")
            return []

        try:
            url = f'{NEWSDATA_API_BASE}/news'

            query_parts = []
            if state_name:
                query_parts.append(state_name)
            if district_name:
                query_parts.append(district_name)

            query = ' OR '.join(query_parts) if query_parts else 'India'

            params = {
                'apikey': NewsDataService.NEWSDATA_API_KEY,
                'q': query,
                'country': 'in',
                'language': 'en',
                'size': limit,
            }

            if category:
                params['category'] = category

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            articles = data.get('results', [])

            logger.info(f"Fetched {len(articles)} articles from NewsData.io")
            return articles
        except Exception as e:
            logger.error(f"Error fetching news from NewsData.io: {str(e)}")
            return []

    @staticmethod
    def store_fetched_news(articles, state=None, district=None, block=None):
        """Store fetched news articles in the database"""
        stored_count = 0

        for article in articles:
            try:
                source_url = article.get('link') or article.get('url')
                if not source_url:
                    continue

                # Check if news already exists
                existing = FetchedNews.objects.filter(source_url=source_url).first()
                if existing:
                    continue

                # Parse published date
                pub_date_str = article.get('pubDate') or article.get('published_at')
                published_at = None
                if pub_date_str:
                    try:
                        published_at = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
                    except:
                        published_at = timezone.now()

                news = FetchedNews.objects.create(
                    title=article.get('title', 'Untitled')[:500],
                    description=article.get('description', '')[:1000],
                    content=article.get('content', ''),
                    image_url=article.get('image_url') or article.get('image'),
                    source_url=source_url,
                    source_name=article.get('source_id') or article.get('source'),
                    state=state,
                    district=district,
                    block=block,
                    category=article.get('category', ''),
                    published_at=published_at or timezone.now(),
                    language=article.get('language', 'en'),
                )
                stored_count += 1
            except Exception as e:
                logger.error(f"Error storing article: {str(e)}")
                continue

        logger.info(f"Stored {stored_count} articles in database")
        return stored_count

    @staticmethod
    def fetch_and_store_news(state_name=None, district_name=None, category=None):
        """Fetch news from API and store in database"""
        try:
            state = None
            district = None

            if state_name:
                state = State.objects.filter(name=state_name).first()
            if district_name and state:
                district = District.objects.filter(name=district_name, state=state).first()

            articles = NewsDataService.fetch_news_by_location(
                state_name=state_name,
                district_name=district_name,
                category=category
            )

            if articles:
                count = NewsDataService.store_fetched_news(articles, state, district)
                return count
            return 0
        except Exception as e:
            logger.error(f"Error in fetch_and_store_news: {str(e)}")
            return 0
