# OpenAI API Integration for House Crush

This document explains how to set up and use the OpenAI API integration for real-time rental property search in House Crush.

## Overview

The OpenAI API integration allows House Crush to search for rental listings in real-time using OpenAI's powerful language models. This provides users with intelligent, AI-powered rental property search capabilities.

## Features

- **AI-Powered Search**: Uses OpenAI's GPT-4o model for intelligent rental search
- **Real-time Results**: Searches for current rental listings across multiple platforms
- **Structured Data Extraction**: Parses and structures rental information from AI responses
- **Fallback Handling**: Provides useful information even when structured data isn't available
- **API Status Monitoring**: Real-time status checking of API connectivity
- **Intelligent Query Building**: Automatically constructs optimized search queries

## Setup Instructions

### 1. Get OpenAI API Key

1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign up for an account if you don't have one
3. Navigate to the API keys section
4. Create a new API key
5. Copy the API key

### 2. Configure Environment

Add your API key to the `.env` file:

```bash
OPENAI_API_KEY=your_api_key_here
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

**Note**: The integration uses direct HTTP requests to the OpenAI API, so no additional SDK is required.

## Usage

### In the Web Application

1. Start the OpenAI version of the application:
   ```bash
   python app_openai.py
   ```

2. Navigate to the web interface
3. Select "OpenAI Search" as your search method
4. Enter your search criteria:
   - Location (required)
   - Price range (optional)
   - Number of bedrooms (optional)
5. Click "Search Properties"
6. View AI-powered results

### Programmatic Usage

```python
from openai_rental_search import search_rentals_with_openai, get_openai_status

# Check API status
status = get_openai_status()
print(f"API Status: {status['status']}")

# Search for rentals
listings = search_rentals_with_openai(
    location="Toronto",
    min_price=1500,
    max_price=2500,
    bedrooms=2
)

for listing in listings:
    print(f"{listing['title']} - ${listing['price']}")
```

## API Endpoint

The integration uses the official OpenAI API endpoint:
- **URL**: `https://api.openai.com/v1/chat/completions`
- **Method**: POST
- **Authentication**: Bearer token
- **Model**: `gpt-4o` (for advanced search capabilities)

For detailed API documentation, visit: [OpenAI API Reference](https://platform.openai.com/docs/api-reference/chat)

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
  "source_website": "OpenAI Search",
  "availability_date": "2024-01-15",
  "collected_date": "2024-01-15T10:30:00",
  "source": "OpenAI API",
  "match_score": 85,
  "match_reason": "Real-time search result from OpenAI API"
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
python test_openai.py
```

This will:
- Check API connectivity
- Test a sample search
- Verify response parsing
- Compare with Perplexity API (if available)
- Show setup instructions if needed

## Troubleshooting

### Common Issues

1. **"API key not set"**
   - Ensure `OPENAI_API_KEY` is in your `.env` file
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

The OpenAI API has rate limits that vary by plan:
- **Free Tier**: Limited requests per minute
- **Paid Plans**: Higher rate limits

The integration respects these limits and will provide appropriate error messages when exceeded.

## Security

- API keys are stored in environment variables (`.env` file)
- Never commit API keys to version control
- The `.env` file is already in `.gitignore`
- All API requests use HTTPS

## Performance

- **Response Time**: Typically 3-8 seconds for search requests
- **Timeout**: 30 seconds for search requests, 10 seconds for status checks
- **Caching**: No caching implemented (real-time results)
- **Concurrent Requests**: Single request per search (no batching)

## Comparison with Perplexity API

| Feature | OpenAI API | Perplexity API |
|---------|------------|----------------|
| **Model** | GPT-4o | Sonar-medium-online |
| **Response Time** | 3-8 seconds | 2-5 seconds |
| **Cost** | Pay-per-token | Free tier available |
| **Search Capabilities** | General knowledge + web search | Specialized web search |
| **JSON Parsing** | Advanced | Good |
| **Fallback Handling** | Comprehensive | Good |

## Integration with House Crush

The OpenAI integration works alongside the existing local database search:

- **Local Search**: Uses pre-collected data with AI ranking
- **OpenAI Search**: Real-time search with AI-powered results
- **Hybrid Approach**: Users can choose their preferred method

Both methods provide AI-powered ranking and filtering for optimal results.

## Support

For issues with the OpenAI API integration:

1. Check the troubleshooting section above
2. Run the test script: `python test_openai.py`
3. Check the application logs for detailed error messages
4. Verify your API key and internet connection

For OpenAI API-specific issues, refer to the [official documentation](https://platform.openai.com/docs/api-reference/chat).

## Cost Considerations

OpenAI API usage is charged per token:
- **Input tokens**: Your search query
- **Output tokens**: AI response
- **Pricing**: Varies by model (GPT-4o is more expensive than GPT-3.5-turbo)

Consider your usage patterns and budget when choosing between OpenAI and Perplexity APIs. 