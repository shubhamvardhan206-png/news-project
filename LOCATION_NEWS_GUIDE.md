# Location-Based News System Setup Guide

## Overview
This guide explains how to use the new location-based news fetching system that integrates REST India API and NewsData.io.

## Features

### 1. Location Hierarchy
- **States**: 28 Indian states/UTs
- **Districts**: 183 districts across all states
- **Blocks**: 549 blocks across all districts

### 2. News Management
- Fetch news articles from NewsData.io filtered by location
- Store news in the database with location tags
- Query news by state, district, or category
- Track views and engagement

## Setup Instructions

### Step 1: Install Dependencies
All required packages are listed in `requirements.txt`:
```bash
pip install -r requirements.txt
```

### Step 2: Get API Keys

#### NewsData.io API Key
1. Visit https://newsdata.io/
2. Sign up for a free account
3. Get your API key from the dashboard
4. Set it as environment variable:
   ```bash
   set NEWSDATA_API_KEY=your_api_key_here
   ```
   Or add to `.env` file:
   ```
   NEWSDATA_API_KEY=your_api_key_here
   ```

### Step 3: Initialize Location Data
The location data (states, districts, blocks) is automatically populated when you run:

```bash
python manage.py fetch_news_and_locations --fetch-locations
```

This command:
- Fetches all 28 Indian states
- Fetches 183 districts across all states
- Fetches 549 blocks across all districts
- Stores everything in the database

**Status after running:**
- States: 28
- Districts: 183
- Blocks: 549

## API Endpoints

### 1. Get All States
**Endpoint**: `/api/states/`
**Method**: GET
**Response**:
```json
{
  "states": [
    {
      "id": 1,
      "name": "Andhra Pradesh",
      "code": "AP"
    },
    ...
  ]
}
```

### 2. Get Districts by State
**Endpoint**: `/api/districts/?state_id=1`
**Method**: GET
**Parameters**:
- `state_id`: (required) ID of the state

**Response**:
```json
{
  "districts": [
    {
      "id": 1,
      "name": "Anantapur",
      "state__name": "Andhra Pradesh"
    },
    ...
  ]
}
```

### 3. Get Blocks by District
**Endpoint**: `/api/blocks/?district_id=1`
**Method**: GET
**Parameters**:
- `district_id`: (required) ID of the district

**Response**:
```json
{
  "blocks": [
    {
      "id": 1,
      "name": "Anantapur Block 1",
      "district__name": "Anantapur"
    },
    ...
  ]
}
```

### 4. Get News by Location
**Endpoint**: `/api/news-by-location/`
**Method**: GET
**Parameters**:
- `state_id`: (optional) Filter by state
- `district_id`: (optional) Filter by district
- `category`: (optional) Filter by category
- `limit`: (optional, default: 20) Number of articles

**Response**:
```json
{
  "news": [
    {
      "id": 1,
      "title": "Breaking News Title",
      "description": "Article description...",
      "image_url": "https://...",
      "source_url": "https://...",
      "source_name": "News Source",
      "category": "Business",
      "published_at": "2026-05-26T10:30:00Z",
      "views": 42
    },
    ...
  ],
  "count": 20
}
```

### 5. Fetch News for Location (Admin Only)
**Endpoint**: `/api/fetch-news-location/`
**Method**: GET
**Authentication**: Requires staff/admin user
**Parameters**:
- `state_id`: (optional) Fetch news for this state
- `district_id`: (optional) Fetch news for this district
- `category`: (optional) Fetch news for this category

**Response**:
```json
{
  "success": true,
  "articles_added": 15
}
```

## Management Commands

### Fetch Location Data
```bash
python manage.py fetch_news_and_locations --fetch-locations
```

### Fetch News Articles
Fetch news for entire India:
```bash
python manage.py fetch_news_and_locations --fetch-news
```

Fetch news for a specific state:
```bash
python manage.py fetch_news_and_locations --fetch-news --state "Maharashtra"
```

Fetch news for a specific district:
```bash
python manage.py fetch_news_and_locations --fetch-news --state "Maharashtra" --district "Mumbai"
```

