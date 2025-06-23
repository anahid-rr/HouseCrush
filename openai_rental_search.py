#!/usr/bin/env python3
"""
OpenAI API Integration for Rental Search
This module uses OpenAI API to search for rental listings in real-time.
Uses the official OpenAI API endpoint for chat completions with GPT-4o-mini.
"""

import os
import json
import logging
import requests
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenAIRentalSearch:
    def __init__(self):
        """Initialize OpenAI API client."""
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        } if self.api_key else {}
        
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found in environment variables")
        else:
            logger.info("OpenAI API client initialized successfully")

    def search_rentals(self, location: str, min_price: Optional[int] = None, 
                      max_price: Optional[int] = None, bedrooms: Optional[int] = None,
                      amenities: Optional[List[str]] = None, lifestyle: Optional[str] = None) -> List[Dict]:
        """
        Search for rental listings using OpenAI API with conversational approach.
        
        Args:
            location: City or area to search
            min_price: Minimum price filter
            max_price: Maximum price filter
            bedrooms: Number of bedrooms required
            amenities: List of required amenities
            lifestyle: Lifestyle preferences (e.g., near a park)
            
        Returns:
            List of rental listings with structured data
        """
        if not self.api_key:
            logger.error("OpenAI API key not available")
            return []

        try:
            # Build conversational search query
            query = self._build_conversational_query(location, min_price, max_price, bedrooms, amenities, lifestyle)
            logger.info(f"Searching with conversational query: {query}")

            # Prepare the API request with conversational approach
            payload = {
                "model": "gpt-4o-mini",  # Using GPT-4o-mini for cost-effective and fast search
                "messages": [
                    {
                        "role": "system",
                        "content": """You are an expert rental property search assistant with access to real-time rental listings. Your task is to:

1. SEARCH REAL-TIME: Use your knowledge to search for actual rental listings from major rental websites like:
   - Zillow.com
   - Apartments.com
   - Rent.com
   - PadMapper.com
   - RentFaster.ca (for Canadian listings)
   - Kijiji.ca (for Canadian listings)
   - Craigslist.org
   - Realtor.com

2. MATCH CRITERIA: Find listings that match at least 80% of the user's requirements. Calculate a match percentage based on:
   - Location match (30%)
   - Price range match (25%)
   - Bedroom/bathroom match (20%)
   - Amenities match (15%)
   - Lifestyle preferences match (10%)

3. RETURN TOP 10: Provide exactly the top 10 listings with the highest match percentages (80%+).

4. EXACT INFORMATION: For each listing, provide:
   - Exact listing URL/link
   - Source website name
   - Complete contact information (phone, email, agent name)
   - Accurate pricing
   - Real amenities and features
   - Current availability status

5. JSON FORMAT: Return ONLY valid JSON in this exact structure:
```json
{
  "search_summary": {
    "location": "searched location",
    "total_listings_found": number,
    "top_matches": number,
    "search_criteria": "user criteria summary"
  },
  "listings": [
    {
      "id": "unique_id",
      "title": "Property title",
      "price": monthly_rent_number,
      "location": "exact address/area",
      "bedrooms": number,
      "bathrooms": number,
      "amenities": ["amenity1", "amenity2"],
      "description": "detailed description",
      "match_percentage": 85,
      "contact": {
        "name": "agent/contact name",
        "phone": "phone number",
        "email": "email address"
      },
      "source_website": "website name",
      "listing_url": "exact listing URL",
      "availability_date": "YYYY-MM-DD",
      "features": ["feature1", "feature2"],
      "images": ["image_url1", "image_url2"]
    }
  ]
}
```

IMPORTANT: Only return listings that actually exist with real URLs and contact information. Do not fabricate listings."""
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                "max_tokens": 4000,
                "temperature": 0.1
            }

            # Make API request
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                self._save_response_to_file(result)
                listings = self._parse_conversational_response(result, location)
                logger.info(f"Found {len(listings)} rental listings with conversational search")
                return listings
            else:
                logger.error(f"API request failed with status {response.status_code}: {response.text}")
                return []

        except Exception as e:
            logger.error(f"Error searching rentals: {e}")
            return []

    def _save_response_to_file(self, response_data: Dict):
        """Save the full OpenAI JSON response to a file for debugging."""
        try:
            results_dir = 'results'
            os.makedirs(results_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(results_dir, f'openai_conversational_response_{timestamp}.json')
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(response_data, f, ensure_ascii=False, indent=4)
            
            logger.info(f"Successfully saved OpenAI conversational response to {file_path}")

        except Exception as e:
            logger.error(f"Error saving OpenAI response to file: {e}")

    def _build_conversational_query(self, location: str, min_price: Optional[int] = None,
                                   max_price: Optional[int] = None, bedrooms: Optional[int] = None,
                                   amenities: Optional[List[str]] = None, lifestyle: Optional[str] = None) -> str:
        """Build a conversational search query for rental listings."""
        query_parts = [f"I'm looking for rental properties in {location}"]
        
        # Add price filters
        if min_price and max_price:
            query_parts.append(f"with a budget between ${min_price:,} and ${max_price:,} per month")
        elif min_price:
            query_parts.append(f"with a minimum budget of ${min_price:,} per month")
        elif max_price:
            query_parts.append(f"with a maximum budget of ${max_price:,} per month")
        
        # Add bedroom filter
        if bedrooms:
            if bedrooms == 1:
                query_parts.append(f"I need a {bedrooms}-bedroom apartment")
            else:
                query_parts.append(f"I need a {bedrooms}-bedroom apartment")
        
        # Add amenities filter
        if amenities:
            amenities_text = ', '.join(amenities)
            query_parts.append(f"The property must include these amenities: {amenities_text}")
            
        # Add lifestyle filter
        if lifestyle:
            query_parts.append(f"I'm looking for a place that fits this lifestyle: '{lifestyle}'")
        
        # Add specific search instructions
        query_parts.append("Please search real-time rental listings and find the top 10 properties that match at least 80% of my criteria.")
        query_parts.append("For each listing, provide the exact listing URL, contact information, and calculate the match percentage based on my requirements.")
        query_parts.append("Focus on finding actual available listings with real contact details and accurate pricing.")
        
        return " ".join(query_parts)

    def _parse_conversational_response(self, response: Dict, location: str) -> List[Dict]:
        """Parse OpenAI conversational response into structured rental listings."""
        listings = []
        
        try:
            # Extract the content from the response
            if 'choices' in response and len(response['choices']) > 0:
                content = response['choices'][0]['message']['content']
                
                # Try to extract JSON from the response
                parsed_data = self._extract_json_from_content(content)
                
                if parsed_data and 'listings' in parsed_data:
                    listings = parsed_data['listings']
                    # Save the complete search results
                    self._save_search_results(parsed_data, location)
                else:
                    # Fallback parsing
                    listings = self._extract_listings_from_text(content, location)
                    
            else:
                logger.warning("No choices found in API response")
                
        except Exception as e:
            logger.error(f"Error parsing conversational API response: {e}")
            listings = []

        return listings

    def _extract_json_from_content(self, content: str) -> Optional[Dict]:
        """Extract JSON data from API response content."""
        try:
            import re
            
            # Pattern to find JSON in markdown code blocks
            match = re.search(r'```json\s*([\s\S]*?)\s*```', content)
            if match:
                json_str = match.group(1)
            else:
                # Fallback to find the largest JSON-like string
                start = content.find('{')
                end = content.rfind('}') + 1
                
                if start != -1 and end != 0:
                    json_str = content[start:end]
                else:
                    json_str = None

            if json_str:
                return json.loads(json_str)

        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Error extracting or parsing JSON from content: {e}")

        return None

    def _extract_listings_from_text(self, content: str, location: str) -> List[Dict]:
        """Extract listings from text when JSON parsing fails."""
        listings = []
        try:
            # Create a basic listing from the text content
            listing = {
                'id': 1,
                'title': f'Rental Search Results for {location}',
                'price': 0,
                'location': location,
                'bedrooms': None,
                'bathrooms': None,
                'amenities': [],
                'description': content[:500] + "..." if len(content) > 500 else content,
                'match_percentage': 0,
                'contact': {'name': 'Contact for details', 'phone': 'N/A', 'email': 'N/A'},
                'source_website': 'OpenAI Search',
                'listing_url': None,
                'availability_date': datetime.now().strftime('%Y-%m-%d'),
                'features': [],
                'images': []
            }
            listings.append(listing)
            
        except Exception as e:
            logger.error(f"Error creating fallback listing: {e}")

        return listings

    def _save_search_results(self, search_data: Dict, location: str):
        """Save the complete search results to a JSON file."""
        try:
            results_dir = 'results'
            os.makedirs(results_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(results_dir, f'rental_search_results_{location}_{timestamp}.json')
            
            # Add metadata to the search results
            search_data['metadata'] = {
                'search_timestamp': datetime.now().isoformat(),
                'location': location,
                'total_listings': len(search_data.get('listings', [])),
                'source': 'OpenAI Conversational Search (GPT-4o-mini)'
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(search_data, f, ensure_ascii=False, indent=4)
            
            logger.info(f"Successfully saved search results to {file_path}")

        except Exception as e:
            logger.error(f"Error saving search results to file: {e}")

    def get_api_status(self) -> Dict:
        """Get the status of the OpenAI API connection."""
        if not self.api_key:
            return {
                'available': False,
                'api_key_set': False,
                'status': 'API key not set'
            }
        
        try:
            # Test API connection with a simple request
            test_payload = {
                "model": "gpt-4o-mini",  # Using GPT-4o-mini for testing
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello"
                    }
                ],
                "max_tokens": 10
            }
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=test_payload,
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    'available': True,
                    'api_key_set': True,
                    'status': 'Connected (GPT-4o-mini)'
                }
            else:
                return {
                    'available': False,
                    'api_key_set': True,
                    'status': f'API Error: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'available': False,
                'api_key_set': True,
                'status': f'Connection Error: {str(e)}'
            }

# Global instance
openai_search = OpenAIRentalSearch()

def search_rentals_with_openai(location: str, min_price: Optional[int] = None,
                              max_price: Optional[int] = None, bedrooms: Optional[int] = None,
                              amenities: Optional[List[str]] = None, lifestyle: Optional[str] = None) -> List[Dict]:
    """Convenience function to search rentals using OpenAI API with conversational approach."""
    return openai_search.search_rentals(location, min_price, max_price, bedrooms, amenities, lifestyle)

def get_openai_status() -> Dict:
    """Get OpenAI API status."""
    return openai_search.get_api_status() 