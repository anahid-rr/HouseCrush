# House Crush - OpenAI Conversational Search Integration

## Overview

House Crush now features an advanced OpenAI-powered conversational search system that provides real-time rental property listings with intelligent matching and detailed information.

## New Features

### 🎯 Conversational Search
- **Natural Language Processing**: Uses GPT-4 to understand user preferences in natural language
- **Real-time Search**: Searches multiple rental websites simultaneously
- **Intelligent Matching**: Calculates match percentages based on user criteria
- **Top 10 Results**: Returns the best 10 properties with 80%+ match scores

### 🏠 Enhanced Property Information
- **Exact Listing URLs**: Direct links to property listings
- **Complete Contact Information**: Agent names, phone numbers, and email addresses
- **Match Percentages**: Visual indicators showing how well properties match criteria
- **Detailed Amenities**: Both predefined and custom amenity options
- **Lifestyle Preferences**: Support for lifestyle-based searches

### 📊 Match Scoring System
The AI calculates match percentages based on:
- **Location Match (30%)**: Proximity to desired area
- **Price Range Match (25%)**: Budget compatibility
- **Bedroom/Bathroom Match (20%)**: Size requirements
- **Amenities Match (15%)**: Desired features
- **Lifestyle Preferences (10%)**: Neighborhood characteristics

### 🔧 Custom Amenities
Users can now add custom amenities beyond the predefined options:
- **Checkbox Options**: Quick selection of common amenities (Parking, Storage, Pool, Bike Storage)
- **Custom Input Fields**: Add any specific amenities (Gym, Balcony, In-unit Laundry, etc.)
- **Dynamic Fields**: Add/remove custom amenity fields as needed

## Setup Instructions

### 1. Environment Variables
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Test the Integration
```bash
python test_openai_search.py
```

## Usage

### Web Interface
1. Navigate to the property search section
2. Enter your location, budget, and bedroom requirements
3. Select common amenities from checkboxes
4. Add custom amenities using the input fields
5. Describe your lifestyle preferences
6. Click "Find Properties with AI"

### API Usage
```python
from openai_rental_search import search_rentals_with_openai

results = search_rentals_with_openai(
    location="Toronto",
    min_price=1500,
    max_price=2500,
    bedrooms=2,
    amenities=["Parking", "Gym", "Balcony"],
    lifestyle="near public transit, quiet neighborhood"
)
```

## Search Sources

The AI searches across multiple rental platforms:
- **Zillow.com**
- **Apartments.com**
- **Rent.com**
- **PadMapper.com**
- **RentFaster.ca** (Canadian listings)
- **Kijiji.ca** (Canadian listings)
- **Craigslist.org**
- **Realtor.com**

## Output Format

Each search result includes:
```json
{
  "id": "unique_id",
  "title": "Property title",
  "price": 2000,
  "location": "exact address/area",
  "bedrooms": 2,
  "bathrooms": 1,
  "amenities": ["Parking", "Gym", "Balcony"],
  "description": "detailed description",
  "match_percentage": 85,
  "contact": {
    "name": "agent name",
    "phone": "phone number",
    "email": "email address"
  },
  "source_website": "website name",
  "listing_url": "exact listing URL",
  "availability_date": "2024-01-15",
  "features": ["feature1", "feature2"],
  "images": ["image_url1", "image_url2"]
}
```

## File Storage

Search results are automatically saved to:
- `results/openai_conversational_response_TIMESTAMP.json` - Raw API responses
- `results/rental_search_results_LOCATION_TIMESTAMP.json` - Processed search results

## Error Handling

The system includes comprehensive error handling:
- **API Connection Issues**: Graceful fallback with informative messages
- **Invalid Responses**: JSON parsing with fallback text extraction
- **Missing Data**: Default values for incomplete listings
- **Rate Limiting**: Automatic retry logic

## Performance

- **Response Time**: Typically 30-60 seconds for comprehensive searches
- **Token Usage**: Optimized for cost-effectiveness while maintaining quality
- **Caching**: Results are saved locally for debugging and analysis

## Troubleshooting

### Common Issues

1. **API Key Not Set**
   - Ensure `OPENAI_API_KEY` is set in your `.env` file
   - Check the API key is valid and has sufficient credits

2. **No Results Found**
   - Try broadening your search criteria
   - Check if the location has available rentals
   - Verify your price range is realistic for the area

3. **Slow Response Times**
   - This is normal for comprehensive searches
   - The AI is searching multiple sources simultaneously
   - Results are worth the wait for quality matches

### Debug Mode

Enable detailed logging by setting the log level:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

- **Image Integration**: Display actual property photos
- **Map Integration**: Visual property locations
- **Saved Searches**: User account with search history
- **Notifications**: Alert when new matching properties are available
- **Comparative Analysis**: Side-by-side property comparisons

## Support

For issues or questions:
1. Check the logs in the `results/` directory
2. Run the test script to verify API connectivity
3. Review the error messages for specific issues
4. Ensure all dependencies are properly installed 