Fetch news by category:
```bash
python manage.py fetch_news_and_locations --fetch-news --category "Technology"
```

### Fetch All Data
```bash
python manage.py fetch_news_and_locations --all
```

This will:
- Fetch all location data (states, districts, blocks)
- Fetch news articles for all of India

## Admin Panel Access

### Location Management
- **States**: Admin → News → States
- **Districts**: Admin → News → Districts
- **Blocks**: Admin → News → Blocks

### News Management
- **Fetched News**: Admin → News → Fetched News
  - View all fetched articles
  - Filter by state, district, category, language
  - Toggle active status
  - Monitor view counts

## Database Models

### State
- `name`: State name (unique)
- `code`: State code (e.g., "MH" for Maharashtra)
- Relations: Has many districts

### District
- `state`: Foreign key to State
- `name`: District name
- Relations: Belongs to State, has many blocks

### Block
- `district`: Foreign key to District
- `name`: Block name
- Relations: Belongs to District

### FetchedNews
- `title`: Article title
- `description`: Article description
- `content`: Full article content
- `image_url`: URL to article image
- `source_url`: URL to original article (unique)
- `source_name`: Name of news source
- `country`: Country (default: "India")
- `state`: Optional link to State
- `district`: Optional link to District
- `block`: Optional link to Block
- `category`: News category
- `language`: Article language (default: "en")
- `published_at`: When article was published
- `fetched_at`: When article was fetched (auto)
- `updated_at`: Last update time (auto)
- `views`: Number of times article was viewed
- `is_active`: Whether article is displayed
- Indexes: state + published_at, district + published_at, category + published_at

## Frontend Integration Example

### JavaScript - Populate Location Dropdowns
```javascript
// Get states
fetch('/api/states/')
  .then(r => r.json())
  .then(data => {
    // Populate state dropdown
    data.states.forEach(state => {
      console.log(state.name, state.code);
    });
  });

// Get districts for selected state
const stateId = 1;
fetch(`/api/districts/?state_id=${stateId}`)
  .then(r => r.json())
  .then(data => {
    // Populate district dropdown
    data.districts.forEach(district => {
      console.log(district.name);
    });
  });

// Get blocks for selected district
const districtId = 1;
fetch(`/api/blocks/?district_id=${districtId}`)
  .then(r => r.json())
  .then(data => {
    // Populate block dropdown
    data.blocks.forEach(block => {
      console.log(block.name);
    });
  });

// Get news for selected location
const params = new URLSearchParams({
  state_id: 1,
  category: 'Technology',
  limit: 20
});
fetch(`/api/news-by-location/?${params}`)
  .then(r => r.json())
  .then(data => {
    // Display news articles
    data.news.forEach(article => {
      console.log(article.title, article.source_name);
    });
  });
```

## Troubleshooting

### Issue: No news articles found
**Solution**: 
1. Verify NewsData.io API key is set correctly
2. Check API quota hasn't been exceeded
3. Try fetching with broader parameters (remove district filter)

### Issue: Cache key warnings
**Solution**: These warnings are only for memcached. For development (SQLite cache), they're safe to ignore.

### Issue: Duplicate articles
**Solution**: 
- The system checks for duplicate `source_url` before storing
- If you see duplicates, check the article URL handling

## Performance Optimization

1. **Caching**: Location data is cached for 24 hours
2. **Indexing**: FetchedNews has indexes on state + date, district + date, category + date
3. **Pagination**: Use `limit` parameter to control response size
4. **Filtering**: Always filter by state/district when possible for faster queries

## Future Enhancements

1. Real REST India API integration (currently using pre-defined data)
2. Real-time news updates with background tasks (Celery)
3. News aggregation from multiple sources
4. Trending topics by location
5. User preference-based news recommendations
6. Search across location hierarchy

## Support

For issues or questions:
1. Check the admin panel for data
2. Verify API keys are set correctly
3. Review Django logs for errors
4. Test endpoints directly with curl or Postman
