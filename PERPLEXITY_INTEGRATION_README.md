# Perplexity API Integration for House Crush

This document explains how to set up and use the Perplexity API integration for real-time rental property search in House Crush.

## Overview

The Perplexity API integration allows House Crush to search for rental listings in real-time across multiple rental websites including:
- Apartments.com
- Zillow.com
- RentalFast.ca
- PadMapper.com

This provides users with up-to-date rental information without needing to pre-collect data.

## Features

- **Real-time Search**: Search for rental listings as they become available
- **Multi-source Search**: Searches across multiple rental platforms simultaneously
- **Intelligent Parsing**: Extracts structured data from search results
- **Fallback Handling**: Provides useful information even when structured data isn't available
- **API Status Monitoring**: Real-time status checking of API connectivity

## Setup Instructions

### 1. Get Perplexity API Key

1. Visit [Perplexity API Settings](https://www.perplexity.ai/settings/api)
2. Sign up for a free account if you don't have one
3. Navigate to the API section
4. Create a new API key
5. Copy the API key

### 2. Configure Environment

Add your API key to the `.env` file:

```bash
PERPLEXITY_API_KEY=your_api_key_here
```

Or use the setup script:

```bash
python setup_env.py
```

### 3. Install Dependencies

The required dependencies are already included in `requirements.txt`:

```bash
pip install -r requirements.txt
```

**Note**: The integration uses direct HTTP requests to the Perplexity API, so no additional SDK is required.

## Usage

### In the Web Application

1. Start the application:
   ```bash
   python app.py
   ```

2. Navigate to the web interface
3. Select "Perplexity API" as your search method
4. Enter your search criteria:
   - Location (required)
   - Price range (optional)
   - Number of bedrooms (optional)
5. Click "Search Properties"
6. View real-time results from multiple rental platforms

### Programmatic Usage

```python
from perplexity_rental_search import search_rentals_with_perplexity, get_perplexity_status

# Check API status
status = get_perplexity_status()
print(f"API Status: {status['status']}")

# Search for rentals
listings = search_rentals_with_perplexity(
    location="Toronto",
    min_price=1500,
    max_price=2500,
    bedrooms=2
)

for listing in listings:
    print(f"{listing['title']} - ${listing['price']}")
```

## API Endpoint

The integration uses the official Perplexity API endpoint:
- **URL**: `https://api.perplexity.ai/chat/completions`
- **Method**: POST
- **Authentication**: Bearer token
- **Model**: `sonar-medium-online` (for real-time search capabilities)

For detailed API documentation, visit: [Perplexity API Reference](https://docs.perplexity.ai/api-reference/chat-completions-post)

## Response Format

The API returns rental listings in the following format:

```json
{
  "id": 1,
  "title": "Modern 2BR Apartment",
  "price": 2200,
  "location": "Toronto, ON",
  "bedrooms": 2,
  "bathrooms": 1,
  "amenities": ["Gym", "Pool", "Parking"],
  "description": "Beautiful modern apartment...",
  "contact": {
    "name": "Property Manager",
    "phone": "N/A",
    "email": "N/A"
  },
  "source_website": "Apartments.com",
  "availability_date": "2024-01-15",
  "collected_date": "2024-01-15T10:30:00",
  "source": "Perplexity API",
  "match_score": 85,
  "match_reason": "Real-time search result from Perplexity API"
}
```

## Error Handling

The integration includes comprehensive error handling:

- **API Key Missing**: Graceful fallback with informative messages
- **Network Errors**: Timeout handling and retry logic
- **Rate Limiting**: Respects API rate limits
- **Invalid Responses**: Fallback to text parsing when JSON extraction fails
- **No Results**: Provides helpful feedback and suggestions

## Testing

Run the test script to verify your setup:

```bash
python test_perplexity.py
```

This will:
- Check API connectivity
- Test a sample search
- Verify response parsing
- Show setup instructions if needed

## Troubleshooting

### Common Issues

1. **"API key not set"**
   - Ensure `PERPLEXITY_API_KEY` is in your `.env` file
   - Check that the key is valid and active

2. **"API Error: 401"**
   - Invalid or expired API key
   - Regenerate your API key

3. **"API Error: 429"**
   - Rate limit exceeded
   - Wait a few minutes before trying again

4. **"No listings found"**
   - Check your search criteria
   - Try a different location or price range
   - Verify internet connectivity

5. **"Connection Error"**
   - Check your internet connection
   - Verify firewall settings
   - Try again later

### Debug Mode

Enable debug logging by setting the log level:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Rate Limits

The Perplexity API has rate limits that vary by plan:
- **Free Tier**: Limited requests per minute
- **Paid Plans**: Higher rate limits

The integration respects these limits and will provide appropriate error messages when exceeded.

## Security

- API keys are stored in environment variables (`.env` file)
- Never commit API keys to version control
- The `.env` file is already in `.gitignore`
- All API requests use HTTPS

## Performance

- **Response Time**: Typically 2-5 seconds for search requests
- **Timeout**: 30 seconds for search requests, 10 seconds for status checks
- **Caching**: No caching implemented (real-time results)
- **Concurrent Requests**: Single request per search (no batching)

## Integration with House Crush

The Perplexity integration works alongside the existing local database search:

- **Local Search**: Uses pre-collected data with AI ranking
- **Perplexity Search**: Real-time search with immediate results
- **Hybrid Approach**: Users can choose their preferred method

Both methods provide AI-powered ranking and filtering for optimal results.

## Support

For issues with the Perplexity API integration:

1. Check the troubleshooting section above
2. Run the test script: `python test_perplexity.py`
3. Check the application logs for detailed error messages
4. Verify your API key and internet connection

For Perplexity API-specific issues, refer to the [official documentation](https://docs.perplexity.ai/api-reference/chat-completions-post). 