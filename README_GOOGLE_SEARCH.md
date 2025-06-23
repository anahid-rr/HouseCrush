# House Crush - Google Custom Search API Integration

## Overview

House Crush now features Google Custom Search API integration, providing real-time rental property search across multiple websites with intelligent filtering and ranking.

## 🎯 Features

### **Real-time Search**
- **Multi-site Search**: Searches across major rental platforms simultaneously
- **Intelligent Filtering**: Price, location, bedrooms, amenities, and lifestyle filtering
- **Smart Ranking**: Calculates match percentages based on search criteria
- **Rich Results**: Extracts contact information, pricing, and property details

### **Search Sources**
The Google Custom Search API searches across multiple rental platforms:
- **Zillow.com**
- **Apartments.com**
- **Rent.com**
- **PadMapper.com**
- **RentFaster.ca** (Canadian listings)
- **Kijiji.ca** (Canadian listings)
- **Craigslist.org**
- **Realtor.com**
- **Rentals.ca**
- **Viewit.ca**

### **Advanced Features**
- **Price Extraction**: Automatically extracts rental prices from search results
- **Contact Information**: Finds phone numbers and email addresses
- **Amenity Detection**: Identifies available amenities from property descriptions
- **Match Scoring**: Calculates compatibility percentages (0-100%)
- **Direct Links**: Provides direct URLs to property listings

## 🚀 Setup Instructions

### 1. Google Cloud Console Setup

#### Step 1: Create/Select Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your Project ID

#### Step 2: Enable Custom Search API
1. Navigate to **APIs & Services** > **Library**
2. Search for "Custom Search API"
3. Click on "Custom Search API"
4. Click **Enable**

#### Step 3: Create API Credentials
1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **API Key**
3. Copy the generated API key
4. (Optional) Restrict the API key to Custom Search API only

### 2. Create Custom Search Engine

#### Step 1: Create Search Engine
1. Go to [Programmable Search Engine](https://programmablesearchengine.google.com/)
2. Click **Create a search engine**
3. Enter any website (e.g., `google.com`) - this is just a placeholder
4. Click **Create**

#### Step 2: Configure Search Engine
1. Click on your created search engine
2. Go to **Setup** tab
3. Under **Sites to search**, add rental websites:
   ```
   zillow.com
   apartments.com
   rent.com
   padmapper.com
   rentfaster.ca
   kijiji.ca
   craigslist.org
   realtor.com
   rentals.ca
   viewit.ca
   ```
4. Set **Search the entire web** to **Yes**
5. Save changes

#### Step 3: Get Search Engine ID
1. In the **Setup** tab, find your **Search engine ID**
2. Copy the ID (format: `123456789012345678901:abcdefghijk`)

### 3. Environment Configuration

Add the following to your `.env` file:
```env
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
```

### 4. Test the Integration

Run the test script to verify everything is working:
```bash
python test_google_search.py
```

## 📊 API Usage

### Basic Search
```python
from google_rental_search import search_rentals_with_google

results = search_rentals_with_google(
    location="Toronto",
    min_price=1500,
    max_price=2500,
    bedrooms=2,
    amenities=["Parking", "Gym"],
    lifestyle="near public transit"
)
```

### Response Format
Each search result includes:
```json
{
  "id": 1,
  "title": "Property title",
  "price": 2000,
  "location": "Toronto",
  "bedrooms": 2,
  "bathrooms": 1,
  "amenities": ["Parking", "Gym", "Balcony"],
  "description": "Property description",
  "match_percentage": 85,
  "contact": {
    "name": "Agent Name",
    "phone": "123-456-7890",
    "email": "agent@example.com"
  },
  "source_website": "Zillow",
  "listing_url": "https://zillow.com/property/123",
  "availability_date": "2024-01-15",
  "features": [],
  "images": []
}
```

## 🔧 Configuration Options

### Search Parameters
- **location**: City or area to search
- **min_price**: Minimum rental price
- **max_price**: Maximum rental price
- **bedrooms**: Number of bedrooms required
- **amenities**: List of required amenities
- **lifestyle**: Lifestyle preferences

### API Limits
- **Free Tier**: 100 searches per day
- **Paid Tier**: $5 per 1000 searches
- **Rate Limit**: 10,000 searches per day

## 🎯 Match Scoring System

The system calculates match percentages based on:
- **Location Match (30%)**: Proximity to desired area
- **Price Range Match (25%)**: Budget compatibility
- **Bedroom/Bathroom Match (20%)**: Size requirements
- **Amenities Match (15%)**: Desired features
- **Availability Match (10%)**: Current availability

## 📁 File Storage

Search results are automatically saved to:
- `results/google_custom_search_response_TIMESTAMP.json` - Raw API responses
- `results/google_rental_search_results_LOCATION_TIMESTAMP.json` - Processed search results

## 🚀 Performance

- **Response Time**: 2-5 seconds
- **Results**: Up to 10 results per search
- **Accuracy**: High accuracy with intelligent filtering
- **Cost**: Very cost-effective compared to other APIs

## 🔍 Search Query Examples

### Basic Location Search
```
rental apartments Toronto
```

### Price Range Search
```
rental apartments Toronto $1500-$2500 rent
```

### Bedroom Search
```
2 bedroom rental apartments Toronto
```

### Amenity Search
```
rental apartments Toronto with parking gym balcony
```

### Lifestyle Search
```
rental apartments Toronto near public transit quiet neighborhood
```

## 🛠️ Troubleshooting

### Common Issues

1. **API Key Not Working**
   - Ensure the API key is correct
   - Check if Custom Search API is enabled
   - Verify API key restrictions

2. **Search Engine ID Issues**
   - Ensure the Search Engine ID is correct
   - Check if search engine is configured properly
   - Verify sites are added to search engine

3. **No Results Found**
   - Try broader search terms
   - Check if location has available rentals
   - Verify search engine configuration

4. **Rate Limiting**
   - Check your daily quota usage
   - Consider upgrading to paid tier
   - Implement request caching

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Cost Analysis

### Free Tier (100 searches/day)
- **Daily Cost**: $0
- **Monthly Cost**: $0
- **Suitable for**: Development and testing

### Paid Tier
- **Cost**: $5 per 1,000 searches
- **Daily Limit**: 10,000 searches
- **Suitable for**: Production applications

## 🔄 Integration with House Crush

The Google Custom Search integration works alongside:
- **OpenAI GPT-4o-mini**: For AI-powered search
- **Local Database**: For offline search
- **Together AI**: For result ranking

### Usage in Web Interface
1. Select "Google Custom Search" from the search method dropdown
2. Enter your search criteria
3. Click "Find Properties"
4. View results with match percentages and contact information

## 🚀 Future Enhancements

- **Image Integration**: Display property photos
- **Map Integration**: Visual property locations
- **Saved Searches**: User account with search history
- **Notifications**: Alert when new matching properties are available
- **Comparative Analysis**: Side-by-side property comparisons
- **Advanced Filtering**: More granular search options

## 📞 Support

For issues or questions:
1. Check the logs in the `results/` directory
2. Run the test script to verify API connectivity
3. Review the error messages for specific issues
4. Ensure all dependencies are properly installed
5. Verify Google Cloud Console configuration

## 📚 Additional Resources

- [Google Custom Search API Documentation](https://developers.google.com/custom-search/v1/using_rest)
- [Google Cloud Console](https://console.cloud.google.com/)
- [Programmable Search Engine](https://programmablesearchengine.google.com/)
- [API Quotas and Pricing](https://developers.google.com/custom-search/v1/introduction#quota) 