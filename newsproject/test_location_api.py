#!/usr/bin/env python
"""
Test script for Location-Based News API endpoints
Run this after the Django server is running: python manage.py runserver
"""

import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newsproject.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from news.models import State, District, FetchedNews

def test_api_endpoints():
    """Test all location and news API endpoints"""
    client = Client()
    base_url = 'http://localhost:8000'

    print("\n" + "="*60)
    print("LOCATION-BASED NEWS API TESTS")
    print("="*60)

    # Test 1: Get all states
    print("\n[TEST 1] Get all states")
    response = client.get('/api/states/')
    if response.status_code == 200:
        data = response.json()
        print(f"[OK] States endpoint working")
        print(f"  Total states: {len(data['states'])}")
        if data['states']:
            print(f"  Sample: {data['states'][0]['name']}")
    else:
        print(f"[FAIL] States endpoint failed: {response.status_code}")

    # Test 2: Get districts for first state
    print("\n[TEST 2] Get districts for Andhra Pradesh")
    state = State.objects.filter(name='Andhra Pradesh').first()
    if state:
        response = client.get(f'/api/districts/?state_id={state.id}')
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Districts endpoint working")
            print(f"  Total districts: {len(data['districts'])}")
            if data['districts']:
                print(f"  Sample: {data['districts'][0]['name']}")
        else:
            print(f"[FAIL] Districts endpoint failed: {response.status_code}")

    # Test 3: Get blocks for first district
    print("\n[TEST 3] Get blocks for first district")
    district = District.objects.first()
    if district:
        response = client.get(f'/api/blocks/?district_id={district.id}')
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Blocks endpoint working")
            print(f"  Total blocks: {len(data['blocks'])}")
            if data['blocks']:
                print(f"  Sample: {data['blocks'][0]['name']}")
        else:
            print(f"[FAIL] Blocks endpoint failed: {response.status_code}")

    # Test 4: Get news by location (no news yet, but endpoint should work)
    print("\n[TEST 4] Get news by location")
    if state:
        response = client.get(f'/api/news-by-location/?state_id={state.id}&limit=5')
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] News by location endpoint working")
            print(f"  Articles found: {data['count']}")
            if data['news']:
                print(f"  Sample: {data['news'][0]['title']}")
        else:
            print(f"[FAIL] News endpoint failed: {response.status_code}")

    # Test 5: Test database statistics
    print("\n[TEST 5] Database Statistics")
    print(f"  States: {State.objects.count()}")
    print(f"  Districts: {District.objects.count()}")
    print(f"  Fetched News: {FetchedNews.objects.count()}")

    print("\n" + "="*60)
    print("TESTS COMPLETED")
    print("="*60)
    print("\nNext steps:")
    print("1. Fetch news articles:")
    print("   python manage.py fetch_news_and_locations --fetch-news")
    print("\n2. Test news retrieval endpoints again")
    print("\n3. Check admin panel at /admin/")
    print("\n")

if __name__ == '__main__':
    test_api_endpoints()
